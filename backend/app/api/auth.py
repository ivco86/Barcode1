from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import verify_password, create_access_token
from app.api.schemas import LoginRequest, LoginResponse
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint
    Приема username/email и password
    Връща JWT token
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create JWT token
    token_data = {
        "tenant_id": str(user.tenant_id),
        "user_id": str(user.id),
        "username": user.username,
        "role": user.role
    }
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "plan": tenant.plan,
            "status": tenant.status
        },
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }
