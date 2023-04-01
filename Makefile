DOCKER := docker
CURRENT_DIR := $(shell pwd)
IMAGE_NAME := transcribot
GID := $(shell id -g)
UID := $(shell id -u)

build:
	$(DOCKER) build . -t $(IMAGE_NAME):latest

build_dev:
	$(DOCKER) build . -t $(IMAGE_NAME):latest --build-arg GID=$(GID) --build-arg UID=$(UID) --build-arg requirements=dev

run:
	$(DOCKER) run --name $(IMAGE_NAME) --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest

run_detach:
	$(DOCKER) run -d --name $(IMAGE_NAME) --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest

bash:
	$(DOCKER) run --rm --env-file .env -v $(CURRENT_DIR):/opt/app -v $(CURRENT_DIR)/whisper_models:/home/apprunner/.cache/whisper -ti $(IMAGE_NAME):latest bash
