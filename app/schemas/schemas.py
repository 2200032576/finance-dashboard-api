from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.models.models import Role, TransactionType


# --- Auth Schemas ---

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[Role] = Role.VIEWER  # Default role is VIEWER

    @field_validator("password")
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- User Schemas ---

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    is_active: bool

    class Config:
        from_attributes = True  # Allows converting SQLAlchemy model to this schema


class UpdateRoleRequest(BaseModel):
    role: Role


class UpdateStatusRequest(BaseModel):
    is_active: bool


# --- Transaction Schemas ---

class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: str   # Expected format: YYYY-MM-DD
    notes: Optional[str] = None

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @field_validator("date")
    def date_format_check(cls, v):
        # Simple check: must look like YYYY-MM-DD
        parts = v.split("-")
        if len(parts) != 3 or len(parts[0]) != 4:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[str] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    date: str
    notes: Optional[str]
    user_id: int

    class Config:
        from_attributes = True