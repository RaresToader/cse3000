import json
import subprocess

from utils import write_to_json, read_json


def resolve_ip(nameserver):
    """
    Use the dig command to resolve the IP address of a nameserver.

    :param nameserver: the nameserver to resolve
    :return: the IP address of the nameserver
    """
    result = subprocess.run(['dig', '+short', nameserver], capture_output=True, text=True)
    return result.stdout.strip()


# https://ipstack.com/blog/5-free-geolocation-apis-to-retrieve-user-coordinates-in-latitude-&-longitude =>
# ways to find where an IP is from

def is_ip_in_country(ip_address, country_code):
    """
    Check if the given IP address is located in Greece using the ipinfo.io API.

    :param ip_address: The IP address to check
    :param country_code: The country code to check
    :return: True if the IP is in Greece, False otherwise
    """
    try:
        response = subprocess.run(['curl', f'http://ipinfo.io/{ip_address}/json'], capture_output=True, text=True)
        data = json.loads(response.stdout)
        return data.get('country') == country_code
    except Exception as e:
        print("Exception while checking if IP is in Greece:", e, "ip address is", ip_address)
        return False


def create_ip_to_domain_map(nameserver_data, country_code):
    """
    Create a map from IP addresses to the domain names they are authoritative for, filtering by IPs in Greece.

    :param nameserver_data: dictionary mapping nameservers to domain names
    :country_code: the country code to check
    :return: mapping of IP addresses to domain names
    """
    ip_to_domains = {}
    for ns, domains in nameserver_data.items():
        ip = resolve_ip(ns)
        if is_ip_in_country(ip, country_code):
            if ip in ip_to_domains:
                ip_to_domains[ip].extend(domains)
            else:
                ip_to_domains[ip] = domains
    return ip_to_domains


if __name__ == "__main__":
    input_file =  input("Please enter the input file path, which contains a map from name servers to domain names.\n")
    output_file = input("Please enter the output file path.\n")
    input_country = input("Please enter the country code you wish the nameservers are in.\n")

    nameservers = read_json(input_file)
    ip_map = create_ip_to_domain_map(nameservers, input_country)
    write_to_json(ip_map,  output_file)
