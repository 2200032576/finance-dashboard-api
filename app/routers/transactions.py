from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Transaction, TransactionType, User
from app.schemas.schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from app.core.security import get_current_user, require_analyst_or_admin, require_admin

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    request: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)  # Viewer cannot create
):
    """Create a new financial transaction. Analyst and Admin only."""
    new_txn = Transaction(**request.model_dump(), user_id=current_user.id)
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    # Optional filters — user can pass these as query params e.g. ?type=INCOME&category=Salary
    type: Optional[TransactionType] = Query(None, description="Filter by INCOME or EXPENSE"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # All roles can view
):
    """
    List transactions with optional filters and pagination.
    All roles can access this. Soft-deleted records are excluded.
    """
    query = db.query(Transaction).filter(Transaction.is_deleted == False)

    # Apply filters only if provided
    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(Transaction.category.ilike(f"%{category}%"))
    if from_date:
        query = query.filter(Transaction.date >= from_date)
    if to_date:
        query = query.filter(Transaction.date <= to_date)

    # Pagination: skip records before current page
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # All roles can view
):
    """Get a single transaction by ID."""
    txn = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return txn


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    request: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)  # Viewer cannot update
):
    """Update a transaction. Analyst and Admin only."""
    txn = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Only update fields that were actually sent in the request
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(txn, field, value)

    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{transaction_id}", status_code=200)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only admin can delete
):
    """
    Soft delete a transaction (marks it as deleted, doesn't remove from DB).
    Admin only.
    """
    txn = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    txn.is_deleted = True
    db.commit()
    return {"message": f"Transaction {transaction_id} deleted successfully."}