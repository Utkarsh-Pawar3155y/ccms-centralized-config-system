"""
FILE: app/services/config_service.py
PURPOSE: Business logic layer between routes and CRUD.

Why have a service layer when we already have CRUD?

CRUD = pure database operations (no business rules)
Service = business logic (rules, validation, orchestration)

Example of "business logic":
  - "Before deleting a config, check if it's a critical system config"
  - "When creating a config, log an audit event"
  - "When fetching configs, apply any transformations"

For Phase 1, the service layer is simple — it mostly calls CRUD directly.
But it gives us a clean place to add business logic later without
touching the routes or the CRUD functions.

Architecture:
    HTTP Request → Route → Service → CRUD → Database
    HTTP Response ← Route ← Service ← CRUD ← Database
"""

from app.websocket_manager import manager
import asyncio
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import crud
from app.schemas import ConfigCreate, ConfigUpdate, ConfigResponse, ConfigListResponse, MessageResponse


def create_config_service(db: Session, config_data: ConfigCreate) -> ConfigResponse:
    """
    Business logic for creating a config.
    
    1. Calls CRUD to create the config
    2. Handles the "already exists" case → converts to HTTP 409 Conflict
    3. Returns a clean response schema
    """
    try:
        new_config = crud.create_config(db, config_data)
    except ValueError as e:
        # ValueError from CRUD (duplicate) → HTTP 409 Conflict
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    response = ConfigResponse.from_orm_model(new_config)

    # 🔥 Send real-time update
    async def send_update():
        await manager.broadcast({
            "event": "config_created",
            "service": response.service_name,
            "environment": response.environment,
            "key": response.key,
            "value": response.value,
            "version": response.version
        })

    asyncio.run(send_update())

    return response


def get_configs_service(
    db: Session,
    service_name: str,
    environment: str
) -> ConfigListResponse:
    """
    Business logic for fetching all configs for a service+environment.
    
    Returns the LATEST version of each config key.
    
    How? Since updates create new rows with higher versions,
    we need to deduplicate — keeping only the highest version per key.
    """
    all_configs = crud.get_configs_for_service(db, service_name, environment)

    if not all_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No configurations found for service='{service_name}', environment='{environment}'"
        )

    # Deduplicate: keep only the latest version for each config_key
    # This handles the case where a key has been updated (multiple versions exist)
    latest_configs: dict[str, object] = {}
    for config in all_configs:
        key = config.config_key
        if key not in latest_configs or config.version > latest_configs[key].version:
            latest_configs[key] = config

    # Convert to response schemas
    config_responses = [
        ConfigResponse.from_orm_model(c)
        for c in sorted(latest_configs.values(), key=lambda x: x.config_key)
    ]

    return ConfigListResponse(
        service_name=service_name,
        environment=environment,
        count=len(config_responses),
        configs=config_responses
    )


def update_config_service(
    db: Session,
    config_id: int,
    update_data: ConfigUpdate
) -> ConfigResponse:
    """
    Business logic for updating a config.
    
    Validation:
    - Check that at least one field is being updated
    - Check that the config exists
    """
    # Check that at least one field was provided
    if update_data.value is None and update_data.environment is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided to update: 'value' or 'environment'"
        )

    updated_config = crud.update_config(db, config_id, update_data)

    if updated_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config with id={config_id} not found"
        )

    response = ConfigResponse.from_orm_model(updated_config)

    async def send_update():
        await manager.broadcast({
            "event": "config_updated",
            "service": response.service_name,
            "environment": response.environment,
            "key": response.key,
            "value": response.value,
            "version": response.version
        })

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_update())
    except RuntimeError:
        asyncio.run(send_update())

    return response


def delete_config_service(db: Session, config_id: int) -> MessageResponse:
    """
    Business logic for deleting a config.
    
    Returns a clear success message or raises 404.
    """
    # Check the config exists before deleting (to give meaningful error)
    config = crud.get_config_by_id(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config with id={config_id} not found"
        )

    success = crud.delete_config(db, config_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete config. Please try again."
        )

    return MessageResponse(
        message=f"Config '{config.config_key}' for service '{config.service_name}' deleted successfully",
        config_id=config_id
    )


def get_version_history_service(
    db: Session,
    service_name: str,
    environment: str,
    config_key: str
) -> dict:
    """
    Business logic for getting version history of a specific config key.
    
    Returns all versions ordered newest first.
    """
    versions = crud.get_config_version_history(db, service_name, environment, config_key)

    if not versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No version history found for "
                f"service='{service_name}', environment='{environment}', key='{config_key.upper()}'"
            )
        )

    return {
        "service_name": service_name,
        "environment": environment,
        "config_key": config_key.upper(),
        "total_versions": len(versions),
        "history": [ConfigResponse.from_orm_model(v) for v in versions]
    }


def get_all_services_service(db: Session) -> dict:
    """Returns overview of all registered services and environments."""
    services = crud.get_all_services(db)
    return {
        "total_service_environments": len(services),
        "services": services
    }
