# Canvas Core Backend

FastAPI + SQLAlchemy + Alembic backend for Canvas AI Labs.

## Setup

1. Create and populate a .env file (see .env.example):
	- DATABASE_URL
	- CANVAS_API_URL, CANVAS_API_KEY (required for Canvas sync endpoints)
	- OPENAI_API_KEY (required for LLM endpoints)

2. Install dependencies (prefer a venv):
	- pip install -r requirements.txt
	- Optional dev tools: pre-commit install

## Run (Docker-first)

This repository is Docker-first. Start the full development environment using Docker Compose.

Start development services:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

Access:

- Backend API: http://localhost:8002
- Frontend UI: http://localhost:3000
- Health check: curl http://localhost:8002/health

## Alembic

- Configure DATABASE_URL in .env
- To run migrations:

alembic upgrade head

- To autogenerate after model changes (review the diff before applying):

alembic revision --autogenerate -m "update models"

## Linting/Formatting/Types

- Ruff: ruff check .
- Black: black .
- isort: isort .
- mypy: mypy .

## Docker Development

Quick start with Docker:

```bash
# Start development environment
make dev

# Check services
make ps

# View logs
make logs

# Stop services
make down
```

Access:
- Backend API: http://localhost:8002
- Frontend UI: http://localhost:3000
- Health check: `make health`

## E2E Testing

The project includes comprehensive end-to-end testing that validates the full Canvas sync workflow:

### Quick E2E Test

```bash
# Install dependencies and run all E2E tests
make e2e-full
```

### Individual Test Components

```bash
# Install E2E testing dependencies
make e2e-install

# Run backend API tests only
make e2e-test-backend

# Run frontend Playwright tests only
make e2e-ui

# Run both backend and frontend tests
make e2e-run
```

### What the E2E Tests Do

1. **Backend API Tests** (`tests/test_api_endpoints.py`):
   - Validates `/health`, `/full_sync`, and `/metrics` endpoints
   - Tests data consistency between sync operations and metrics
   - Ensures proper API response structures

2. **Frontend E2E Tests** (`ui/tests/e2e/canvas_sync.spec.ts`):
   - Navigates to dashboard and verifies no error banners
   - Clicks "Full Sync" button and waits for completion
   - Polls `/api/metrics` until courses > 0 (60s timeout)
   - Verifies dashboard cards update with real data
   - Takes screenshot at `test-artifacts/canvas-sync.png`

The E2E test validates the complete user journey: dashboard loads → sync triggers → data fetches → UI updates successfully.

## Smoke Test

- Start server and visit root: should serve static dashboard.
- Try API endpoints under /api (courses, assignments, ai/*, llm/*). Some require env keys.

