"""
FILE: app/crud.py
PURPOSE: All database operations (Create, Read, Update, Delete).

"CRUD" = Create, Read, Update, Delete — the 4 basic operations on any database.

This layer is intentionally separated from the routes.
Think of it as the "database access layer" or "repository pattern".

Why separate? Clean architecture:
  - Routes: Handle HTTP (what URL, what status code)
  - CRUD:   Handle database (pure data access logic)
  - This makes code easier to test, maintain, and reuse
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Config
from app.schemas import ConfigCreate, ConfigUpdate


# ─────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────

def create_config(db: Session, config_data: ConfigCreate) -> Config:
    """
    Creates a new configuration record in the database.
    
    Steps:
    1. Check if a config with same service+env+key already exists
    2. If it does, raise an error (no duplicates allowed)
    3. If not, create a new Config row and save it
    
    Args:
        db: The database session (connection)
        config_data: Validated data from the POST request
    
    Returns:
        The newly created Config object (with auto-generated id, timestamps)
    
    Raises:
        ValueError: If a config with the same service+env+key already exists
    """
    # Check for duplicate: same service + environment + key combination
    existing = db.query(Config).filter(
        Config.service_name == config_data.service_name,
        Config.environment == config_data.environment,
        Config.config_key == config_data.key
    ).first()

    if existing:
        raise ValueError(
            f"Config already exists: service='{config_data.service_name}', "
            f"environment='{config_data.environment}', key='{config_data.key}'. "
            f"Use PUT /configs/{existing.id} to update it."
        )

    # Create the SQLAlchemy model instance (this does NOT hit the DB yet)
    new_config = Config(
        service_name=config_data.service_name,
        environment=config_data.environment,
        config_key=config_data.key,      # Map 'key' → 'config_key'
        config_value=config_data.value,  # Map 'value' → 'config_value'
        version=1                         # Always starts at version 1
    )

    db.add(new_config)   # Stage the new record (queued for insert)
    db.commit()          # Actually write to the database
    db.refresh(new_config)  # Reload the object to get DB-generated values (id, timestamps)

    return new_config


# ─────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────

def get_config_by_id(db: Session, config_id: int) -> Config | None:
    """
    Fetches a single configuration by its ID.
    
    Returns None if not found (caller decides what to do with None).
    """
    return db.query(Config).filter(Config.id == config_id).first()


def get_configs_for_service(
    db: Session,
    service_name: str,
    environment: str
) -> list[Config]:
    """
    Fetches ALL configurations for a given service + environment combination.
    
    This is the main "read" endpoint — services call this to get their configs.
    
    Example:
        get_configs_for_service(db, "payment-service", "prod")
        → Returns all prod configs for payment-service:
          [DB_HOST, DB_PORT, CACHE_SIZE, TIMEOUT, ...]
    
    Returns the latest version of each config, sorted by key alphabetically.
    """
    return (
        db.query(Config)
        .filter(
            Config.service_name == service_name,
            Config.environment == environment
        )
        .order_by(Config.config_key)  # Alphabetical order for readability
        .all()
    )


def get_config_version_history(
    db: Session,
    service_name: str,
    environment: str,
    config_key: str
) -> list[Config]:
    """
    Returns ALL versions of a specific config key for a service+environment.
    
    Wait — if we update a config in-place, how do we have history?
    Answer: We DON'T update in-place. When a config is updated (see update_config),
    we CREATE a new row with version+1 and keep the old row.
    This is called "append-only" or "event sourcing" pattern.
    
    Example:
        History of DB_HOST for payment-service/prod:
        v1 → "payment-db-old.internal" (created Jan 1)
        v2 → "payment-db.internal"     (updated Jan 15)  ← current (latest version)
    
    Returns versions ordered newest first (latest version at the top).
    """
    return (
        db.query(Config)
        .filter(
            Config.service_name == service_name,
            Config.environment == environment,
            Config.config_key == config_key.upper()
        )
        .order_by(desc(Config.version))  # Newest version first
        .all()
    )


# ─────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────

def update_config(
    db: Session,
    config_id: int,
    update_data: ConfigUpdate
) -> Config | None:
    """
    Updates a configuration by creating a NEW versioned row.
    
    IMPORTANT: We DON'T overwrite the existing row.
    Instead, we:
    1. Find the current (latest) config row
    2. Create a BRAND NEW row with:
       - Same service_name, environment, config_key
       - Updated value/environment (whatever changed)
       - version = old_version + 1
       - Fresh timestamps
    
    This preserves complete history — you can always see what a config
    was set to at any point in time!
    
    Args:
        db: The database session
        config_id: ID of the config to update
        update_data: Fields to update (only provided fields are changed)
    
    Returns:
        The newly created Config row (new version), or None if config_id not found
    """
    # Find the existing config
    existing_config = db.query(Config).filter(Config.id == config_id).first()

    if not existing_config:
        return None  # Caller will return a 404

    # Determine the new values (use existing value if not provided)
    new_value = update_data.value if update_data.value is not None else existing_config.config_value
    new_environment = update_data.environment if update_data.environment is not None else existing_config.environment

    # Create a new row with incremented version (preserve history!)
    new_version_config = Config(
        service_name=existing_config.service_name,
        environment=new_environment,
        config_key=existing_config.config_key,
        config_value=new_value,
        version=existing_config.version + 1,  # Increment version
        # created_at and updated_at will be set automatically by the model defaults
    )

    db.add(new_version_config)
    db.commit()
    db.refresh(new_version_config)

    return new_version_config


# ─────────────────────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────────────────────

def delete_config(db: Session, config_id: int) -> bool:
    """
    Permanently deletes a configuration by ID.
    
    Note: This deletes the specific row. If there are multiple versions
    of the same config key, only this specific version is deleted.
    
    Returns:
        True if deleted successfully
        False if the config_id was not found
    """
    config = db.query(Config).filter(Config.id == config_id).first()

    if not config:
        return False  # Not found

    db.delete(config)
    db.commit()

    return True  # Successfully deleted


# ─────────────────────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────────────────────

def get_all_services(db: Session) -> list[dict]:
    """
    Returns a list of all unique service_name + environment combinations.
    Useful for the health check / overview endpoint.
    """
    results = (
        db.query(Config.service_name, Config.environment)
        .distinct()
        .order_by(Config.service_name, Config.environment)
        .all()
    )

    return [
        {"service_name": row.service_name, "environment": row.environment}
        for row in results
    ]
