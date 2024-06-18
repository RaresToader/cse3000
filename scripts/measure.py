import time

import numpy as np
# from matplotlib import pyplot as plt

from scapy.fields import ShortField, ByteField, IntField, LongField
from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.dns import DNS, DNSQR, DNSRROPT
from scapy.layers.netflow import port
from scapy.layers.ntp import NTPPrivate, NTP
from scapy.packet import Raw, Packet, Padding
from scapy.sendrecv import sr1, sniff, send
from scapy.volatile import RandShort

from memcached_client import get_max_baf, get_all_keys
from utils import read_ips, save_ips, read_json, write_to_json

dns_query_type = {
    "DNSKEY": 48,
    "ANY": 255
}


def valid_dns_response(packet, ip):
    """
     Filter function used when sniffing for a DNS packet answer to check its validity.
    :param packet: Response packet under test
    :param ip: Source IP address in response (Destination IP in request) => DNS host
    :return: True if the packet is a valid DNS response, False otherwise
    """
    # rules to check if a DNS packet is valid
    # the source IP of the packet we sniff needs to be the IP of the resolver we set
    # there has to be a UDP section in the response and the source port should be 53
    # rcode should be 0 which is NOERROR
    # qr == 1 indicates that the query is a response!
    if is_fragment(packet):
        return packet[IP].src == ip

    return (IP in packet and packet[IP].src == ip and
            UDP in packet and packet[UDP].sport == 53 and
            ((DNS in packet and packet[DNS].qr == 1 and
              packet[DNS].rcode == 0) or packet.haslayer(Raw)))

    # also handle Raw responses! in case of a malformed DNS packet =>
    # scapy seems to sniff Raw responses

    # BitEnumField("rcode", 0, 4, {0: "ok", 1: "format-error",
    #                              2: "server-failure", 3: "name-error",
    #                              4: "not-implemented", 5: "refused"}),


def is_fragment(pkt):
    """
    Determine if the given packet is a fragment of an original larger packet.
    This function checks if the packet contains an IP layer and then verifies whether
    the packet's IP header indicates that it is a fragment. This is determined by checking
    two conditions:
    1. The 'flags' field of the IP header has the More Fragments (MF) bit set, which
      indicates that there are more fragments after this one.
    2. The 'frag' field, which indicates the fragment offset, is greater than 0,
      signifying that the packet is not the first fragment.

    :param pkt: The packet to be checked.
    :returns bool: True if the packet is a fragment, False otherwise.
    """
    return IP in pkt and (pkt[IP].flags == 1 or pkt[IP].frag > 0)


def send_dns_query(ip, domain="SL", query_type=255):
    """
    Send a DNS query to the given IP.
    :param ip: the IP to send the query to, the DNS resolver
    :param domain: the domain we're querying (default: .)
    :param query_type: the type of DNS query (default: 255 => ANY)
    :return: a tuple (length of request, length of response)
    """
    dns = DNS(ad=1)
    dns.qd = DNSQR(qname=domain, qtype=query_type, qclass="IN")  # query section
    dns.ar = DNSRROPT(rclass=4096, z=1)  # additional records
    # rclass = 32768

    request = IP(dst=ip) / UDP(dport=53, sport=RandShort()) / dns

    try:
        send(request, verbose=0)

        timeout_duration = 1.2  # time in seconds to wait for a response
        responses = sniff(lfilter=lambda x: valid_dns_response(x, ip), timeout=timeout_duration)
        # print(responses)
        # < Sniffed: TCP:0
        # UDP: 1
        # ICMP: 0
        # Other: 0 >
        # ../data/censys_full_csv/dns_filtered_that_respond.csv
        # calculate the total payload length of all responses!
        response_payload_length = 0
        for response in responses:
            # response.show()
            if Raw in response:
                response_payload_length += len(response[Raw])
            elif DNS in response:
                response_payload_length += len(response[DNS])
            # if (UDP in response):
            #     response_payload_length += response[UDP].len - 8
        request_payload_length = len(request[DNS])
        # print(request_payload_length, response_payload_length)
        return request_payload_length, response_payload_length
    except Exception as e:
        print(f"Error sending DNS packet to {ip}: {e}")
        return len(request[DNS]), 0


def is_ntp_response(packet, ip):
    """
    Filter for capturing NTP responses from a specific IP.
    """
    return IP in packet and packet[IP].src == ip and UDP in packet and packet[UDP].sport == 123


