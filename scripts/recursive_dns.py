import subprocess

from utils import read_ips, save_ips


def check_recursive(ip):
    """
    Checks if the given ip address is a recursive DNS server.
    :param ip: the DNS server to check
    :return: whether the DNS server that was checked is recursive
    """
    try:
        result = subprocess.run(
            ["dig", f"@{ip}", "google.com", "+rec", "+time=1"],
            capture_output=True,
            text=True
        )
        return "NOERROR" in result.stdout
    except Exception as e:
        print(f"Error checking IP {ip}: {e}")
        return False


def process_dns_hosts(input_path, output_path):
    """
    Helper function that parses and processes the hosts and saves the results.
    :param input_path: the input path to the file
    :param output_path: the output path
    :return: None
    """
    valid_ips = []

    ips = read_ips(input_path)

    total_ips = len(ips)

    for index, ip in enumerate(ips):
        if check_recursive(ip):
            valid_ips.append(ip)
        progress_percentage = (index + 1) / total_ips * 100
        print(f"Processed {index + 1}/{total_ips} IPs ({progress_percentage:.2f}%)")

    save_ips(valid_ips, output_path)

if __name__ == "__main__":
    input_file_path = input("Enter the path to the CSV file with DNS IP addresses: \n")
    output_file_path = input("Enter the path for the output CSV file of valid recursive DNS hosts: \n")
    process_dns_hosts(input_file_path, output_file_path)
