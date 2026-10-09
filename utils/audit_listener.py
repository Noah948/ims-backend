from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from datetime import datetime
from decimal import Decimal
from uuid import UUID

IGNORED_FIELDS = {"updated_at", "created_at"}


def _serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    return value


def _serialize_dict(data):
    if not data:
        return data
    return {k: _serialize_value(v) for k, v in data.items()}


def register_audit_listeners():

    @event.listens_for(Session, "before_flush")
    def collect_changes(session: Session, flush_context, instances):
        if "audit_changes" not in session.info:
            session.info["audit_changes"] = []
        changes = session.info["audit_changes"]

        for instance in session.new:
            if not _is_auditable(instance):
                continue
            changes.append(_build_change_payload(instance, "CREATE"))

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
                    old_val = history.deleted[0] if history.deleted else None
                    new_val = history.added[0] if history.added else None
                    old_values[key] = _serialize_value(old_val)
                    new_values[key] = _serialize_value(new_val)
            if not old_values:
                continue
            if "deleted_at" in new_values and new_values["deleted_at"] is not None:
                operation = "SOFT_DELETE"
            else:
                operation = "UPDATE"
            changes.append(_build_change_payload(instance, operation, old_values, new_values))

        for instance in session.deleted:
            if not _is_auditable(instance):
                continue
            changes.append(_build_change_payload(instance, "DELETE"))

    @event.listens_for(Session, "after_flush_postexec")
    def create_audit_logs(session: Session, flush_context):
        changes = session.info.pop("audit_changes", [])
        if not changes:
            return
        for change in changes:
            audit = AuditLog(**change)
            session.add(audit)


def _is_auditable(instance) -> bool:
    if isinstance(instance, AuditLog):
        return False
    if not hasattr(instance, "id"):
        return False
    business_id = _extract_business_id(instance)
    if not business_id:
        return False
    return True


def _build_change_payload(instance, operation, old_values=None, new_values=None):
    return {
        "business_id": _extract_business_id(instance),
        "user_id": _extract_user_id(instance),
        "entity_type": instance.__class__.__name__.lower(),
        "entity_id": getattr(instance, "id", None),
        "operation": operation,
        "old_values": _serialize_dict(old_values),
        "new_values": _serialize_dict(new_values),
    }


def _extract_business_id(instance):
    if hasattr(instance, "business_id") and instance.business_id:
        return instance.business_id
    if instance.__class__.__name__ == "Business":
        return getattr(instance, "id", None)
    state = inspect(instance)
    for column in state.mapper.columns:
        for fk in column.foreign_keys:
            if "businesses" in fk.target_fullname:
                return getattr(instance, column.key, None)
    return None


def _extract_user_id(instance):
    if hasattr(instance, "user_id") and instance.user_id:
        return instance.user_id
    if instance.__class__.__name__ == "User":
        return getattr(instance, "id", None)
    state = inspect(instance)
    for column in state.mapper.columns:
        for fk in column.foreign_keys:
            if "users" in fk.target_fullname:
                return getattr(instance, column.key, None)
    return None