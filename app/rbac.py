ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_MEMBER = "member"
ROLE_VIEWER = "viewer"

PERMISSION_WRITE = "write"
PERMISSION_MANAGE_USERS = "manage_users"
PERMISSION_RELEASE = "release"

ROLE_PERMISSIONS = {
    ROLE_ADMIN: {PERMISSION_WRITE, PERMISSION_MANAGE_USERS, PERMISSION_RELEASE},
    ROLE_MANAGER: {PERMISSION_WRITE, PERMISSION_RELEASE},
    ROLE_MEMBER: {PERMISSION_WRITE},
    ROLE_VIEWER: set(),
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
