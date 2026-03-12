"""
FILE: app/models.py
PURPOSE: Defines the database table structure using SQLAlchemy ORM.

"ORM" stands for Object-Relational Mapper.
Instead of writing raw SQL like:
    CREATE TABLE configs (id SERIAL PRIMARY KEY, ...);

You define Python classes, and SQLAlchemy automatically translates them
into database tables. Much cleaner and safer!

This file creates the 'configs' table in PostgreSQL.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class Config(Base):
    """
    Represents a single configuration entry stored in the database.
    
    Maps to the 'configs' table in PostgreSQL.
    Each instance of this class = one row in the table.
    
    Example row:
        id:            1
        service_name:  "payment-service"
        environment:   "prod"
        config_key:    "DB_HOST"
        config_value:  "payment-db.internal"
        version:       1
        created_at:    2024-01-15 10:30:00
        updated_at:    2024-01-15 10:30:00
    """

    # __tablename__ tells SQLAlchemy what to name the table in PostgreSQL
    __tablename__ = "configs"

    # --- COLUMNS ---

    # Primary key: unique ID for each config row (auto-increments: 1, 2, 3, ...)
    id = Column(Integer, primary_key=True, index=True)

    # The name of the service this config belongs to
    # e.g., "payment-service", "order-service", "notification-service"
    # index=True makes searching by this column fast
    service_name = Column(String(100), nullable=False, index=True)

    # Which environment this config is for
    # e.g., "dev", "staging", "prod"
    environment = Column(String(50), nullable=False, index=True)

    # The configuration key (like a variable name)
    # e.g., "DB_HOST", "CACHE_SIZE", "TIMEOUT", "FEATURE_FLAG"
    config_key = Column(String(200), nullable=False)

    # The configuration value (like a variable's value)
    # Using Text (not String) to support very long values
    # e.g., "payment-db.internal", "512", "30", "true"
    config_value = Column(Text, nullable=False)

    # Version number — starts at 1, increments on every update
    # This enables version history: you can track what changed and when
    version = Column(Integer, nullable=False, default=1)

    # Timestamp: when was this config first created?
    # timezone.utc ensures we store in UTC (good practice for multi-region systems)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Timestamp: when was this config last updated?
    # Also updates automatically whenever the row is modified
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        """Human-readable representation — useful for debugging in the terminal"""
        return (
            f"<Config(id={self.id}, "
            f"service='{self.service_name}', "
            f"env='{self.environment}', "
            f"key='{self.config_key}', "
            f"v{self.version})>"
        )
