import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# --- Enums (fixed set of allowed values) ---

class Role(str, enum.Enum):
    VIEWER = "VIEWER"      # Can only view data
    ANALYST = "ANALYST"    # Can view + access insights
    ADMIN = "ADMIN"        # Full access


class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


# --- User Table ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(Role), default=Role.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)  # Admin can deactivate users
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One user can have many transactions
    transactions = relationship("Transaction", back_populates="owner")


# --- Transaction Table ---

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)   # INCOME or EXPENSE
    category = Column(String(100), nullable=False)         # e.g. "Salary", "Food"
    date = Column(String(20), nullable=False)              # Format: YYYY-MM-DD
    notes = Column(Text, nullable=True)                    # Optional description
    is_deleted = Column(Boolean, default=False)            # Soft delete flag

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Each transaction belongs to one user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="transactions")