def send_ntp_query(ip):
    """
    Send a 'monlist' NTP query to the given IP.
    :param ip: the IP to send the query to
    :return: a tuple (length of request, length of response)
    """
    data = "\x17\x00\x03\x2a" + "\x00" * 4  # 0x17 for private mode, 0x00 for response, 0x03 for version, 0x2a for monlist
    try:
        pkt = (IP(dst=ip) / UDP(dport=123, sport=RandShort()) / Raw(load=data))

        request_size = len(pkt[Raw].load)
        try:

            send(pkt)
            responses = sniff(timeout=1, lfilter=lambda x: is_ntp_response(x, ip))
            total_response_size = 0
            for response in responses:
                total_response_size += len(response[UDP].payload)
                if Padding in response:
                    total_response_size -= len(response[Padding])
            # total_response_size = sum(len(response[UDP].payload) for response in responses)  # response[NTP]
            if request_size >= 0 and total_response_size > 0:
                amplification_factor = total_response_size / request_size
                print(amplification_factor)
                return request_size, total_response_size
            else:
                return request_size, 0
        except Exception as e:
            print(f"Error sending NTP monlist packet to {ip}: {e}")
            return request_size, 0
    except Exception as e:
        print(f"Error constructing NTP monlist packet to {ip}: {e}")
        return 0, 0


def send_ntp_mode7_command(target_ip, command_code=1):
    # NTP Mode 7 requires a specific format:
    # - implementation: 3 (XNTPD)
    # - request_code: command_code (this changes based on the command)
    # (0 for PEER_LIST, 1 for PEER_LIST_SUM, 16 for GET_RESTRICT).
    # - sequence, status, association_id usually 0 for basic requests
    # - auth and key_id are 0 since no authentication is being used
    # ntp = NTPPrivate(
    #     # rm_vn_mode=0x1B,
    #     response=0,  # This is a request
    #     more=0,  # Not expecting multiple packets
    #     version=2,  # Version number 2/3
    #     implementation=3, # Assuming XNTPD
    #     auth=0,  # No authentication
    #     mode=7, # 6 => mode 6 (control), or mode 7 (private)
    #     seq=0,  # Sequence number
    #     request_code=command_code, # => 12 for CTL_OP_REQ_NONCE and 31 for UNSETTRAP
    #     err=0,
    #     nb_items=0,  # Number of data items
    #     mbz=0,  # Must be zero
    #     data_item_size=0,  # Size of each data item
    #     # data=(b'\x00' * 40)  # => ntpdc and ntpq add padding
    # )

    # Stack and send the packet
    try:
        packet = IP(dst=target_ip) / UDP(dport=123, sport=RandShort()) / NTPPrivate(
            # rm_vn_mode=0x1B,
            response=0,  # This is a request
            more=0,  # Not expecting multiple packets
            version=2,  # Version number 2/3
            implementation=3,  # Assuming XNTPD
            auth=0,  # No authentication
            mode=7,  # 6 => mode 6 (control), or mode 7 (private)
            seq=0,  # Sequence number
            request_code=command_code,  # => 12 for CTL_OP_REQ_NONCE and 31 for UNSETTRAP
            err=0,
            nb_items=0,  # Number of data items
            mbz=0,  # Must be zero
            data_item_size=0,  # Size of each data item
            # data=(b'\x00' * 40)  # => ntpdc and ntpq add padding
        )

        request_size = len(packet[NTP])

        try:
            send(packet)

            responses = sniff(timeout=1, lfilter=lambda x: is_ntp_response(x, target_ip))

            total_response_size = 0
            for response in responses:
                # sum(len(response[UDP].payload) for response in responses))  # response[NTP]
                total_response_size = total_response_size + len(response[UDP].payload)
                if Padding in response:
                    total_response_size -= len(response[Padding])
            if request_size >= 0 and total_response_size > 0:
                amplification_factor = total_response_size / request_size
                print(request_size, total_response_size, amplification_factor)
                return request_size, total_response_size
            else:
                return request_size, 0
            # return 0, 0
        except Exception as e:
            print(f"Error sending NTP packet to {target_ip}: {e}")
            return request_size, 0
    except Exception as e:
        print(f"Error constructing NTP packet to {target_ip}: {e}")
        return 0, 0


