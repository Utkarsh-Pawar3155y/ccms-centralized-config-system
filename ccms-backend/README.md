# 🔧 CCMS — Centralized Configuration Management System
### Phase 1 MVP Backend

A production-style REST API backend built with **Python + FastAPI + PostgreSQL**.  
This system acts as a centralized config server for microservices.

---

## 📁 Project Structure

```
ccms-backend/
│
├── app/
│   ├── __init__.py          # Makes 'app' a Python package
│   ├── main.py              # FastAPI app entry point — server starts here
│   ├── database.py          # PostgreSQL connection setup (SQLAlchemy engine)
│   ├── models.py            # Database table definitions (ORM models)
│   ├── schemas.py           # Request/Response data shapes (Pydantic)
│   ├── crud.py              # Raw database operations (Create/Read/Update/Delete)
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── config_routes.py # HTTP endpoint definitions (URL → function mapping)
│   │
│   └── services/
│       ├── __init__.py
│       └── config_service.py # Business logic layer
│
├── requirements.txt         # Python dependencies
├── .env.example             # Template for environment variables
└── README.md                # This file
```

### How data flows through the layers:

```
HTTP Request
    ↓
config_routes.py   (Which URL? What HTTP method?)
    ↓
config_service.py  (Business rules, validation)
    ↓
crud.py            (Database queries)
    ↓
PostgreSQL Database
    ↑
(Response flows back up the same chain)
```

---

## 🚀 Setup & Installation (Step by Step)

### Step 1 — Install Python

Check if Python is installed:
```bash
python --version
# or
python3 --version
```

Should show Python 3.10 or higher. If not installed:
- **Windows**: Download from https://python.org/downloads → Check "Add to PATH"
- **Mac**: `brew install python3` (or download from python.org)
- **Ubuntu/Debian**: `sudo apt install python3 python3-pip python3-venv`

---

### Step 2 — Download / Clone the project

If you have git:
```bash
git clone <your-repo-url>
cd ccms-backend
```

Or just copy the folder to your machine and open a terminal inside it:
```bash
cd path/to/ccms-backend
```

---

### Step 3 — Create a Virtual Environment

A virtual environment keeps this project's packages separate from other projects.
Think of it as a clean sandbox just for this project.

```bash
# Create the virtual environment (run this ONCE)
python -m venv venv

# Activate it (run this EVERY time you open a new terminal)

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

You'll see `(venv)` at the start of your terminal prompt when it's active. ✅

---

### Step 4 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` — the web framework
- `uvicorn` — the web server that runs FastAPI
- `sqlalchemy` — the ORM (talks to PostgreSQL)
- `psycopg2-binary` — PostgreSQL driver
- `pydantic` — data validation
- `python-dotenv` — reads .env files

---

### Step 5 — Install & Setup PostgreSQL

#### On Windows:
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer — remember the password you set for the `postgres` user
3. Open "pgAdmin" or "SQL Shell (psql)" from Start Menu

#### On Mac:
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### On Ubuntu/Debian:
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

### Step 6 — Create the Database

Connect to PostgreSQL:

```bash
# On Mac/Linux:
psql -U postgres

# On Windows (in SQL Shell / psql):
# Just press Enter when asked for hostname, port, username
# Then type your password
```

Once inside the `postgres=#` prompt, run:

```sql
-- Create the database
CREATE DATABASE ccms_db;

-- Verify it was created
\l

-- Exit psql
\q
```

---

### Step 7 — Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Open .env in any text editor and set your database password
```

Edit the `.env` file:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/ccms_db
```

Replace `YOUR_PASSWORD_HERE` with the password you set when installing PostgreSQL.

---

### Step 8 — Run the Server

```bash
uvicorn app.main:app --reload
```

- `app.main` → the file `app/main.py`
- `:app` → the variable named `app` inside that file (the FastAPI instance)
- `--reload` → auto-restarts when you change code (great for development!)

