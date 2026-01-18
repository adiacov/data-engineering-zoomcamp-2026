# Project metadata
version=0.0.1
package_name=pipeline

# Docker commands
docker-build:
	docker build -t $(package_name):$(version) .

# docker-run:
# 	docker run --rm $(package_name):$(version)

docker-run:
	docker run --rm -v $(PWD)/data:/app/data $(package_name):$(version)

docker-debug:
# 	docker run -it --rm $(package_name):$(version) bash
	docker run -it --rm -v $(PWD)/data:/app/data $(package_name):$(version) bash

# Docker cleanup for this project only
docker-clean:
# Remove any stopped containers from this image
	-docker ps -a -q --filter ancestor=$(package_name):$(version) | xargs -r docker rm
# Remove the project image
	-docker rmi -f $(package_name):$(version)


# Project commands
build:
	python -m pip install -e .

run:
	python src/$(package_name)/pipeline.py

clean:
	rm -rf build dist *.egg-info src/$(package_name).egg-info

# Multi-step commands
all: clean build run

docker-all: docker-clean docker-build docker-run