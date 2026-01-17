root=pipeline

docker-build:
	 docker build -t pipeline:0.0.1 .

docker-run:
	docker run -it --rm pipeline:0.0.1

install:
	pip install $(root)

run:
	python3 $(root)/pipeline.py