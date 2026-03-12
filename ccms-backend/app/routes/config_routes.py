"""
FILE: app/routes/config_routes.py
PURPOSE: Defines all API endpoints (routes) for the CCMS.

This is the "front door" of your API.
Each function here corresponds to one HTTP endpoint.

FastAPI uses "decorators" like @router.post("/configs") to say:
  "When someone sends a POST request to /configs, call this function"

The actual work is delegated to the service layer — routes are thin.
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status

from app.database import get_db
from app.schemas import (
    ConfigCreate,
    ConfigUpdate,
    ConfigResponse,
    ConfigListResponse,
    MessageResponse
)
from app.services import config_service

# APIRouter groups related endpoints together
# prefix="/configs" means all routes here start with /configs
# tags=["Configurations"] groups them in Swagger UI
router = APIRouter(
    prefix="/configs",
    tags=["Configurations"]
)


@router.get(
    "/",
    summary="Get all configurations",
    description="Returns all configuration entries in the system"
)
def get_all_configs(db: Session = Depends(get_db)):
    from app.models import Config

    configs = db.query(Config).all()

    return [
        ConfigResponse.from_orm_model(c)
        for c in configs
    ]


# ═══════════════════════════════════════════════════════════════
# POST /configs
# Create a new configuration
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/",
    response_model=ConfigResponse,
    status_code=status.HTTP_201_CREATED,  # 201 = Created (more specific than 200 OK)
    summary="Create a new configuration",
    description="""
    Creates a new configuration entry for a service.
    
    - **service_name**: The name of your service (e.g., payment-service)
    - **environment**: One of: `dev`, `staging`, `prod`
    - **key**: Configuration key name (auto-uppercased, e.g., DB_HOST)
    - **value**: Configuration value (e.g., payment-db.internal)
    
    Returns 409 Conflict if a config with the same service+environment+key already exists.
    Use PUT to update an existing config.
    """
)
def create_config(
    config_data: ConfigCreate,            # FastAPI reads + validates the request body
    db: Session = Depends(get_db)         # FastAPI injects the DB session automatically
):
    """
    POST /configs
    
    Creates a new configuration. Fails if service+env+key already exists.
    """
    return config_service.create_config_service(db, config_data)


# ═══════════════════════════════════════════════════════════════
# GET /configs/{service_name}/{environment}
# Fetch all configs for a service + environment
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/{service_name}/{environment}",
    response_model=ConfigListResponse,
    summary="Get all configurations for a service and environment",
    description="""
    Fetches all the latest configurations for a specific service and environment.
    
    This is the endpoint your microservices call on startup to load their config!
    
    - Returns only the **latest version** of each configuration key
    - Returns 404 if no configs found for this service+environment
    
    **Example**: `GET /configs/payment-service/prod`
    """
)
def get_configs_for_service(
    service_name: str,     # Taken from the URL path (e.g., "payment-service")
    environment: str,      # Taken from the URL path (e.g., "prod")
    db: Session = Depends(get_db)
):
    """
    GET /configs/{service_name}/{environment}
    
    Returns all latest configs for the service+environment combo.
    """
    return config_service.get_configs_service(db, service_name, environment)


# ═══════════════════════════════════════════════════════════════
# PUT /configs/{config_id}
# Update an existing configuration (creates new version)
# ═══════════════════════════════════════════════════════════════

@router.put(
    "/{config_id}",
    response_model=ConfigResponse,
    summary="Update a configuration (creates a new version)",
    description="""
    Updates an existing configuration by creating a new versioned record.
    
    **Important**: This does NOT overwrite the old value — it creates a new row
    with an incremented version number. Old versions are preserved for history.
    
    You can update:
    - **value**: The new configuration value
    - **environment**: Move this config to a different environment
    
    At least one field must be provided.
    """
)
def update_config(
    config_id: int,                # Taken from the URL path
    update_data: ConfigUpdate,     # Request body (only fields being updated)
    db: Session = Depends(get_db)
):
    """
    PUT /configs/{config_id}
    
    Creates a new version of the config with updated fields.
    """
    return config_service.update_config_service(db, config_id, update_data)


# ═══════════════════════════════════════════════════════════════
# DELETE /configs/{config_id}
# Delete a specific configuration record
# ═══════════════════════════════════════════════════════════════

@router.delete(
    "/{config_id}",
    response_model=MessageResponse,
    summary="Delete a configuration",
    description="""
    Permanently deletes a specific configuration record by its ID.
    
    **Note**: This deletes the specific version row. Other versions of the 
    same config key (if they exist) are not affected.
    
    Returns 404 if the config_id doesn't exist.
    """
)
def delete_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """
    DELETE /configs/{config_id}
    
    Permanently removes a config record.
    """
    return config_service.delete_config_service(db, config_id)


# ═══════════════════════════════════════════════════════════════
# GET /configs/{service_name}/{environment}/history/{key}
# Get version history for a specific config key
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/{service_name}/{environment}/history/{config_key}",
    summary="Get version history for a config key",
    description="""
    Returns all historical versions of a specific config key for a service+environment.
    
    Versions are ordered newest first (latest version at the top).
    
    **Example**: `GET /configs/payment-service/prod/history/DB_HOST`
    
    Returns all versions of DB_HOST for payment-service in prod:
    - v2: "payment-db.internal" (current)
    - v1: "payment-db-old.internal" (previous)
    """
)
def get_version_history(
    service_name: str,
    environment: str,
    config_key: str,
    db: Session = Depends(get_db)
):
    """
    GET /configs/{service_name}/{environment}/history/{config_key}
    
    Returns full version history for a specific config key.
    """
    return config_service.get_version_history_service(
        db, service_name, environment, config_key
    )



@router.get(
    "/history",
    summary="Get global configuration history",
    description="Returns version history of all configuration changes"
)
def get_all_config_history(db: Session = Depends(get_db)):
    from app.models import Config
    from sqlalchemy import desc

    configs = (
        db.query(Config)
        .order_by(desc(Config.created_at))
        .all()
    )

    return [
        ConfigResponse.from_orm_model(c)
        for c in configs
    ]