# Memcached packet (opcode 0x10 for stat)
# https://github.com/memcached/memcached/wiki/BinaryProtocolRevamped#packet-structure
# => from memcached wiki, describes the packet structure of memcached
# I used it as a reference in creating the memcached packet
class Memcached(Packet):  # extend the packet class
    name = "Memcached"
    fields_desc = [ShortField("magic", 0x80),
                   ByteField("opcode", 0),
                   ShortField("key_length", 0),
                   ByteField("extras_length", 0),
                   ByteField("data_type", 0),
                   ShortField("vbucket", 0),
                   IntField("total_body_length", 0),
                   IntField("opaque", 0),
                   LongField("cas", 0)]


def send_memcached_query_helper(ip, command):
    """
    Send a memcached query to the given IP.
    :param ip: the IP address to send the query to
    :param command: the command to be sent to the server
    :return: the decoded payload response
    """
    request = (IP(dst=ip) / UDP(sport=RandShort(), dport=11211) / Raw(load=command))
    # Raw(load="\x00\x01\x00\x00\x00\x01\x00\x00stats slabs\r\n"))
    try:
        response = sr1(request, timeout=2, verbose=0)

        if response and Raw in response:
            raw_payload = response[Raw].load
            decoded_payload = raw_payload.decode('utf-8', errors='ignore')
            # print(decoded_payload)
            return decoded_payload
        return ""
    except Exception as e:
        print(f"Failed sending memcached packet to {ip}: {e}, command: {command}")
        return ""


def parse_stats_items_response(response):
    """
    Parse the response from 'stats items' to extract slab IDs.
    :param response: the response from 'stats items' command
    :return: a list of slab IDs
    """
    slab_ids = []
    for line in response.splitlines():
        if line.startswith("STAT items:"):
            slab_id = line.split(':')[1]
            if slab_id not in slab_ids:
                slab_ids.append(slab_id)
    return slab_ids


# ITEM hu [117500 b; 1718029205 s]
# END
#
def parse_cachedump_response(response):
    """
    Parse the response from 'stats cachedump' to extract keys and their sizes.
    :param response: the response from 'stats cachedump' command
    :return: a list of tuples (key, size)
    """
    keys_and_sizes = []
    response = response.strip()
    for line in response.splitlines():
        if "ITEM" in line:
            parts = line.split()
            if len(parts) >= 3:
                key = parts[1]
                size_info = parts[2].strip('[]').split('b;')[0]
                keys_and_sizes.append((key, int(size_info)))
    return keys_and_sizes


def measure_baf_memcached(ip):
    """
    Finds the key with the largest associated value from a Memcached server and outputs the request and response size
    of a "get" with the corresponding key.
    :param ip: the IP address of the Memcached server
    :return: request size, response size
    """

    def is_memcached_response(pkt):
        return IP in pkt and pkt[IP].src == ip

    try:
        # Get slab information
        stats_items_response = send_memcached_query_helper(ip, "\x00\x01\x00\x00\x00\x01\x00\x00stats items\r\n")
        slab_ids = parse_stats_items_response(stats_items_response)

        largest_key = None
        largest_size = 0
        largest_BAF = 0
        # Iterate over slab classes
        for slab_id in slab_ids:
            cachedump_response = send_memcached_query_helper(ip,
                                                             f"\x00\x01\x00\x00\x00\x01\x00\x00stats cachedump {slab_id} 0\r\n")
            keys_and_sizes = parse_cachedump_response(cachedump_response)

            for key, size in keys_and_sizes:
                theoretical_req_size = 13 + len(key) + 1
                theoretical_resp_size = size
                theoretical_baf = theoretical_resp_size / theoretical_req_size
                if theoretical_baf > largest_BAF:
                    largest_BAF = theoretical_baf
                    largest_size = size
                    largest_key = key

        request = (IP(dst=ip) / UDP(sport=RandShort(), dport=11211) / Raw(
            load=f"\x00\x01\x00\x00\x00\x01\x00\x00get {largest_key}\r\n"))

        print(largest_key)
        # print(largest_size)
        request_size = len(request[Raw].load)
        send(request)

        responses = sniff(timeout=5, lfilter=is_memcached_response)
        total_response_size = 0
        # count = 0
        for response in responses:
            # if UDP in response:
            #     print(len(response[UDP].payload))
            #     total_response_size += len(response[UDP].payload)
            if Raw in response:
                # count += 1
                # print(len(response[Raw]))
                total_response_size += len(response[Raw])

        # print(count)
        # print(request_size)
        # print(total_response_size)
        return request_size, total_response_size

    except Exception as e:
        print(f"Error sending memcached packet to {ip}: {e}")
        return 0, 0



