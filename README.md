# Canvas Core Backend

FastAPI + SQLAlchemy + Alembic backend for Canvas AI Labs.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git (to clone the repo)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/canvas-ai-labs/canvas-core-backend.git
cd canvas-core-backend
```

### 2️⃣ Configure Environment
Create a `.env` file with your Canvas API credentials:
```bash
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL (auto-configured for Docker)
# - CANVAS_API_URL, CANVAS_API_KEY (required for Canvas sync)
# - OPENAI_API_KEY (required for LLM features)
```

### 3️⃣ Start Everything
```bash
# Start all services (backend, frontend, database, redis)
docker compose -f docker-compose.dev.yml up -d
```

### 4️⃣ Access the Application
- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8002
- **Health Check**: http://localhost:8002/health
- **API Docs**: http://localhost:8002/docs

### 5️⃣ Stop Services
```bash
docker compose -f docker-compose.dev.yml down
```

## 📊 What's Running?

| Service | Port | Purpose |
|---------|------|---------|
| Frontend (Next.js) | 3000 | Dashboard UI |
| Backend (FastAPI) | 8002 | API & Canvas sync |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & job queue |

## 📊 What's Running?

| Service | Port | Purpose |
|---------|------|---------|
| Frontend (Next.js) | 3000 | Dashboard UI |
| Backend (FastAPI) | 8002 | API & Canvas sync |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & job queue |

## 🛠️ Development Commands

### View Logs
```bash
# View all logs
docker compose -f docker-compose.dev.yml logs -f

# View specific service
docker logs canvas-core-backend-backend-1 -f
docker logs canvas-core-backend-frontend-1 -f
```

### Check Service Status
```bash
docker compose -f docker-compose.dev.yml ps
```

### Rebuild After Code Changes
```bash
# Rebuild and restart (for Dockerfile changes)
docker compose -f docker-compose.dev.yml up -d --build

# Note: Hot reload is enabled, so most code changes apply automatically
```

## 🗄️ Database Management

## 🗄️ Database Management

### Alembic Migrations

- Configure DATABASE_URL in .env
- To run migrations:

```bash
alembic upgrade head
```

- To autogenerate after model changes (review the diff before applying):

```bash
alembic revision --autogenerate -m "update models"
```

## 🧪 Testing

### Run All Tests
```bash
# Run backend API tests + Playwright E2E tests
make e2e-run
```

### Backend API Tests Only
```bash
.venv/bin/pytest tests/test_api_endpoints.py -v
```

### Frontend E2E Tests Only
```bash
cd ui && npx playwright test
```

### What the Tests Validate

1. **Backend API Tests** (`tests/test_api_endpoints.py`):
   - ✅ Health endpoint returns 200
   - ✅ Full sync endpoint completes successfully
   - ✅ Metrics endpoint returns correct structure
   - ✅ Data consistency between sync and metrics
   - ✅ CORS headers are present
   - ✅ Multiple sync calls are safe

2. **Frontend E2E Tests** (`ui/tests/e2e/canvas_sync.spec.ts`):
   - ✅ Dashboard loads without errors
   - ✅ "Full Sync" button triggers sync
   - ✅ Dashboard updates with real Canvas data
   - ✅ Screenshot saved at `ui/test-artifacts/canvas-sync.png`
   - ✅ Tests run in Chrome, Firefox, and Safari

## 🔧 Code Quality Tools

## 🔧 Code Quality Tools

```bash
# Linting
ruff check .

# Formatting
black .

# Import sorting
isort .

# Type checking
mypy .
```

## 📝 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /metrics` - Get sync metrics (courses, assignments, deadlines count)
- `POST /full_sync` - Trigger full Canvas data sync

### Data Endpoints
- `GET /courses` - List all courses
- `GET /assignments` - List all assignments

### AI/LLM Endpoints
- Requires `OPENAI_API_KEY` in `.env`
- See `/docs` for full API documentation

## 🐳 Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Next.js UI    │◄────────│  FastAPI Backend │
│  (port 3000)    │         │   (port 8002)    │
└─────────────────┘         └──────────────────┘
                                     │
                            ┌────────┴────────┐
                            ▼                 ▼
                    ┌──────────────┐  ┌─────────┐
                    │  PostgreSQL  │  │  Redis  │
                    │  (port 5432) │  │ (6379)  │
                    └──────────────┘  └─────────┘
```

- **Frontend**: Next.js with proxy (`/api/*` → `backend:8002`)
- **Backend**: FastAPI with auto-reload, CORS configured
- **Database**: PostgreSQL with persistent volumes
- **Cache**: Redis for job queue and caching

## 🚢 Production Deployment

Use the production compose file:

```bash
docker compose -f docker-compose.prod.yml up -d
```

Differences from dev:
- No auto-reload
- Optimized builds
- Production-ready settings

## 📚 Additional Resources

- **Makefile commands**: Run `make help` for all available commands
- **API Documentation**: http://localhost:8002/docs (when running)
- **Alembic migrations**: See `alembic/versions/` for migration history

## 🏷️ Version

Current stable version: **v0.1.0**

Baseline features:
- ✅ Docker-first architecture
- ✅ Backend on port 8002 with normalized routes
- ✅ Next.js proxy working with service name resolution
- ✅ Full E2E test coverage (backend + browser tests)
- ✅ Python 3.9 compatibility

