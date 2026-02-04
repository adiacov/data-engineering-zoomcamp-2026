"""Configuration file"""

from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)


def get_root_path() -> Path:
    """Returns the project rood Path object form a current working directory"""

    logger.info("Deriving root path from current working directory")

    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        return Path(env_root)

    # fallback: check cwd
    root_target = "data-engineering-zoomcamp-2026"
    cwd = Path(os.getcwd())
    if cwd.name == root_target:
        return cwd

    # fallback: search parents
    for parent in Path(os.getcwd()).parents:
        if parent.name == root_target:
            return Path(parent)

    result_msg = (
        f"Successfully found root path from current working directory: {env_root}"
        if env_root
        else f"Could not find project root path from current working directory: {env_root}"
    )

    logger.info(result_msg)
    return None


def set_logging():
    """Set logging"""
    logging.basicConfig(
        level=logging.INFO,  # Set the minimum level to log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",  # Define the message format
    )
