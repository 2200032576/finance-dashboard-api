from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, users, transactions, dashboard
from app.core.seed import seed_data

# Create all database tables automatically based on our models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Dashboard API",
    description="""
## Finance Dashboard Backend

A role-based financial records management system.

### Roles
| Role | Permissions |
|------|------------|
| **VIEWER** | View transactions, view summary |
| **ANALYST** | View transactions, view all dashboard insights |
| **ADMIN** | Full access — manage users, create/update/delete transactions |

### How to use
1. Login with one of the seeded accounts below
2. Copy the token from the response
3. Click **Authorize** (top right) and paste: `Bearer <your_token>`
4. Now all protected routes will work

### Seeded Test Accounts
| Email | Password | Role |
|-------|----------|------|
| admin@finance.com | admin123 | ADMIN |
| analyst@finance.com | analyst123 | ANALYST |
| viewer@finance.com | viewer123 | VIEWER |
    """,
    version="1.0.0",
)

# Allow requests from any frontend (useful for local testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route groups
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])


@app.on_event("startup")
def on_startup():
    """Runs once when the server starts — loads seed data."""
    seed_data()


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "running",
        "message": "Finance Dashboard API is live",
        "docs": "/docs"
    }