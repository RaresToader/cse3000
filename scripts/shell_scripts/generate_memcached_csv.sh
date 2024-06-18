#!/bin/bash

# Check if the filename is provided as an argument!
if [ -z "$1" ]; then
    echo "Usage: $0 <subnet>"
    exit 1
fi

SUBNET=$1

# Filter JSON output from Censys API using jq
# output will be a JSON array holding tuples (ip, [(protocol,port])
echo "Processing data with jq..."
jq '[.[] | {ip: .ip, services: [.services[] | select(.service_name == "DNS" or .service_name == "NTP" or .service_name == "MEMCACHED") | {protocol: .transport_protocol, port: .port}]}]' "$SUBNET" > filtered_list.json

echo "Generating CSV file..."

# Save the Memcached servers
#jq -r '[.[] | select(any(.services[]; .protocol == "TCP" and .port == 11211)) | {ip, services: [.services[] | select(.protocol == "TCP" and .port == 11211)]}] | .[] | [.ip, (.services[] | [.protocol, (.port|tostring)] | join(":"))] | @csv' filtered_list.json > ../data/censys_csv/memcached.csv
jq -r '[.[] | .ip] | unique | .[]' "$SUBNET" > ../../data/censys_full_csv/memcached.csv


echo "CSV files have been created: memcached.csv"


# Do cleanup!
rm filtered_list.json
