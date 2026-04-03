# Finance Dashboard API

A backend REST API for a finance dashboard system featuring **role-based access control**, **JWT authentication**, and **aggregated analytics** — built with FastAPI and SQLite.

 **Live API:** https://finance-dashboard-api-6kxy.onrender.com  
 **Swagger Docs:** https://finance-dashboard-api-6kxy.onrender.com/docs

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (Python) |
| Database | SQLite via SQLAlchemy ORM |
| Authentication | JWT (JSON Web Tokens) |
| Validation | Pydantic v2 |
| Password Hashing | bcrypt via passlib |
| API Docs | Swagger UI — auto-generated at `/docs` |

---

## Features

- **JWT Authentication** — Register and login to get a token. All protected routes verify it automatically.
- **Role-Based Access Control** — Three roles with clearly enforced permissions at the route level.
- **Financial Records CRUD** — Create, read, update, and soft-delete transactions.
- **Filtering & Pagination** — Filter transactions by type, category, and date range. Paginate results.
- **Dashboard Analytics** — Summary totals, category breakdowns, and monthly trends.
- **Soft Delete** — Transactions are never permanently removed, maintaining an audit trail.
- **Seed Data** — Sample users and transactions loaded automatically on startup.

---

## Roles & Permissions

| Role | Permissions |
|------|------------|
| **VIEWER** | View transactions, view dashboard summary and recent activity |
| **ANALYST** | Everything VIEWER can do + access category breakdowns and monthly trends |
| **ADMIN** | Full access — manage users, create/update/delete transactions |

---

## Project Structure

```
finance-dashboard-api/
├── app/
│   ├── main.py              # App entry point and route registration
│   ├── database.py          # Database connection and session management
│   ├── models/
│   │   └── models.py        # User and Transaction database models
│   ├── schemas/
│   │   └── schemas.py       # Request validation and response schemas
│   ├── routers/
│   │   ├── auth.py          # Register and login endpoints
│   │   ├── users.py         # User management (Admin only)
│   │   ├── transactions.py  # Financial records CRUD with filtering
│   │   └── dashboard.py     # Summary and analytics endpoints
│   └── core/
│       ├── security.py      # JWT logic and reusable role guards
│       └── seed.py          # Startup seed data loader
├── .python-version
├── requirements.txt
└── README.md
```

---

## Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/2200032576/finance-dashboard-api.git
cd finance-dashboard-api
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the server
```bash
uvicorn app.main:app --reload
```

### 5. Open the docs
```
http://localhost:8000/docs
```

> The SQLite database is created automatically on first run. Seed data is loaded on startup — no manual setup needed.

---

## Test Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@finance.com | admin123 | ADMIN |
| analyst@finance.com | analyst123 | ANALYST |
| viewer@finance.com | viewer123 | VIEWER |

---

## API Reference

### Auth
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and receive JWT token | No |

### Users
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/users/me` | Get your own profile | Any |
| GET | `/users/` | List all users | Admin |
| PATCH | `/users/{id}/role` | Update a user's role | Admin |
| PATCH | `/users/{id}/status` | Activate or deactivate a user | Admin |

### Transactions
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| POST | `/transactions/` | Create a transaction | Analyst, Admin |
| GET | `/transactions/` | List transactions with filters | Any |
| GET | `/transactions/{id}` | Get a single transaction | Any |
| PUT | `/transactions/{id}` | Update a transaction | Analyst, Admin |
| DELETE | `/transactions/{id}` | Soft delete a transaction | Admin |

**Available filters for `GET /transactions/`**
```
?type=INCOME
?type=EXPENSE
?category=Salary
?from_date=2024-01-01
?to_date=2024-03-31
?page=1&limit=10
```

### Dashboard
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/dashboard/summary` | Total income, expenses, net balance | Any |
| GET | `/dashboard/by-category` | Totals grouped by category and type | Analyst, Admin |
| GET | `/dashboard/trends` | Monthly income and expense trends | Analyst, Admin |
| GET | `/dashboard/recent` | Most recent transactions | Any |

---

## Design Decisions

**Soft Delete**  
Transactions are marked as deleted via an `is_deleted` flag rather than being removed from the database. This preserves the audit trail, which is important in any financial system.

**Role Guards as Reusable Dependencies**  
Access control is implemented as FastAPI dependency functions (`require_admin`, `require_analyst_or_admin`) that are injected directly into route definitions. This keeps routes clean and makes permissions easy to change in one place.

**JWT Authentication**  
Stateless token-based auth. The token encodes the user's ID and role, and is verified on every protected request without hitting the database for a session lookup.

**Pagination**  
The transaction list endpoint supports `page` and `limit` query parameters to prevent large data dumps and simulate real-world API behaviour.

---

## Assumptions

1. Roles are assigned at registration and can be updated later by an Admin.
2. All roles can view all transactions — simulating a shared finance dashboard.
3. Dates are stored as `YYYY-MM-DD` strings for simplicity.
4. Soft-deleted transactions are excluded from all queries and dashboard calculations.
5. The JWT secret key is hardcoded for this assignment. In production it would be stored as an environment variable.
