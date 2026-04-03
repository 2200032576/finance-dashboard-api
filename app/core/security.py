from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User

# --- Config ---

SECRET_KEY = "finance-secret-key-change-in-production"  # In real apps, store this in .env
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# HTTPBearer shows a clean "Enter token" box in Swagger UI
bearer_scheme = HTTPBearer()


# --- Token Creation ---

def create_access_token(data: dict) -> str:
    """Create a JWT token that expires in 24 hours."""
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# --- Get Current Logged-In User ---

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    This runs on every protected route.
    It reads the token, finds the user, and returns them.
    If the token is invalid or expired, it returns a 401 error.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Extract the actual token string from the Bearer credentials
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or deactivated.")
    return user


# --- Role-Based Access Guards ---
# These are reusable functions you attach to any route to restrict access by role

def require_analyst_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Only ANALYST and ADMIN can access this route."""
    if current_user.role not in ["ANALYST", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Access denied. Analyst or Admin role required.")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Only ADMIN can access this route."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
    return current_user