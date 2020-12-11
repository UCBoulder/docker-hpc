VERSION=0.1
NAME=cluster-jupyterlab
IMAGE_NAME=$(DOCKER_USER)/$(NAME)

TAG := $(shell git rev-parse --short HEAD)
IMAGE := $(IMAGE_NAME):$(TAG)
LATEST := $(IMAGE_NAME):latest

# DOCKER TASKS

# Build the container

build: ## Build the container
	docker build -t $(IMAGE) .
	make tag

build-no-cache: ## Build the container
	docker build -t $(IMAGE) --no-cache .

run: ## Run container with /home/mooc mapped to current directory
	docker run --rm -p 9999:9999 -i -t -e USERID=$UID --name="$(NAME)" $(LATEST)


# Docker tagging
tag: tag-latest tag-version ## Generate container tags for the `{version}` ans `latest` tags

tag-latest: ## Generate container `{version}` tag
	@echo 'create tag latest'
	docker tag $(IMAGE) $(LATEST)

tag-version: ## Generate container `latest` tag
	@echo 'create tag $(VERSION)'
	docker tag $(IMAGE) $(IMAGE_NAME):$(VERSION)-$(TAG)
