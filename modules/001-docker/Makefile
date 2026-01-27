# -----------------------------
# Module 001-docker
# -----------------------------

# Module metadata
VERSION := 0.0.1
PACKAGE_NAME := pipeline
IMAGE_NAME := $(PACKAGE_NAME):$(VERSION)
DIST_NAME := $(PACKAGE_NAME)-$(VERSION)

# Paths (relative to module's Makefile)
ROOT_PATH := $(abspath ../../)# two levels up from module
DIST_PATH := $(ROOT_PATH)/dist
SRC_PATH := src/pipeline
DOCKERFILE := docker/Dockerfile

# UV / Python (local dev)
run:
	uv run $(SRC_PATH)/ingest_data.py \
		--year 2021 \
		--month 1 \
		--chunksize 100000 \
		--db-user postgres \
		--db-password postgres \
		--db-name ny_taxi \
		--db-table-prefix yellow_taxi_data

clean:
	@echo "Deleting all $(PACKAGE_NAME)-$(VERSION) source distributions and wheels from $(DIST_PATH)"
	rm -f "$(ROOT_PATH)/dist/$(PACKAGE_NAME)-"*


# Docker commands (local dev)
docker-build:
	docker build \
		-f $(DOCKERFILE) \
		-t $(IMAGE_NAME) \
		$(ROOT_PATH)

docker-run:
	docker run -it --rm \
		--network=de_zoomcamp_network \
		-e DB_HOST=postgres \
		-e DATA_DIR=/data \
		-v $(pwd)/data:/data \
		$(IMAGE_NAME) \
		--year 2021 \
		--month 1 \
		--chunksize 100000 \
		--db-user postgres \
		--db-password postgres \
		--db-name ny_taxi \
		--db-table-prefix yellow_taxi_data

docker-debug:
	docker run -it --rm \
		$(IMAGE_NAME) \
		bash

docker-clean:
	-docker rmi -f $(IMAGE_NAME)

docker-all: docker-build docker-run
