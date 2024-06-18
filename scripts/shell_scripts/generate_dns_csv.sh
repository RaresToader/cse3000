#!/bin/bash

# Check if the dns file is provided as an argument!
if [ -z "$1" ]; then
    echo "Usage: $0 <dns_file.json>"
    exit 1
fi

SUBNET=$1

# Filter JSON output from Censys API using jq
# output will be a JSON array holding tuples (ip, [(protocol,port])
echo "Processing data with jq..."
#jq '[.[] | {ip: .ip, services: [.services[] | select(.service_name == "DNS" or .service_name == "NTP" or .service_name == "MEMCACHED") | {protocol: .transport_protocol, port: .port}]}]' "$SUBNET" > filtered_list.json

echo "Generating CSV files..."

# Save the DNS server
#jq -r '[.[] | select(any(.services[]; .protocol == "UDP" and .port == 53)) | {ip, services: [.services[] | select(.protocol == "UDP" and .port == 53)]}] | .[] | [.ip, (.services[] | [.protocol, (.port|tostring)] | join(":"))] | @csv' filtered_list.json > ../../data/censys_full_csv/dns.csv
#jq -r '[.[] | .ip] | unique | @csv' "$SUBNET" > ../../data/censys_full_csv/dns.csv
jq -r '[.[] | .ip] | unique | .[]' "$SUBNET" > ../../data/censys_full_csv/dns.csv


echo "CSV file have been created: dns.csv"

# Do cleanup!
#rm filtered_list.json