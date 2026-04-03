from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.models import User, Transaction, Role, TransactionType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_data():
    """
    This runs once when the app starts.
    It adds sample users and transactions so evaluators can test immediately.
    If data already exists, it skips — so it won't duplicate on restart.
    """
    db = SessionLocal()

    # Skip if users already exist
    if db.query(User).first():
        db.close()
        return

    # --- Create Sample Users ---
    users = [
        User(
            name="Admin User",
            email="admin@finance.com",
            hashed_password=pwd_context.hash("admin123"),
            role=Role.ADMIN,
            is_active=True,
        ),
        User(
            name="Analyst User",
            email="analyst@finance.com",
            hashed_password=pwd_context.hash("analyst123"),
            role=Role.ANALYST,
            is_active=True,
        ),
        User(
            name="Viewer User",
            email="viewer@finance.com",
            hashed_password=pwd_context.hash("viewer123"),
            role=Role.VIEWER,
            is_active=True,
        ),
    ]
    db.add_all(users)
    db.commit()
    for u in users:
        db.refresh(u)

    # --- Create Sample Transactions ---
    transactions = [
        Transaction(amount=5000, type=TransactionType.INCOME, category="Salary", date="2024-01-01", notes="January salary", user_id=users[0].id),
        Transaction(amount=200, type=TransactionType.EXPENSE, category="Food", date="2024-01-05", notes="Groceries", user_id=users[0].id),
        Transaction(amount=1500, type=TransactionType.INCOME, category="Freelance", date="2024-01-10", notes="Web project", user_id=users[1].id),
        Transaction(amount=800, type=TransactionType.EXPENSE, category="Rent", date="2024-01-15", notes="Monthly rent", user_id=users[1].id),
        Transaction(amount=300, type=TransactionType.EXPENSE, category="Utilities", date="2024-02-01", notes="Electricity bill", user_id=users[0].id),
        Transaction(amount=2000, type=TransactionType.INCOME, category="Salary", date="2024-02-01", notes="Bonus", user_id=users[2].id),
        Transaction(amount=150, type=TransactionType.EXPENSE, category="Food", date="2024-02-10", notes="Restaurant", user_id=users[2].id),
        Transaction(amount=500, type=TransactionType.INCOME, category="Freelance", date="2024-03-05", notes="Design work", user_id=users[0].id),
    ]
    db.add_all(transactions)
    db.commit()
    db.close()

    print("✅ Seed data loaded successfully.")