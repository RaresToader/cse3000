# from scapy.fields import ShortField
# from scapy.layers.inet import IP, UDP
# from scapy.layers.dns import DNS, DNSQR, DNSRROPT
# from scapy.packet import Raw, Packet
# from scapy.sendrecv import sr1, sniff, send
# from scapy.volatile import RandShort
#
#
# class Query:
#     def create_packet(self, ip, *args, **kwargs):
#         raise NotImplementedError
#
#     def send_packet(self, pkt):
#         raise NotImplementedError
#
#
# class DNSQuery(Query):
#     def create_packet(self, ip, domain=".", qtype=255, qclass="IN", z=1):
#         dns = DNS(rd=1, ad=1)
#         dns.qd = DNSQR(qname=domain, qtype=qtype, qclass=qclass)
#         dns.ar = DNSRROPT(rclass=4096, rrname=0, extrcode=0, version=0, z=z)
#         request = IP(dst=ip) / UDP(dport=53, sport=RandShort()) / dns
#         return self.send_packet(request)
#
#     def send_packet(self, request):
#         try:
#             response = sr1(request, timeout=2, verbose=0)
#             if response:
#                 return len(request[DNS]), len(response[DNS])
#             else:
#                 return len(request[DNS]), 0
#         except Exception as e:
#             print(f"Error sending DNS packet: {e}")
#             return len(request[DNS]), 0
#
# class NTPQuery(Query):
#     def is_ntp_response(self, packet, ip):
#         return IP in packet and packet[IP].src == ip and UDP in packet and packet[UDP].sport == 123
#
#     def send_query(self, ip):
#         data = "\x17\x00\x03\x2a" + "\x00" * 4
#         try:
#             pkt = (IP(dst=ip) / UDP(dport=123, sport=RandShort()) / Raw(load=data))
#             request_size = len(pkt[Raw].load)
#             send(pkt)
#             responses = sniff(timeout=1, lfilter=lambda x: self.is_ntp_response(x, ip))
#             total_response_size = sum(len(response[UDP].payload) for response in responses)
#             if request_size > 0 and total_response_size > 0:
#                 return request_size, total_response_size
#             else:
#                 return request_size, 0
#         except Exception as e:
#             print(f"Error sending NTP packet: {e}")
#             return request_size, 0
#
#
# class MemcachedStrategy(Query):
#     class Memcached(Packet):
#         name = "Memcached"
#         fields_desc = [ShortField("magic", 0x80), ...]  # Shortened for brevity
#
#     def send_query(self, ip):
#         request = (IP(dst=ip) / UDP(dport=11211, sport=RandShort()) / self.Memcached(opcode=0x10))
#         try:
#             response = sr1(request, timeout=2, verbose=0)
#             if response:
#                 return len(request), len(response)
#             else:
#                 return len(request), 0
#         except Exception as e:
#             print(f"Error sending memcached packet: {e}")
#             return len(request), 0
#
# class QueryAnalyzer:
#     def __init__(self, strategy):
#         self.strategy = strategy
#
#     def analyse_ips(self, ip_list):
#         baf_values = []
#         for ip in ip_list:
#             req_size, resp_size = self.strategy.send_query(ip)
#             baf = self._calculate_baf(req_size, resp_size)
#             baf_values.append(baf)
#         return baf_values
#
#     def _calculate_baf(self, request_size, response_size):
#         if request_size > 0:
#             return response_size / request_size
#         return 0
#
#     class DNSStrategy:
#         def send_query(self, ip, domain="gr.", qtype=255, qclass="IN", z=0):
#             raise NotImplementedError
#
#     class RootNSQueryStrategy(DNSStrategy):
#         def send_query(self, ip):
#             dns = DNS(rd=1, ad=1)
#             dns.qd = DNSQR(qname="visitgreece.gr", qtype=2, qclass="IN")  # query section
#             dns.ar = DNSRROPT(rclass=4096, rrname=0, extrcode=0, version=0, z=1)  # additional records
#             request = IP(dst=ip) / UDP(dport=53, sport=RandShort()) / dns
#             return self._send(request)
#
#     class DNSKEYQueryStrategy(DNSStrategy):
#         def send_query(self, ip):
#             dns = DNS(ad=1)
#             dns.qd = DNSQR(qname="gr.", qtype=48)
#             dns.ar = DNSRROPT(rclass=4096, z=1)
#             request = IP(dst=ip) / UDP(dport=53, sport=RandShort()) / dns
#             return self._send(request)
#
#     class AnyQueryStrategy(DNSStrategy):
#         def send_query(self, ip):
#             dns = DNS(rd=1, ad=1)
#             dns.qd = DNSQR(qname="gr.", qtype=255, qclass="ANY")
#             request = IP(dst=ip) / UDP(dport=53, sport=RandShort()) / dns
#             return self._send(request)
#
#     class DNSStrategyContext:
#         def __init__(self, strategy):
#             self.strategy = strategy
#
#         def send_query(self, ip):
#             return self.strategy.send_query(ip)
#
#         def _send(self, request):
#             try:
#                 response = sr1(request, timeout=2, verbose=0)
#                 if response:
#                     return len(request[DNS]), len(response[DNS])
#                 else:
#                     return len(request[DNS]), 0
#             except Exception as e:
#                 print(f"Error sending DNS packet: {e}")
#                 return len(request[DNS]), 0
#
