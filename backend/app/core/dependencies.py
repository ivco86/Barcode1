from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.core.security import decode_access_token
from app.core.config import settings
from app.models.tenant import Tenant
from app.models.user import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> dict:
    """
    Извлича текущия потребител от JWT token
    Връща dict с tenant_id, user_id и role
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Remove "Bearer " prefix
        token = authorization.replace("Bearer ", "")

        # Decode JWT
        payload = decode_access_token(token)

        tenant_id = payload.get("tenant_id")
        user_id = payload.get("user_id")

        if not tenant_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Verify user exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        return {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "role": payload.get("role"),
            "username": payload.get("username")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_subscription(tenant_id: str, db: Session) -> Tenant:
    """
    Проверява дали tenant-а има активен subscription
    (Локално - винаги активен, Cloud - проверява реално)
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Ако subscription checks са disabled (локално) - винаги OK
    if not settings.SUBSCRIPTION_CHECKS_ENABLED:
        return tenant

    # Cloud - проверявай реално
    if tenant.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription suspended. Please update payment method."
        )

    if tenant.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription cancelled."
        )

    return tenant


def require_role(allowed_roles: list[str]):
    """
    Dependency за проверка на роля
    Usage: Depends(require_role(["owner", "admin"]))
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