# def send_memcached_query2(ip):
#     """
#     Send a memcached stats query to the given IP.
#     :param ip: the IP address to send the query to
#     :return:
#     """
#     try:
#
#         ip = IP(dst=ip)
#
#         syn = TCP(sport=RandShort(), dport=11211, flags='S')
#         syn_ack = sr1(ip / syn)  # send SYN to initialise connection
#
#         # TCP SYN-ACK response
#         ack = TCP(sport=syn.sport, dport=11211, seq=syn_ack.ack, ack=syn_ack.seq + 1, flags='A')
#         sr1(ip / ack)  # / send
#
#         payload = "stats\r\n"  # Memcached commands also end with carriage return and newline
#         request = TCP(sport=syn.sport, dport=11211, seq=ack.seq, ack=syn_ack.seq + 1, flags='PA')
#         response = sr1(ip / request / Raw(load=payload))
#
#         last_ack = TCP(sport=syn.sport, dport=port, seq=response.ack, ack=response.seq + len(response.load), flags='A')
#         sr1(ip / last_ack)  # / send
#
#         fin = TCP(sport=syn.sport, dport=port, seq=last_ack.seq, ack=last_ack.ack, flags='FA')
#         fin_ack = sr1(ip / fin)
#
#         # Last ACK to complete the termination
#         last_ack = TCP(sport=syn.sport, dport=port, seq=fin_ack.ack, ack=fin_ack.seq + 1, flags='A')
#         sr1(ip / last_ack)  # / send
#
#         request_size = len(request)
#         response_size = len(response)
#         print(request_size)
#         print(response_size)
#         return request_size, response_size
#     except Exception as e:
#         print(f"Failed sending memcached packet to {ip}: {e}")
#         return len(request), 0


def send_memcached_query_over_tcp(ip):
    try:
        resp, req = get_max_baf(get_all_keys(ip))
        return req, resp

    except Exception as e:
        print(f"Failed sending memcached packet to {ip}: {e}")
        return 0, 0


def calculate_baf(request_size, response_size):
    """
    Helper method to compute the BAF (bandwidth amplification factor).
    :param request_size: the size of the request (UDP payload) in bytes
    :param response_size: the size of the response (UDP payload) in bytes
    :return: the BAF for the given request and response
    """
    if request_size > 0:
        # print(response_size / request_size)
        return response_size / request_size
    return 0


def analyse_ips(ip_list, function):
    """
    Helper method to compute the BAF for each IP address provided.
    :param ip_list: the list of IP addresses
    :param function: the function to send packets that returns request and response size
    :return: the list of BAFs for each IP address
    """
    baf_values = []
    initial_size = len(ip_list)
    for i in range(len(ip_list)):
        ip = ip_list[i]
        req_size, resp_size = function(ip)
        baf = calculate_baf(req_size, resp_size)
        baf_values.append(baf)
        if (i % 50 == 0):
            print(f"Progress: {i} / {initial_size}")
        time.sleep(0.1)
    return baf_values


def process_ips(ip_dict):
    """
    Process each IP and domain pair in the dictionary.
    :param ip_dict: Dictionary mapping IPs to a list of domains
    :return: Dictionary with IPs, domains, and their BAFs
    """
    results = {}
    all_bafs = []
    for ip, domains in ip_dict.items():
        ip_results = {}
        for domain in domains:
            req_size, resp_size = send_dns_query(ip, domain)
            baf = calculate_baf(req_size, resp_size)
            print(baf)
            all_bafs.append(baf)
            ip_results[domain] = baf
        results[ip] = ip_results
    return results, all_bafs


def main():
    input_file = input("Please enter the input filename. \n")
    mode = input("Please enter the service type (DNS/NTP/Memcached): ").lower()

    ips = read_ips(input_file)

    if mode == 'dns':
        baf = analyse_ips(ips, send_dns_query)
    elif mode == 'ntp':
        baf = analyse_ips(ips, send_ntp_query)
    elif mode == 'memcached':
        baf = analyse_ips(ips, measure_baf_memcached)
    else:
        print("Incorrect mode. Please enter either 'dns', 'ntp' or 'memcached'!")
        return

    print("Mean BAF:", np.mean(baf))
    print("Standard Deviation BAF:", np.std(baf))
    print("Variance BAF:", np.var(baf))

    data = zip(ips, baf)
    output_file = input("Please enter the output file path. \n")

    save_ips(data, output_file, baf=True)


if __name__ == "__main__":
    main()
