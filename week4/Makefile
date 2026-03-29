.PHONY: run test format lint seed

HOST ?= 127.0.0.1
PORT ?= 8000
PYTHONPATH_DIR ?= .

ifeq ($(OS),Windows_NT)
PY_ENV_PREFIX = set "PYTHONPATH=$(PYTHONPATH_DIR)" &&
else
PY_ENV_PREFIX = PYTHONPATH=$(PYTHONPATH_DIR)
endif

run:
	$(PY_ENV_PREFIX) uvicorn backend.app.main:app --reload --host $(HOST) --port $(PORT)

test:
	$(PY_ENV_PREFIX) pytest -q backend/tests

format:
	black .
	ruff check . --fix

lint:
	ruff check .

seed:
	$(PY_ENV_PREFIX) python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
