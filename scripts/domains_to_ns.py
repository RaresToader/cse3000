import subprocess
from utils import read_domains_from_csv, write_to_json


def fetch_name_servers(domain):
    """
    Fetch name servers for a given domain using the 'dig' command.
    :param domain: The domain we're querying to find its name servers.
    :return: (potentially) a list of name servers.
    """
    command = f"dig {domain} NS +short"
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE)
        name_servers =  result.stdout.strip().split('\n')
        cleaned_name_servers = [ns[:-1] if ns.endswith('.') else ns for ns in name_servers] # there is a trailing dot as a consequence of running the dig command
        return cleaned_name_servers

    except subprocess.CalledProcessError:
        return []


def map_name_servers_to_domains(domains):
    """
    Map name servers to the domains they are authoritative for.
    :param domains: List of domain names.
    :return: Dictionary with name servers as keys and list of domains they are authoritative for as values.
    """
    ns_map = {}
    for domain in domains:
        name_servers = fetch_name_servers(domain)
        for ns in name_servers:
            if ns in ns_map:
                ns_map[ns].append(domain)
            else:
                ns_map[ns] = [domain]
    return ns_map



def main():
    input_file = input("Please enter the input file path, which contains a list of domain names.\n")
    output_file = input("Please enter the output file path.\n")

    domains = read_domains_from_csv(input_file)
    ns_map = map_name_servers_to_domains(domains)

    write_to_json(ns_map, output_file)

if __name__ == "__main__":
    main()
