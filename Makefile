.PHONY: build up down down-v show-logs show-logs-api makemigrations migrate collectstatic superuser volume authors-db flake8 black-check black-diff black isort-check isort-diff isort

build:
	docker compose -f local.yml up --build -d --remove-orphans
up:
	docker compose -f local.yml up -d

down:
	docker compose -f local.yml down

down-v:
	docker compose -f local.yml down -v

banker-config:
	docker compose -f local.yml config
	
show-logs:
	docker compose -f local.yml logs

show-logs-api:
	docker compose -f local.yml logs api

migrations:
	docker compose -f local.yml run --rm api python manage.py makemigrations

migrate:
	docker compose -f local.yml run --rm api python manage.py migrate

collectstatic:
	docker compose -f local.yml run --rm api python manage.py collectstatic --no-input --clear

superuser:
	docker compose -f local.yml run --rm api python manage.py createsuperuser


volume:
	docker volume inspect author-havin-clone-api_local_postgres_data

flash:
	docker compose -f local.yml run --rm api python manage.py flash

network-inspect:
	docker network inspect bancker_local_nw


banker-db:
	docker compose -f local.yml exec postgres psql --username=alisultani --dbname=banker

flake8:
	docker compose -f local.yml exec api flake8 .

black-check:
	docker compose -f local.yml exec api black . --check --exclude=migrations .

black-diff:
	docker compose -f local.yml exec api black . --diff --exclude=migrations

black:
	docker compose -f local.yml exec api black . --exclude=migrations

isort-check:
	docker compose -f local.yml exec api isort . --check-only --skip venv --skip migrations  

isort-diff:
	docker compose -f local.yml exec api isort . --diff --skip venv --skip migrations

isort:
	docker compose -f local.yml exec api isort . --skip venv --skip migrations

index:
	docker compose exec api python manage.py search_index --rebuild

create:
	docker compose -f local.yml exec api python manage.py search_index --create

pytest:
	docker compose -f local.yml run --rm api pytest -p no:warnigs --cov=. -v
pytest-error:
	docker compose -f local.yml run --rm api pytest -p no:warnings --cov=. -v --tb=short

cov-report:
	docker compose -f local.yml run --rm api pytest -p no:warnigs --cov=. --cov-report html


