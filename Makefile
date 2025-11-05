
.PHONY: setup migrate run test

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -U pip wheel && pip install -e . && pip install pytest

migrate:
	@echo "Apply DB migrations and (optionally) run legacy migration";
	alembic upgrade head
	python scripts/migrate_legacy.py --dry-run

check:
	@python scripts/alembic_check_safe.py

db: migrate check
	@echo "DB upgraded + checked (safe). See tmp/alembic_drift.txt"

run:
	bash scripts/run_dev.sh

test:
	pytest -q
