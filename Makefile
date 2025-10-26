
.PHONY: setup migrate run test

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -U pip wheel && pip install -e . && pip install pytest

migrate:
	@echo "Apply DB migrations and (optionally) run legacy migration"; 
	alembic upgrade head
	python scripts/migrate_legacy.py --dry-run

run:
	bash scripts/run_dev.sh

test:
	pytest -q
