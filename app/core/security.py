from typing import List, Callable, Optional
from fastapi import Request, HTTPException, status

def _extract_role(claims: dict) -> Optional[str]:
    if not isinstance(claims, dict):
        return None
    role = claims.get("role")
    if role:
        return str(role).lower()
    roles = claims.get("roles")
    if isinstance(roles, list) and roles:
        return str(roles[0]).lower()
    return None

def require_roles(allowed: List[str]) -> Callable:
    allowed_l = [r.lower() for r in allowed]

    def _dep(request: Request):
        claims = getattr(request.state, "claims", None)
        if not claims:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")

        role = _extract_role(claims)
        if role is None:
            # no role in token ? forbidden
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

        # allow direct match
        if role in allowed_l:
            return True

        # treat "owner" as superset admin
        if role == "owner":
            return True

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    return _dep
