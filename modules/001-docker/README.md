# Data Engineering Zoomcamp

## Homework

[FIND HOMEWORK HERE](homework.md)

## Docker-based Ingestion Pipeline

This project ingests NYC taxi data into PostgreSQL.
PostgreSQL is provided via **Docker Compose** and is required for both local and containerized runs.

---

## Prerequisites

* Docker
* Docker Compose
* Python 3.13+
* GNU Make

---

## Environment Configuration

The database host is configured via environment variable:

```bash
DB_HOST=postgres   # Docker
DB_HOST=localhost  # Local
```

If not set, the default is `localhost`.

---

## Build

### Start infrastructure (required)

Starts PostgreSQL and pgAdmin.

```bash
docker compose up -d
```

---

### Build locally

Installs the project in editable mode.

```bash
make build
```

---

### Build Docker image

Builds the ingestion image.

```bash
make docker-build
```

---

## Run

### Run locally

Runs ingestion against the Dockerized PostgreSQL.

```bash
make run
```

---

### Run with Docker

Runs ingestion inside a container.

```bash
make docker-run
```

---

### Build + Run (local)

```bash
make all
```

---

### Build + Run (Docker)

```bash
make docker-all
```

---

## Debugging

Interactive shell inside the container:

```bash
make docker-debug
```

---

## Services

* **PostgreSQL**: `localhost:5432`
* **pgAdmin**: [http://localhost:5050](http://localhost:5050)

  * user: `admin@admin.com`
  * password: `admin`
