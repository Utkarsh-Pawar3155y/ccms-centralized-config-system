"""
FILE: app/database.py
PURPOSE: Sets up the connection to PostgreSQL using SQLAlchemy.

Think of this file as the "phone line" between your FastAPI app and the database.
It creates:
  - An "engine" (the actual connection)
  - A "SessionLocal" (a factory that creates DB sessions on demand)
  - A "Base" class that all DB models will inherit from
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read the database URL from environment variables
# psycopg3 requires 'postgresql+psycopg://' prefix
# We auto-convert the common 'postgresql://' format so your .env file does not need to change
_raw_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ccms_db")
DATABASE_URL = (
    _raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if _raw_url.startswith("postgresql://") and "+psycopg" not in _raw_url
    else _raw_url
)

# Create the SQLAlchemy engine
# The engine manages the low-level connection pool to PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=True,        # Set to False in production — this logs every SQL query (useful for debugging)
    pool_pre_ping=True  # Checks connection health before using it
)

# SessionLocal is a "session factory"
# Each time you call SessionLocal(), you get a fresh database session
SessionLocal = sessionmaker(
    autocommit=False,  # We manually commit — safer, prevents accidental partial writes
    autoflush=False,   # We manually flush — more control over when data is sent to DB
    bind=engine
)

# Base class for all ORM models
# Every model (table) you create will inherit from this Base
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency function for FastAPI.
    
    This is a "generator" function used with FastAPI's dependency injection system.
    
    How it works:
    1. Creates a new DB session
    2. Yields it to the route handler (your API endpoint)
    3. After the request is done, closes the session (cleanup)
    
    The 'try/finally' ensures the session is ALWAYS closed,
    even if an error occurs during the request.
    
    Usage in routes:
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
