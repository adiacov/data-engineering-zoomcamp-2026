from pathlib import Path
import logging
from io import BytesIO
import sys
import zipfile
import requests
from typing import List
from common.config import set_logging, get_root_path

set_logging()
logger = logging.getLogger(__name__)

# Kestra config (left unchanged as requested)
KESRA_BASE_URL = "http://localhost:8080"
USERNAME = "admin@kestra.io"
PASSWORD = "Admin1234"


def _get_all_yaml_files(directory: Path) -> List[Path]:
    """Return all .yaml and .yml files under a directory."""
    return list(directory.glob("**/*.yaml")) + list(directory.glob("**/*.yml"))


def upload_all_flows(flows_dir: Path) -> None:
    """Uploads all flows to Kestra instance."""
    flow_files = _get_all_yaml_files(flows_dir)

    if not flow_files:
        logger.warning("No YAML flow files found in %s", flows_dir)
        return

    logger.info("Uploading %d flows to Kestra", len(flow_files))
    _upload_flows_from_dir(flows_dir, flow_files)


def upload_single_flow(flows_dir: Path, flow_name: str) -> None:
    """Uploads a single flow to Kestra instance.

    :param flows_dir: root directory containing flow files
    :param flow_name: flow file name, with or without .yaml/.yml extension
    """

    if flow_name.endswith((".yaml", ".yml")):
        flows = list(flows_dir.glob(f"**/{flow_name}"))
    else:
        flows = list(flows_dir.glob(f"**/{flow_name}.yaml")) + list(
            flows_dir.glob(f"**/{flow_name}.yml")
        )

    if not flows:
        logger.error("Flow '%s' not found under %s", flow_name, flows_dir)
        return

    if len(flows) > 1:
        raise ValueError(
            f"Multiple flows named '{flow_name}' found. "
            "Please specify a unique file."
        )

    logger.info("Uploading flow '%s' to Kestra", flows[0].name)
    _upload_flows_from_dir(flows_dir, flows)


def _upload_flows_from_dir(flows_dir: Path, flow_files: List[Path]) -> None:
    """Create a ZIP from flow files and upload it to Kestra."""

    if not flow_files:
        logger.warning("No flows to upload; skipping request")
        return

    try:
        with BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in flow_files:
                    # Preserve directory structure relative to flows_dir
                    arcname = file_path.relative_to(flows_dir)
                    zf.write(file_path, arcname=arcname)

            zip_buffer.seek(0)

            url = f"{KESRA_BASE_URL}/api/v1/flows/import"
            files = {"fileUpload": ("flows.zip", zip_buffer, "application/zip")}

            response = requests.post(
                url,
                auth=(USERNAME, PASSWORD),
                files=files,
                timeout=30,
            )

        if response.ok:
            logger.info("Successfully uploaded %d flow(s)", len(flow_files))
        else:
            logger.error(
                "Failed to upload flows: %s - %s",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

    except requests.RequestException:
        logger.exception("Network error while uploading flows to Kestra")
        raise

    except Exception:
        logger.exception("Unexpected error while uploading flows")
        raise


def main() -> None:
    # Root Kestra flows directory
    flows_directory = (
        get_root_path().resolve() / "modules" / "002-workflow-orchestration" / "flows"
    )

    args = sys.argv

    if len(args) == 1:
        upload_all_flows(flows_directory)
    elif len(args) == 2:
        upload_single_flow(flows_directory, args[1])
    else:
        logger.warning(
            "Invalid arguments. Usage:\n"
            "  script.py            # upload all flows\n"
            "  script.py <flow>     # upload single flow"
        )


if __name__ == "__main__":
    main()
