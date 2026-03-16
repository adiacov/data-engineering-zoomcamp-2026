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

produce-no-limit:
	uv run python ./src/streaming/producer_no_limit.py

flink-hourly_rides:
	docker compose exec jobmanager ./bin/flink run \
		-py /opt/src/streaming/jobs/job_hourly_rides.py \
		--pyFiles /opt/src

flink-pass-through:
	docker compose exec jobmanager ./bin/flink run \
		-py /opt/src/streaming/jobs/job_pass_through.py \
		--pyFiles /opt/src

flink-session-streak:
	docker compose exec jobmanager ./bin/flink run \
		-py /opt/src/streaming/jobs/job_session_streak.py \
		--pyFiles /opt/src

flink-largest_tip:
	docker compose exec jobmanager ./bin/flink run \
		-py /opt/src/streaming/jobs/job_largest_tip.py \
		--pyFiles /opt/src