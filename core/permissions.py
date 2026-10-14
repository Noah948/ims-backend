from enum import Enum

from models.enums import MemberRole


class Permission(str, Enum):
    VIEW_DASHBOARD = "view_dashboard"

    MANAGE_SUBSCRIPTION = "manage_subscription"
    VIEW_BILLING = "view_billing"
    UPDATE_BUSINESS_SETTINGS = "update_business_settings"

    VIEW_TEAM_MEMBERS = "view_team_members"
    INVITE_TEAM_MEMBERS = "invite_team_members"
    REMOVE_TEAM_MEMBERS = "remove_team_members"
    CHANGE_USER_ROLES = "change_user_roles"

    CREATE_CATEGORIES = "create_categories"
    EDIT_CATEGORIES = "edit_categories"
    DELETE_CATEGORIES = "delete_categories"

    CREATE_PRODUCTS = "create_products"
    EDIT_PRODUCTS = "edit_products"
    DELETE_PRODUCTS = "delete_products"

    RECORD_SALES = "record_sales"
    EDIT_SALES = "edit_sales"
    DELETE_SALES = "delete_sales"

    MANAGE_EXPENSES = "manage_expenses"

    VIEW_REPORTS = "view_reports"
    # Operators see reports in limited form; this unlocks the full version.
    VIEW_FULL_REPORTS = "view_full_reports"
    EXPORT_REPORTS = "export_reports"

    VIEW_AUDIT_LOGS = "view_audit_logs"
    RESTORE_DELETED_ITEMS = "restore_deleted_items"
    PERMANENTLY_DELETE_DATA = "permanently_delete_data"


# Single source of truth for role-based access. To change who can do what,
# edit this map; routes only declare which Permission they need.
ROLE_PERMISSIONS: dict[MemberRole, frozenset[Permission]] = {
    MemberRole.OWNER: frozenset(Permission),
    MemberRole.OPERATOR: frozenset({
        Permission.VIEW_DASHBOARD,
        Permission.CREATE_PRODUCTS,
        Permission.EDIT_PRODUCTS,
        Permission.RECORD_SALES,
        Permission.VIEW_REPORTS,
    }),
}


def has_permission(role: MemberRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())
