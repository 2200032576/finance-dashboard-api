from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import create_access_token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    Returns a JWT token on success so the user can start using the API immediately.
    """
    # Check if email is already taken
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Hash the password before saving — never store plain text passwords
    new_user = User(
        name=request.name,
        email=request.email,
        hashed_password=pwd_context.hash(request.password),
        role=request.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create and return a token
    token = create_access_token({"user_id": new_user.id, "role": new_user.role})
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    Returns a JWT token to use for all protected routes.
    """
    # Find the user by email
    user = db.query(User).filter(User.email == request.email).first()

    # Check if user exists and password is correct
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been deactivated.")

    token = create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": token}