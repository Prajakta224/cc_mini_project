"""Authentication router — register, login, logout, me."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse, MessageResponse
from app.services.auth_service import hash_password, verify_password, create_access_token, needs_rehash
from app.services.audit_service import log_event
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _get_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    # Check duplicate email
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        log_event(db, "REGISTER", False, details={"reason": "duplicate_email"}, ip_address=_get_ip(request))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role="user",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_event(db, "REGISTER", True, user_id=user.id, ip_address=_get_ip(request),
              details={"email": body.email, "name": body.name})
    return user


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    ip = _get_ip(request)

    if not user or not verify_password(body.password, user.password_hash):
        log_event(db, "LOGIN_FAILURE", False,
                  user_id=user.id if user else None,
                  ip_address=ip, details={"email": body.email})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    # Rehash if parameters upgraded
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(body.password)

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(str(user.id), user.role)
    log_event(db, "LOGIN_SUCCESS", True, user_id=user.id, ip_address=ip, details={"email": body.email})
    from app.config import settings
    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log_event(db, "LOGOUT", True, user_id=current_user.id, ip_address=_get_ip(request))
    # JWT is stateless; client must discard the token.
    # For production: implement a token blacklist or short-lived tokens with refresh.
    return MessageResponse(message="Logged out successfully. Please discard your access token.")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
