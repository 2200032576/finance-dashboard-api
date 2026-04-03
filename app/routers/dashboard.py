from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models.models import Transaction, TransactionType, User
from app.core.security import get_current_user, require_analyst_or_admin

router = APIRouter()


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # All roles can view summary
):
    """
    Returns overall financial summary:
    total income, total expenses, and net balance.
    """
    active = db.query(Transaction).filter(Transaction.is_deleted == False)

    total_income = active.filter(Transaction.type == TransactionType.INCOME)\
        .with_entities(func.sum(Transaction.amount)).scalar() or 0

    total_expense = active.filter(Transaction.type == TransactionType.EXPENSE)\
        .with_entities(func.sum(Transaction.amount)).scalar() or 0

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expense, 2),
        "net_balance": round(total_income - total_expense, 2),
    }


@router.get("/by-category")
def get_by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)  # Viewer cannot access this
):
    """
    Returns total amounts grouped by category.
    Useful for seeing which categories spend or earn the most.
    Analyst and Admin only.
    """
    results = db.query(
        Transaction.category,
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.is_deleted == False
    ).group_by(Transaction.category, Transaction.type).all()

    # Format into a clean list
    return [
        {"category": r.category, "type": r.type, "total": round(r.total, 2)}
        for r in results
    ]


@router.get("/trends")
def get_monthly_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)  # Analyst and Admin only
):
    """
    Returns income and expense totals grouped by month (YYYY-MM).
    Useful for spotting trends over time.
    """
    results = db.query(
        func.substr(Transaction.date, 1, 7).label("month"),  # Extract YYYY-MM from date
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.is_deleted == False
    ).group_by("month", Transaction.type).order_by("month").all()

    return [
        {"month": r.month, "type": r.type, "total": round(r.total, 2)}
        for r in results
    ]


@router.get("/recent")
def get_recent_transactions(
    limit: int = Query(5, ge=1, le=20, description="Number of recent transactions to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # All roles can view recent activity
):
    """Returns the most recent transactions. All roles can access."""
    recent = db.query(Transaction)\
        .filter(Transaction.is_deleted == False)\
        .order_by(Transaction.created_at.desc())\
        .limit(limit).all()

    return [
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type,
            "category": t.category,
            "date": t.date,
        }
        for t in recent
    ]