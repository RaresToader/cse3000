#!/bin/bash

# Check if the ntp file is provided as an argument!
if [ -z "$1" ]; then
    echo "Usage: $0 <file_name>"
    exit 1
fi

SUBNET=$1

# Filter JSON output from Censys API using jq
# output will be a JSON array holding tuples (ip, [(protocol,port])
echo "Processing data with jq..."
#jq '[.[] | {ip: .ip, services: [.services[] | select(.service_name == "DNS" or .service_name == "NTP" or .service_name == "MEMCACHED") | {protocol: .transport_protocol, port: .port}]}]' "$SUBNET" > filtered_list.json

# Save the list into separate CSV files for NTP
echo "Generating CSV file..."

# Save the NTP servers
#jq -r '[.[] | select(any(.services[]; .protocol == "UDP" and .port == 123)) | {ip, services: [.services[] | select(.protocol == "UDP" and .port == 123)]}] | .[] | [.ip, (.services[] | [.protocol, (.port|tostring)] | join(":"))] | @csv' filtered_list.json > ../data/censys_csv/ntp.csv

jq -r '[.[] | .ip] | unique | .[]' "$SUBNET" > ../../data/censys_full_csv/ntp.csv

echo "CSV files have been created: ntp.csv"


# Do cleanup!
#rm filtered_list.json
