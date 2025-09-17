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

## Run

Development server:

uvicorn backend.main:app --reload

Then open http://127.0.0.1:8000/ to view the static dashboard.

Health check:

curl http://127.0.0.1:8000/health

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

## Smoke Test

- Start server and visit root: should serve static dashboard.
- Try API endpoints under /api (courses, assignments, ai/*, llm/*). Some require env keys.

