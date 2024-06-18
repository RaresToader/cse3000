from scapy.all import *
from scapy.contrib.memcached import *

def memcached_stats_request(ip, port):
    # Memcached header fields for STATS command
    # Reference: https://github.com/memcached/memcached/wiki/BinaryProtocolRevamped#packet-structure
    magic = 0x80         # Request
    opcode = 0x10        # Opcode for STAT
    key_length = 0       # No key for STATS
    extras_length = 0    # No extras for STATS
    data_type = 0        # Always 0 for current Memcached implementations
    vbucket_id = 0       # Usually 0 for non-vBucket implementations
    total_body_length = 0 # No extras, no key, no value
    opaque = 0           # Data echoed back in the response
    cas = 0              # Data version check, not used in STATS

    # Build the header
    header = struct.pack('!BBHBBHIIQ', magic, opcode, key_length, extras_length, data_type, vbucket_id, total_body_length, opaque, cas)

    # Send the packet
    s = conf.L2socket(iface="eth0")
    s.send(Ether()/IP(dst=ip)/TCP(dport=port)/Raw(load=header))
    
    # Wait for a response
    response = s.recv(1024)
    print(response.show())

# Replace '' with the IP of your Memcached server and 11211 with the port
memcached_stats_request('', 11211)

# Memcached header for stats command (opcode 0x10 for stat)
# 0x80 is the request magic byte, 0x10 is the opcode for stat,
# 0x0000 is the key length (no key for general stats), 0x00 is the extras length,
# 0x00 is the data type, 0x0000 is the vbucket id,
# 0x00000000 is the total body length (no extras, no key, no value),
# 0x00000001 is the opaque (can be anything), 0x0000000000000000 is the CAS
# header = bytes.fromhex('80 10 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00')