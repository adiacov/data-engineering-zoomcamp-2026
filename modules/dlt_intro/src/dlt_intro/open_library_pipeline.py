"""Template for building a `dlt` pipeline to ingest data from a REST API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def open_library_rest_api_source():
    """Define dlt resources from Open Library REST API endpoints."""
    config: RESTAPIConfig = {
        "client": {
            # Open Library API base URL
            "base_url": "https://openlibrary.org/",
            # Open Library uses session-based authentication or S3 keys
            # For public access, no authentication is required for most endpoints
            # If authentication is needed, it would be via cookies or S3 keys
        },
        "resource_defaults": {
            # Default configuration for all resources
            "endpoint": {
                "params": {
                    # Default parameters for API requests
                }
            }
        },
        "resources": [
            {
                "name": "books",
                "endpoint": {
                    "path": "search.json",
                    "method": "GET",
                    "params": {
                        # Search for books on data engineering
                        "q": "data engineering",
                        "limit": 100,
                        "offset": 0
                    },
                    "paginator": {
                        "type": "offset",
                        "limit_param": "limit",
                        "offset_param": "offset",
                        "limit": 100,
                        "maximum_offset": 1000,
                        "total_path": "numFound"
                    }
                }
            }
        ]
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name='open_library_pipeline',
    destination='duckdb',
    # `refresh="drop_sources"` ensures the data and the state is cleaned
    # on each `pipeline.run()`; remove the argument once you have a
    # working pipeline.
    refresh="drop_sources",
    # show basic progress of resources extracted, normalized files and load-jobs on stdout
    progress="log",
)


def main():
    """Run the Open Library pipeline."""
    load_info = pipeline.run(open_library_rest_api_source())
    print(load_info)  # noqa: T201


if __name__ == "__main__":
    main()
