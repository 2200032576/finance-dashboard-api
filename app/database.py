from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Using SQLite — a simple file-based database, no server needed
# The file "finance.db" will be auto-created in the project folder
DATABASE_URL = "sqlite:///./finance.db"

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required setting for SQLite
)

# Each request gets its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our models will inherit from
Base = declarative_base()


# This function is used as a dependency in routes
# It opens a DB session, gives it to the route, then closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()