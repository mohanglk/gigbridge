"""Role assignment rules that do not depend on any client platform."""

from app.modules.auth.models import PlatformRole, User, UserPlatformRole

PUBLIC_REGISTRATION_ROLE_KEY = "member"

def grant_registration_role(user: User, role: PlatformRole) -> None:
    """Grant only the fixed base role; privileged grants need trusted admin flow."""
    if (
        role.key.casefold() != PUBLIC_REGISTRATION_ROLE_KEY
        or not role.is_registration_assignable
    ):
        raise ValueError("This role cannot be granted during public registration.")

    user.role_grants.append(UserPlatformRole(role=role))
