from fastapi import APIRouter, Request, HTTPException, status
from app.auth.rbac import ensure_role

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/me")
async def get_me(request: Request):
    # Must have decoded claims from tenancy middleware
    claims = getattr(request.state, "claims", None)
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")
    
    return {
        "user": claims.get("sub"),
        "tenant": claims.get("tid"), 
        "role": claims.get("role")
    }

# Admin router (separate prefix)
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/health")
async def admin_health(request: Request):
    # Must have decoded claims from tenancy middleware
    claims = getattr(request.state, "claims", None)
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")

    # Enforce role >= owner; convert any unexpected error into a clean 403
    try:
        ensure_role(claims, "owner")
    except HTTPException as e:
        # Expected 403 from RBAC
        if e.status_code == status.HTTP_403_FORBIDDEN:
            raise
        # Any other HTTP error -> bubble
        raise
    except Exception as e:
        # Unexpected error -> 403 with context (dev only)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"role check failed: {e}")

    return {"ok": True, "msg": f"admin health for tenant={getattr(request.state, 'tenant', None)}", "role": claims.get("role")}
