.PHONY: dev up down logs ps prod-up prod-down prod-logs health e2e-install e2e-run e2e-test-backend e2e-ui e2e-full

dev:
	docker compose -f docker-compose.dev.yml up -d --build

up:
	docker compose -f docker-compose.dev.yml up -d

down:
	docker compose -f docker-compose.dev.yml down

logs:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 backend

ps:
	docker compose -f docker-compose.dev.yml ps

prod-up:
	docker compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f --tail=100 backend

health:
	curl -sS http://localhost:8002/health || true

# E2E Testing Targets
e2e-install:
	@echo "📦 Installing E2E testing dependencies..."
	pip install -r requirements.txt
	cd ui && npm install
	cd ui && npx playwright install

e2e-test-backend:
	@echo "🧪 Running backend API tests..."
	.venv/bin/pytest tests/test_api_endpoints.py -v

e2e-ui:
	@echo "🎭 Running Playwright E2E tests..."
	cd ui && npx playwright test tests/e2e/canvas_sync.spec.ts

e2e-run: e2e-test-backend e2e-ui
	@echo "✅ All E2E tests completed!"

e2e-full: e2e-install e2e-run
	@echo "🚀 Complete E2E test suite finished!"