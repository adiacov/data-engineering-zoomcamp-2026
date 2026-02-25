from typing import Any

import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)


@dlt.source(name="yellow_taxi")
def github_source() -> Any:
    # Create a REST API configuration for the GitHub API
    # Use RESTAPIConfig to get autocompletion and type checking
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net",
            "paginator": {
                "type": "page_number",
                "base_page": 1,
                "total_path": None,
                "stop_after_empty_page": True,
            },
        },
        # The default configuration for all resources and their endpoints
        "resource_defaults": {
            "endpoint": {
                "params": {
                    "per_page": 1000,
                },
            },
        },
        "resources": [
            {
                "name": "data_engineering_zoomcamp_api",
                "table_name": "taxi_data",
            }
        ],
    }

    yield from rest_api_resources(config)


def main() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="ingestion",
        progress="log",
    )

    load_info = pipeline.run(github_source())
    print(load_info)  # noqa: T201


if __name__ == "__main__":
    main()
