# import pylibmc
#
#
#
# def connect_to_memcached(host):
#     mc = pylibmc.Client([host], binary=True)
#
#     slabs = mc.get_stats('slabs')
#     print(slabs)
#     if not slabs:
#         print("Failed to retrieve slab statistics")
#         return set()
#
#     # print(stats_items)
#     slab_ids = set()
#     for server_address, stats_dict in slabs:
#         for key in stats_dict.keys():
#             print(key)
#             if ':' in key:
#                 slab_id = key.split(':')[0]
#                 slab_ids.add(slab_id)
#
#
#     print(slab_ids)
#
#     # Data to be stored in every key => at most 1MB
#     large_data = "a" * (1024 * 1024)
#
#     small_data = "a" * 10
#     # Split data into chunks
#
#     # mc.set('a', small_data) # 43 bytes request
#
#
#     # chunk = mc.get('a') # 39 bytes request
#
#     # mc.
#     # print(chunk)
import telnetlib


def get_slab_ids(server, port=11211):
    """
    Get slab ids from a Memcached server
    :param server: the Memcached server
    :param port: the port to connect to
    :return: the set of slab ids
    """
    tn = telnetlib.Telnet(server, port)

    tn.write(b'stats items\n')  # => 12 bytes
    tn.write(b'quit\n')

    # Read the output from the server
    output = tn.read_all().decode('utf-8')

    # Parse the output to extract slab IDs
    slab_ids = set()
    for line in output.splitlines():
        if line.startswith('STAT items'):
            parts = line.split(':')
            if len(parts) > 1:
                slab_id = parts[1].split()[0]
                slab_ids.add(slab_id)
    return slab_ids


def get_keys_for_slab(server, slab_id, port=11211):
    """
    For a given slab id, return all keys for that slab
    :param server: the server to connect to
    :param slab_id: the id of the slab to get keys for
    :param port: the port to connect to (11211 default for Memcached)
    :return: a dictionary, the keys for that slab, and the length of the values associated with the keys
    """
    tn = telnetlib.Telnet(server, port)

    # Send cachedump for the slab to get info about keys
    cmd = f'stats cachedump {slab_id} 100\n'.encode('utf-8')
    tn.write(cmd)
    tn.write(b'quit\n')

    output = tn.read_all().decode('utf-8')

    # Parse the output to extract keys
    keys = {}
    for line in output.splitlines():
        if line.startswith('ITEM'):
            parts = line.split()
            if len(parts) > 1:
                key = parts[1]
                size_str = parts[2].strip('[').strip(']')
                size = int(size_str.split(' ')[0])
                keys[key] = size
    return keys


def get_all_keys(server, port=11211):
    """
    Gets all keys for a given Memcached server.
    :param server: the Memcached server
    :param port: the port to connect to
    :return: all the (key, size of value associated with the key) in the server
    """
    slab_ids = get_slab_ids(server, port)

    all_keys = {}
    for slab_id in slab_ids:
        slab_keys = get_keys_for_slab(server, slab_id, port)
        all_keys.update(slab_keys)

    return all_keys


def get_max_baf(keys_with_sizes):
    """
    Get the maximum BAF that can be obtained with the keys and values stored in a memcached server
    :param keys_with_sizes: a dictionary holding keys and the size of the values associated with the keys
    :return: the maximum attainable BAF
    """
    request_size = 3
    response_size = 0
    for key, size in keys_with_sizes.items():
        if(size > len(key) + 1): # only consider keys that actually amplify
            request_size = request_size + len(key) + 1
            response_size += size
    return response_size , request_size


if __name__ == "__main__":
    ip = input("Enter an IP\n")
    keys_with_sizes = get_all_keys(ip)
    print(get_max_baf(keys_with_sizes))

# 1,048,576 bytes can be at most scored by a memcached server == 1 MB
# number of keys depends, but we could assume one character length keys =>
# 128 ascii characters => 128 * 1MB / request => maximum baf size


