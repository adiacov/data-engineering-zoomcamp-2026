# Data Engineering Zoomcamp

## Docker workshop

### Build (local)

Installs the project as a Python package.

```bash
make build
```

### Run (local)

Runs the pipeline entry point.

```bash
make run
```

### Build + Run (local)

Sequential build and execution.

```bash
make all
```

### Docker Build

Builds the Docker image.

```bash
make docker-build
```

### Docker Run

Runs the pipeline inside a container.

```bash
make docker-run
```

### Docker Debug

Starts an interactive shell in the container.

```bash
make docker-debug
```

### Docker Build + Run

Builds and runs the Docker image.

```bash
make docker-all
```
