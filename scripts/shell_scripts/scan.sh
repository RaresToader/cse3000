#!/bin/bash

# Check if the subnet is provided as an argument! Might need to adapt based on how the AS is given to us
if [ -z "$1" ]; then
    echo "Usage: $0 <subnet>"
    exit 1
fi

SUBNET=$1

# Query Censys API for servers in the subnet, restricting to servers implementing DNS, NTP or Memcached
echo "Querying Censys for services in subnet $SUBNET..."

censys search "ip: $SUBNET AND services.service_name: {NTP, DNS, MEMCACHED}" > initial_list.json

# Filter JSON output from Censys API using jq
# output will be a JSON array holding tuples (ip, [(protocol,port])
echo "Processing data with jq..."
jq '[.[] | {ip: .ip, services: [.services[] | select(.service_name == "DNS" or .service_name == "NTP" or .service_name == "MEMCACHED") | {protocol: .transport_protocol, port: .port}]}]' initial_list.json > filtered_list.json

# Save the list into separate CSV files for DNS, NTP, and Memcached
echo "Generating CSV files..."

# Save the DNS servers
jq -r '[.[] | select(any(.services[]; .protocol == "UDP" and .port == 53)) | {ip, services: [.services[] | select(.protocol == "UDP" and .port == 53)]}] | .[] | [.ip, (.services[] | [.protocol, (.port|tostring)] | join(":"))] | @csv' filtered_list.json > dns.csv

# Save the NTP servers
jq -r '[.[] | select(any(.services[]; .protocol == "UDP" and .port == 123)) | {ip, services: [.services[] | select(.protocol == "UDP" and .port == 123)]}] | .[] | [.ip, (.services[] | [.protocol, (.port|tostring)] | join(":"))] | @csv' filtered_list.json > ntp.csv

# Save the Memcached servers
jq -r '[.[] | select(any(.services[]; .protocol == "TCP" and .port == 11211)) | {ip, services: [.services[] | select(.protocol == "TCP" and .port == 11211)]}] | .[] | [.ip, (.services[] | [.protocol, (.port|tostring)] | join(":"))] | @csv' filtered_list.json > memcached.csv

echo "CSV files have been created: dns.csv, ntp.csv, memcached.csv"


# Do cleanup!
rm filtered_list.json
rm initial_list.json