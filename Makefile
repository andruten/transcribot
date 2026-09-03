DOCKER := docker
CURRENT_DIR := $(shell pwd)
IMAGE_NAME := transcribot

check_env:
ifeq ("$(wildcard .env)","")
	cp env.sample .env
endif

build:
	$(DOCKER) build . -t $(IMAGE_NAME):latest

build_dev:
	$(DOCKER) build . -t $(IMAGE_NAME):latest --build-arg requirements=dev

run:
	$(DOCKER) run --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/root/.cache/whisper -ti $(IMAGE_NAME):latest

run_detached:
	$(DOCKER) run -d --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/root/.cache/whisper -ti $(IMAGE_NAME):latest

setup_local:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements/pro.txt

run_local: check_env
	set -a && . ./.env && set +a && .venv/bin/python -m main

bash:
	$(DOCKER) run --rm --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/root/.cache/whisper -ti $(IMAGE_NAME):latest bash

format: check_env build_dev
	@$(DOCKER) run --rm --env-file .env -v $(CURRENT_DIR):/opt/app $(IMAGE_NAME):latest ruff format

lint: check_env build_dev
	@$(DOCKER) run --rm --env-file .env -v $(CURRENT_DIR):/opt/app $(IMAGE_NAME):latest ruff check --fix --show-fixes

lint_check: check_env build_dev
	@$(DOCKER) run --rm --env-file .env $(IMAGE_NAME):latest ruff check --show-fixes

format_check: check_env build_dev
	@$(DOCKER) run --rm --env-file .env $(IMAGE_NAME):latest ruff format --check

test: check_env build_dev
	@$(DOCKER) run --rm --env-file .env $(IMAGE_NAME):latest python -m pytest .
