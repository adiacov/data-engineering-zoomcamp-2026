root=pipeline
version=0.0.1

# docker commands
docker-build:
	 docker build -t pipeline:$(version) .

docker-run:
	docker run --rm pipeline:$(version)

docker-debug:
	docker run -it --rm pipeline:$(version) bash

# project commands
build:
	pip install $(root)/.

run:
	python pipeline/pipeline.py

# multiple commands

# multi project
all: build run

# multi docker
docker-all: docker-build docker-run
