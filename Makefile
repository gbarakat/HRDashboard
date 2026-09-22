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

dbt:              ## staging -> core -> ml feature views; every model is tested before its children build
	$(DBT) build $(DBT_FLAGS) --exclude tag:ml_output

ml:               ## pay_equity -> learner_segments -> attrition -> forecast, then test the ml.* outputs
	$(PYTHON) -m ml
	$(DBT) test $(DBT_FLAGS) --select tag:ml_output

test:
	$(PYTHON) -m pytest -q tests
	$(DBT) test $(DBT_FLAGS)
