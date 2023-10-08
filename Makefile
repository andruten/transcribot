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
	$(DOCKER) run --name $(IMAGE_NAME) --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest

run_detached:
	$(DOCKER) run -d --name $(IMAGE_NAME) --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest

bash:
	$(DOCKER) run --rm --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest bash

test: check_env build_dev
	@$(DOCKER) run --rm --env-file .env $(IMAGE_NAME):latest python -m pytest .

lint: check_env build_dev
	@$(DOCKER) run --rm --env-file .env $(IMAGE_NAME):latest flake8 .
