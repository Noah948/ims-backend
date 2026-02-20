from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from models.audit_log import AuditLog


def register_audit_listeners():

    @event.listens_for(Session, "before_flush")
    def collect_changes(session, flush_context, instances):

        if not hasattr(session, "_audit_changes"):
            session._audit_changes = {
                "create": [],
                "update": [],
                "delete": []
            }

        changes = session._audit_changes

        # CREATE
        for instance in session.new:
            if _is_auditable(instance):
                changes["create"].append(instance)

        # UPDATE
        for instance in session.dirty:
            if not _is_auditable(instance):
                continue

            state = inspect(instance)

            if any(
                state.attrs[attr.key].history.has_changes()
                for attr in state.mapper.column_attrs
            ):
                changes["update"].append(instance)

        # DELETE
        for instance in session.deleted:
            if _is_auditable(instance):
                changes["delete"].append(instance)

    @event.listens_for(Session, "after_flush")
    def create_audit_logs(session, flush_context):

        if not hasattr(session, "_audit_changes"):
            return

        changes = session._audit_changes

        for operation in ["create", "update", "delete"]:
            for instance in changes[operation]:
                _create_log(session, instance, operation.upper())

        # Clear immediately after flush
        session._audit_changes = {
            "create": [],
            "update": [],
            "delete": []
        }


# =====================================================
# HELPERS
# =====================================================

def _is_auditable(instance):

    # Never audit audit log
    if isinstance(instance, AuditLog):
        return False

    if not hasattr(instance, "id"):
        return False

    user_id = _extract_user_id(instance)
    if not user_id:
        return False

    return True


def _create_log(session, instance, operation):

    user_id = _extract_user_id(instance)
    if not user_id:
        return

    audit = AuditLog(
        user_id=user_id,
        entity_type=instance.__class__.__name__.lower(),
        entity_id=getattr(instance, "id", None),
        operation=operation
    )

    session.add(audit)


def _extract_user_id(instance):
    """
    Reliable user_id extraction without recursion.
    """

    # 1️⃣ Direct FK
    if hasattr(instance, "user_id") and instance.user_id:
        return instance.user_id

    # 2️⃣ If instance itself is User
    if instance.__class__.__name__ == "User":
        return getattr(instance, "id", None)

    # 3️⃣ Check foreign keys pointing to user table
    mapper = inspect(instance.__class__)

    for column in mapper.columns:
        for fk in column.foreign_keys:
            if "users" in fk.target_fullname:
                return getattr(instance, column.key, None)

    return None
