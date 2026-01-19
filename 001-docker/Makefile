# Project metadata
version=0.0.1
package_name=pipeline

# Docker commands
docker-build:
	docker build -t $(package_name):$(version) .

docker-run:
	docker run -it --rm \
	--network=001-docker_default \
	-e DB_HOST=postgres \
	$(package_name):$(version) \
	--year 2021 \
	--month 1 \
	--chunksize 100000 \
	--db-user postgres \
	--db-password postgres \
	--db-name ny_taxi \
	--db_table yellow_taxi_data

docker-debug:
	docker run -it --rm $(package_name):$(version) bash

# Docker cleanup for this project only
docker-clean:
# Remove any stopped containers from this image
	-docker ps -a -q --filter ancestor=$(package_name):$(version) | xargs -r docker rm
# Remove the project image
	-docker rmi -f $(package_name):$(version)


# Project commands
build:
	python -m pip install -e .
# 	python -m pip install -r requirements.txt && \
	python -m pip install -e .

run:
	python -m $(package_name).ingest_data \
	--year 2021 \
	--month 1 \
	--chunksize 100000 \
	--db-user postgres \
	--db-password postgres \
	--db-name ny_taxi \
	--db_table yellow_taxi_data

clean:
	rm -rf build dist **/*.egg-info

# Multi-step commands
all: clean build run

docker-all: docker-build docker-run