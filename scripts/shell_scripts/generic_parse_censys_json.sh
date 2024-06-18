#!/bin/bash

# Usage: ./generic_parse_censys_json.sh <input_file.json> <service_name> <transport_protocol> <port>.
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <input_file.json> <service_name> <transport_protocol> <port>"
    exit 1
fi

INPUT_FILE="$1"
SERVICE_NAME="$2"
PROTOCOL="$3"
PORT=$4
OUTPUT_DIR=../data/censys # run from one directory above (remember the pwd is the one where you run the script from)
OUTPUT_FILE=$OUTPUT_DIR/${SERVICE_NAME}.csv


# Ensure the output directory exists
mkdir -p $OUTPUT_DIR

# Filter the JSON output (the format supported by Censys) using jq
echo "Processing data with jq for $SERVICE_NAME..."

jq_filter="[.[] | {ip: .ip, services: [.services[] | select(.service_name == \"$SERVICE_NAME\") | {protocol: .transport_protocol, port: .port}]}]"

jq "$jq_filter" "$INPUT_FILE" > filtered_list.json

#cat filtered_list.json

echo "Generating CSV file for $SERVICE_NAME..."

# Generate CSV based on protocol type
jq_csv_filter="[.[] | select(any(.services[]; .protocol == \"$PROTOCOL\" and .port == $PORT)) | {ip, services: [.services[] | select(.protocol == \"$PROTOCOL\" and .port == $PORT)]}] | .[] | [.ip, (.services[] | [.protocol, (.port|tostring)] | join(\":\"))] | @csv"

jq -r "$jq_csv_filter" filtered_list.json > "$OUTPUT_FILE"

#cat "$OUTPUT_FILE"

echo "CSV file has been created: $OUTPUT_FILE"

# Do cleanup!
rm filtered_list.json
