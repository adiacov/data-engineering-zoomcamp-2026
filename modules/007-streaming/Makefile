d-build:
	docker compose up --build

d-up:
	docker compose up

d-upd:
	docker compose up -d

d-down:
	docker compose down

d-downv:
	docker compose down -v

produce:
	uv run python ./src/streaming/producer.py

flink-hourly_rides:
	docker compose exec jobmanager ./bin/flink run \
		-py /opt/src/streaming/jobs/job_hourly_rides.py \
		--pyFiles /opt/src

flink-pass-through:
	docker compose exec jobmanager ./bin/flink run \
		-py /opt/src/streaming/jobs/job_pass_through.py \
		--pyFiles /opt/src