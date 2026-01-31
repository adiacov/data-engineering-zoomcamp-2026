# Package all /modules at once
build-all:
	uv build --clear --all-packages

# Start docker containers
docker-up:
	docker compose up -d

# Stop docker containers, clean
docker-down:
	docker compose down

# Encode base64 kestra-de-zoomcamp-flows keys
kestra_encode:
	@echo "Encoding kestra-de-zoomcamp-flows keys"
	@sed -i '/^SECRET_GCP_CREDS=/d' ./dev/gcp/.env-kestra
	@echo "SECRET_GCP_CREDS=$$(base64 ./dev/gcp/kestra-de-zoomcamp-flows.json -w 0)" >> ./dev/gcp/.env-kestra


