SHELL  := /bin/bash
PYTHON ?= python3
DBT    ?= dbt
DBT_FLAGS := --project-dir dbt --profiles-dir dbt

.PHONY: all up down reset debug data dbt ml test

## make all: empty DB -> raw -> staging/core (tested) -> ml -> tests
all: up data dbt ml test

## Postgres lifecycle
up:
	docker compose up -d --wait postgres

down:
	docker compose down

reset:            ## drop the volume: next `make all` starts from an empty database
	docker compose down -v

debug:
	$(DBT) debug $(DBT_FLAGS)

## Pipeline
data:
	$(PYTHON) -m generator.load

dbt:
	$(DBT) build $(DBT_FLAGS) --exclude path:models/ml

ml:
	$(PYTHON) -m ml.pay_equity
	$(PYTHON) -m ml.learner_segments
	$(PYTHON) -m ml.attrition
	$(PYTHON) -m ml.forecast
	$(DBT) build $(DBT_FLAGS) --select path:models/ml

test:
	$(PYTHON) -m pytest -q
	$(DBT) test $(DBT_FLAGS)
