from pathlib import Path
import logging
from io import BytesIO
import zipfile
import requests
from common.config import set_logging, get_root_path

set_logging()
logger = logging.getLogger(__name__)

# Kestra config
KESRA_BASE_URL = "http://localhost:8080"
USERNAME = "admin@kestra.io"
PASSWORD = "Admin1234"


def upload_flows_from_dir(flows_dir: Path):
    # Find all YAML files
    flow_files = list(flows_dir.glob("*.yaml"))
    if not flow_files:
        logger.warning("No YAML flow files found in %s", flows_dir)
        return

    # Create in-memory ZIP
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for file_path in flow_files:
            zf.write(file_path, arcname=file_path.name)
    zip_buffer.seek(0)

    # POST request
    url = f"{KESRA_BASE_URL}/api/v1/flows/import"
    files = {"fileUpload": ("flows.zip", zip_buffer, "application/zip")}

    response = requests.post(url, auth=(USERNAME, PASSWORD), files=files, timeout=30)
    zip_buffer.close()

    if response.ok:
        logger.info("Successfully uploaded %d flows", len(flow_files))
    else:
        logger.error(
            "Failed to upload flows: %s - %s", response.status_code, response.text
        )
        response.raise_for_status()


def main():
    flows_directory = (
        get_root_path().resolve() / "modules" / "002-workflow-orchestration" / "flows"
    )
    upload_flows_from_dir(flows_directory)


if __name__ == "__main__":
    main()
