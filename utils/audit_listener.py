from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from models.audit_log import AuditLog

# Fields that should NOT trigger audit updates
IGNORED_FIELDS = {"updated_at", "created_at"}

# =====================================================
# REGISTER LISTENERS
# =====================================================

def register_audit_listeners():

    @event.listens_for(Session, "before_flush")
    def collect_changes(session: Session, flush_context, instances):

        if "audit_changes" not in session.info:
            session.info["audit_changes"] = []

        changes = session.info["audit_changes"]

        # -------------------------
        # CREATE
        # -------------------------
        for instance in session.new:
            if not _is_auditable(instance):
                continue

            changes.append(
                _build_change_payload(instance, "CREATE")
            )

        # -------------------------
        # UPDATE
        # -------------------------
        for instance in session.dirty:

            if not _is_auditable(instance):
                continue

            state = inspect(instance)

            old_values = {}
            new_values = {}

            for attr in state.mapper.column_attrs:
                key = attr.key

                if key in IGNORED_FIELDS:
                    continue

                history = state.attrs[key].history

                if history.has_changes():
                    old_values[key] = history.deleted[0] if history.deleted else None
                    new_values[key] = history.added[0] if history.added else None

            if not old_values:
                continue

            # Detect SOFT_DELETE
            if "deleted_at" in new_values and new_values["deleted_at"] is not None:
                operation = "SOFT_DELETE"
            else:
                operation = "UPDATE"

            changes.append(
                _build_change_payload(
                    instance,
                    operation,
                    old_values,
                    new_values
                )
            )

        # -------------------------
        # DELETE
        # -------------------------
        for instance in session.deleted:
            if not _is_auditable(instance):
                continue

            changes.append(
                _build_change_payload(instance, "DELETE")
            )

    # -----------------------------------------------------
    # SAFELY CREATE AUDIT LOGS AFTER FLUSH
    # -----------------------------------------------------

    @event.listens_for(Session, "after_flush_postexec")
    def create_audit_logs(session: Session, flush_context):

        changes = session.info.pop("audit_changes", [])

        if not changes:
            return

        for change in changes:
            audit = AuditLog(**change)
            session.add(audit)


# =====================================================
# HELPERS
# =====================================================

def _is_auditable(instance) -> bool:

    # Never audit AuditLog itself
    if isinstance(instance, AuditLog):
        return False

    if not hasattr(instance, "id"):
        return False

    user_id = _extract_user_id(instance)
    if not user_id:
        return False

    return True


def _build_change_payload(instance, operation, old_values=None, new_values=None):

    return {
        "user_id": _extract_user_id(instance),
        "entity_type": instance.__class__.__name__.lower(),
        "entity_id": getattr(instance, "id", None),
        "operation": operation,
        "old_values": old_values,
        "new_values": new_values,
    }


def _extract_user_id(instance):

    state = inspect(instance)

    # 1️⃣ Direct user_id field
    if hasattr(instance, "user_id") and instance.user_id:
        return instance.user_id

    # 2️⃣ If instance is User
    if instance.__class__.__name__ == "User":
        return getattr(instance, "id", None)

    # 3️⃣ Search for FK pointing to users table
    for column in state.mapper.columns:
        for fk in column.foreign_keys:
            if "users" in fk.target_fullname:
                return getattr(instance, column.key, None)

    return None