You should see:
```
🚀 CCMS Backend starting up...
📦 Creating database tables (if not exist)...
✅ Database tables ready!
🌍 Server is live at: http://localhost:8000
📖 API Documentation: http://localhost:8000/docs
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 🧪 Testing the API

### Option 1: Swagger UI (Recommended for beginners)

Open your browser and go to:
```
http://localhost:8000/docs
```

You'll see an interactive UI where you can test every endpoint by clicking them!

---

### Option 2: Test Manually with curl

#### Create a config:
```bash
curl -X POST http://localhost:8000/configs/ \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "payment-service",
    "environment": "prod",
    "key": "DB_HOST",
    "value": "payment-db.internal"
  }'
```

#### Get configs for a service:
```bash
curl http://localhost:8000/configs/payment-service/prod
```

#### Update a config (use the id returned from create):
```bash
curl -X PUT http://localhost:8000/configs/1 \
  -H "Content-Type: application/json" \
  -d '{"value": "new-payment-db.internal"}'
```

#### Delete a config:
```bash
curl -X DELETE http://localhost:8000/configs/1
```

#### Get version history:
```bash
curl http://localhost:8000/configs/payment-service/prod/history/DB_HOST
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check + endpoint overview |
| `GET` | `/health` | Simple health check |
| `GET` | `/services` | List all registered services |
| `POST` | `/configs/` | Create a new configuration |
| `GET` | `/configs/{service}/{env}` | Get all configs for a service |
| `PUT` | `/configs/{id}` | Update a config (creates new version) |
| `DELETE` | `/configs/{id}` | Delete a config |
| `GET` | `/configs/{service}/{env}/history/{key}` | Get version history |

---

## 📦 Example Configs to Create

```json
// Payment Service - Prod
{ "service_name": "payment-service", "environment": "prod", "key": "DB_HOST", "value": "payment-db.internal" }
{ "service_name": "payment-service", "environment": "prod", "key": "TIMEOUT", "value": "30" }
{ "service_name": "payment-service", "environment": "prod", "key": "CACHE_SIZE", "value": "512" }

// Order Service - Dev
{ "service_name": "order-service", "environment": "dev", "key": "DB_HOST", "value": "localhost:5432" }
{ "service_name": "order-service", "environment": "dev", "key": "FEATURE_FLAG", "value": "true" }

// Notification Service - Staging
{ "service_name": "notification-service", "environment": "staging", "key": "SMTP_HOST", "value": "smtp.staging.internal" }
```

---

## 🔍 Versioning Explained

Every time you `PUT` (update) a config, a **new row** is created with `version + 1`.
The old row is **kept** for history.

```
DB_HOST for payment-service/prod:

v1 → "payment-db-old.internal"   (created Jan 1)
v2 → "payment-db.internal"       (updated Jan 15)  ← current
```

When you call `GET /configs/payment-service/prod`, you get **only v2** (latest).
When you call `GET /configs/payment-service/prod/history/DB_HOST`, you get **both v1 and v2**.

---

## 🛑 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused` | PostgreSQL not running | `sudo systemctl start postgresql` |
| `password authentication failed` | Wrong password in .env | Check your .env DATABASE_URL |
| `database "ccms_db" does not exist` | DB not created | Run `CREATE DATABASE ccms_db;` in psql |
| `409 Conflict` | Config key already exists | Use PUT to update it |
| `404 Not Found` | Wrong service name/id | Check your service_name spelling |
| `ModuleNotFoundError` | Packages not installed | Run `pip install -r requirements.txt` |
| `venv not found` | Virtual env not activated | Run `source venv/bin/activate` |

---

## 🏗️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Programming language |
| FastAPI | Web framework — creates the REST API |
| Uvicorn | ASGI web server — runs FastAPI |
| PostgreSQL | Relational database — stores configs |
| SQLAlchemy | ORM — Python ↔ PostgreSQL bridge |
| Pydantic | Data validation — validates API inputs/outputs |
| python-dotenv | Reads .env configuration files |

---

*Built for CCMS Phase 1 MVP — College + Industry Project*
