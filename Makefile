DOCKER := docker
CURRENT_DIR := $(shell pwd)
IMAGE_NAME := transcribot

build:
	$(DOCKER) build . -t $(IMAGE_NAME):latest

build_dev:
	$(DOCKER) build . -t $(IMAGE_NAME):latest --build-arg requirements=dev

run:
	$(DOCKER) run --rm --env-file .env -u "$(id -u):$(id -g)" -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest

run_detach:
	$(DOCKER) run -d --rm --env-file .env -u "$(id -u):$(id -g)" -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest

bash:
	$(DOCKER) run --rm --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest bash
