#!/bin/bash

# Helper functions
info() {
    echo "[INFO] $1";
}

error() {
    echo "[ERROR] $1";
}

# Program arguments
TAXI_TYPE=$1 # taxi dataset. one of [green, yellow]
YEAR=$2 # ingestion YEAR
MO=$3 # ingestion MONTH
printf -v MONTH %02d ${MO} # ingestion MONTH zero padded

# Program variables
BASE_URL="https://d37ci6vzurychx.cloudfront.net/trip-data"
FILE_NAME="${TAXI_TYPE}_tripdata_${YEAR}-${MONTH}.parquet"
URL="${BASE_URL}/${FILE_NAME}"

DATA_DIR="/home/adiacov/Documents/private/projects/data-engineering/data-engineering-zoomcamp-2026/data"
TARGET_DIR="${DATA_DIR}/taxi/ingestion/${TAXI_TYPE}/${YEAR}/${MONTH}"
FILE="${TARGET_DIR}/${FILE_NAME}"

info "Starting taxi parquet file ingestion: ${FILE_NAME}";

if [[ -f ${FILE} ]]; then
    info "File already exists ${FILE}.";
    info "Skip ingestion.";
    exit 0;
fi

mkdir -p ${TARGET_DIR}
wget -q ${URL} -O ${FILE}

info "Finished file ingestion ${FILE}";