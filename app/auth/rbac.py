from fastapi import HTTPException, status
from typing import Mapping

# Simple hierarchy: analyst < owner < admin
ROLE_ORDER = ("analyst", "owner", "admin")
RANK = {r: i for i, r in enumerate(ROLE_ORDER)}

def has_role(claims: Mapping, minimum_role: str) -> bool:
    """Return True if the token's role is >= the minimum required role."""
    role = str(claims.get("role", "")).lower()
    return RANK.get(role, -1) >= RANK.get(minimum_role.lower(), 99)

def ensure_role(claims: Mapping, minimum_role: str) -> None:
    """Raise 403 if the token's role is insufficient."""
    if not has_role(claims, minimum_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"insufficient role: need '{minimum_role}', have '{claims.get('role')}'",
        )
