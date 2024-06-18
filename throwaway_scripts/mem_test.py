import socket
#
# # Configuration for Memcached server
# MEMCACHED_SERVER = ""
# MEMCACHED_PORT = 11211
# BUFFER_SIZE = 4096
#
# # UDP client setup
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
# # Memcached UDP request header structure:
# # 0-1 Request ID
# # 2-3 Sequence number
# # 4-5 Total number of datagrams
# # 6-7 Reserved for future use
# request_id = b'\x01\x02'  # Randomly chosen request ID
# sequence_number = b'\x00\x00'
# total_datagrams = b'\x00\x01'
# reserved = b'\x00\x00'
#
# # Command: stats
# command = 'stats\r\n'
# data = request_id + sequence_number + total_datagrams + reserved + command.encode()
#
# # Sending command to Memcached server
# client_socket.sendto(data, (MEMCACHED_SERVER, MEMCACHED_PORT))
#
# # Receiving and processing the response
# received_data, addr = client_socket.recvfrom(BUFFER_SIZE)
# print("Received from Memcached:", received_data.decode())
#
# # Closing the socket
# client_socket.close()
ip = ""
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.2)  # set the timeout
    s.connect((ip, 11211))  ## 11211 is the default port for memcached
    s.send(b"stats\r\n")  # send a "version" query
    response = s.recv(1024)
    s.close()
    print(response)
except Exception as e:
    print(f"Error checking Memcached for {ip}: {e}")