"""
FILE: app/main.py
PURPOSE: The entry point of the entire FastAPI application.

This is where everything comes together:
1. FastAPI app is created
2. Database tables are created (if they don't exist)
3. All routes are registered
4. Middleware (CORS) is configured

When you run 'uvicorn app.main:app', Python:
  - Imports this file
  - Finds the 'app' variable (the FastAPI instance)
  - Starts the web server
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routes import config_routes


# ─────────────────────────────────────────────────────────────
# LIFESPAN: Startup & Shutdown Events
# ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code here runs ONCE when the server starts (before handling any requests).
    
    We use it to:
    1. Create database tables (if they don't already exist)
       - Safe to run on every startup — won't destroy existing data
       - Equivalent to: CREATE TABLE IF NOT EXISTS configs (...)
    
    The 'yield' separates startup (above) from shutdown (below).
    Code after yield runs when the server is stopping.
    """
    print("🚀 CCMS Backend starting up...")
    print("📦 Creating database tables (if not exist)...")

    # This creates all tables defined in models.py
    # It reads all classes that inherit from Base and creates their tables
    Base.metadata.create_all(bind=engine)

    print("✅ Database tables ready!")
    print("🌍 Server is live at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")

    yield  # <-- Server is running here, handling requests

    # Shutdown code (runs when you press Ctrl+C)
    print("👋 CCMS Backend shutting down...")


# ─────────────────────────────────────────────────────────────
# FASTAPI APPLICATION INSTANCE
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Centralized Configuration Management System (CCMS)",
    description="""
## 🔧 CCMS — Phase 1 MVP

A centralized configuration server for managing service configurations
across different environments.

### What this API does:
- **Store** configurations for your microservices (payment-service, order-service, etc.)
- **Separate** configs by environment (dev, staging, prod)
- **Version** every config change — complete history preserved
- **Serve** configs to services via simple REST API calls

### Quick Start:
1. `POST /configs` — Create a new config
2. `GET /configs/{service}/{env}` — Fetch all configs for a service
3. `PUT /configs/{id}` — Update a config (creates new version)
4. `DELETE /configs/{id}` — Delete a config

### Version History:
`GET /configs/{service}/{env}/history/{key}` — See all versions of a config key
    """,
    version="1.0.0",
    contact={
        "name": "CCMS Development Team",
    },
    lifespan=lifespan  # Register our startup/shutdown handler
)


# ─────────────────────────────────────────────────────────────
# CORS MIDDLEWARE
# ─────────────────────────────────────────────────────────────

# CORS = Cross-Origin Resource Sharing
# This allows your API to be called from browsers running on different domains
# e.g., a React frontend at http://localhost:3000 calling your API at http://localhost:8000

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],        # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# REGISTER ROUTES
# ─────────────────────────────────────────────────────────────

# Include the config routes — this adds all the /configs endpoints to our app
app.include_router(config_routes.router)


# ─────────────────────────────────────────────────────────────
# ROOT ENDPOINT — Health Check
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint — a simple health check.
    
    Call GET http://localhost:8000/ to verify the server is running.
    """
    return {
        "service": "CCMS — Centralized Configuration Management System",
        "version": "1.0.0",
        "phase": "Phase 1 MVP",
        "status": "running",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "create_config":    "POST   /configs/",
            "get_configs":      "GET    /configs/{service_name}/{environment}",
            "update_config":    "PUT    /configs/{config_id}",
            "delete_config":    "DELETE /configs/{config_id}",
            "version_history":  "GET    /configs/{service_name}/{environment}/history/{config_key}"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check for load balancers and monitoring tools."""
    return {"status": "healthy", "service": "ccms-backend"}


@app.get("/services", tags=["Health"])
def list_services(db=None):
    """Overview of all registered services. Useful for admin dashboards."""
    from app.database import get_db
    from app.services import config_service
    import inspect

    # Get a DB session manually for this one-off endpoint
    gen = get_db()
    db = next(gen)
    try:
        return config_service.get_all_services_service(db)
    finally:
        try:
            next(gen)
        except StopIteration:
            pass
