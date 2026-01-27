# Package all /modules at once
build-all:
	uv build --clear --all-packages

# Start docker containers
docker-up:
	docker compose up -d

# Stop docker containers, clean
docker-down:
	docker compose down
