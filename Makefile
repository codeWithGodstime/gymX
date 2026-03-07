# Makefile for GymX Django Project

# Local Development Commands
.PHONY: build-local up-local down-local logs-local migrate-local collectstatic-local shell-local

build-local:
	docker compose -f docker/docker-compose.local.yml build

up-local:
	docker compose -f docker/docker-compose.local.yml up --build

up-local-d:
	docker compose -f docker/docker-compose.local.yml up -d

down-local:
	docker compose -f docker/docker-compose.local.yml down

logs-local:
	docker compose -f docker/docker-compose.local.yml logs -f

migrate-local:
	docker compose -f docker/docker-compose.local.yml exec web python manage.py migrate_schemas

collectstatic-local:
	docker compose -f docker/docker-compose.local.yml exec web python manage.py collectstatic --noinput

shell-local:
	docker compose -f docker/docker-compose.local.yml exec web python manage.py shell

createsuperuser-local:
	docker compose -f docker/docker-compose.local.yml exec web python manage.py createsuperuser

# Production Commands
.PHONY: build-prod up-prod down-prod logs-prod migrate-prod collectstatic-prod

build-prod:
	docker compose -f docker/docker-compose.production.yml build

up-prod:
	docker compose -f docker/docker-compose.production.yml up

up-prod-d:
	docker compose -f docker/docker-compose.production.yml up -d

down-prod:
	docker compose -f docker/docker-compose.production.yml down

logs-prod:
	docker compose -f docker/docker-compose.production.yml logs -f

migrate-prod:
	docker compose -f docker/docker-compose.production.yml exec web python manage.py migrate

collectstatic-prod:
	docker compose -f docker/docker-compose.production.yml exec web python manage.py collectstatic --noinput

# Utility Commands
.PHONY: clean-volumes clean-images

clean-volumes:
	docker volume prune -f

clean-images:
	docker image prune -f

# Quick Start
.PHONY: start-local start-prod

start-local: build-local up-local-d
	@echo "Local development environment started. Access at http://localhost:8000"
	@echo "Mailhog UI: http://localhost:8025"
	@echo "Minio Console: http://localhost:9001"

start-prod: build-prod up-prod-d
	@echo "Production environment started. Access at http://localhost:8000"