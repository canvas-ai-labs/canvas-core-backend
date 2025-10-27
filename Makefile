.PHONY: dev up down logs ps prod-up prod-down prod-logs health

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