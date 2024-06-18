import subprocess
import csv

from utils import read_ips, write_to_json


def find_buffer_size(ip):
    """
    Runs the dig command on the given IP address to retrieve the UDP payload size (EDNS max buffer size).
    :param ip: the ip of the DNS resolver
    :return: the UDP size if found, otherwise None
    """
    try:
        command = ['dig', f'@{ip}', '.', '+dnssec', '+notcp']
        result = subprocess.check_output(command, text=True)

        for line in result.split('\n'):
            if 'udp:' in line:
                udp_size = line.split('udp:', 1)[1].split()[0].strip()
                return udp_size
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running dig for {ip}: {str(e)}")
        return None


def run_fpdns(ip):
    """
    Runs FPDNS fingerprinting on the given host.
    :param ip: the ip of the DNS resolver
    :return: a string, the version of DNS that was fingerprinted
    """
    try:
        # Run the fpdns command on a DNS host to retrieve the version
        result = subprocess.check_output(['fpdns', '-t', '20', ip], text=True)
        # Extract only the version
        parsed_result = result.split(':', 1)[1].strip() if ':' in result else 'No result'
        # print(parsed_result)
        return parsed_result
    except subprocess.CalledProcessError as e:
        print(f"Error running fpdns for {ip}: {str(e)}")
        return 'Error'


# Process each IP and write results to CSV

def process_ips_fpdns(ips, output_csv_path, result_counter):
    """
    Processes the given list of IP addresses, retrieving the version of DNS that was fingerprinted for each one.
    :param ips: the given list of IP addresses
    :param output_csv_path: the output CSV file path
    :param result_counter: the number of DNS fingerprinting results for each version
    :return: nothing
    """
    with open(output_csv_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['IP', 'Buffer Size'])
        init_size = len(ips)
        for i in range(len(ips)):
            ip = ips[i]
            # result = run_fpdns(ip)
            result = find_buffer_size(ip)
            if result == None:
                result = "None"
            csv_writer.writerow([ip, result])

            if result in result_counter:
                result_counter[result] += 1
            else:
                result_counter[result] = 1

            if i % 50 == 0:
                print(f"Processed {i}/{init_size}")

if __name__ == '__main__':
    # Path to the file containing the IP addresses
    ip_path = "../data/censys_full_csv/dns_filtered_that_respond.csv"

               # + input("Enter the csv file name of the ips: "))
    ips = read_ips(ip_path)  # read the IPS from the csv
    # Path to the output CSV file
    output_csv_path = "../data/censys_full_csv/dns_filtered_buffer_sizes.csv"
                       # + input("Enter the csv file name of the output file: "))

    # Path to the output JSON file for counters
    output_json_path = "../data/censys_full_csv/counters_buffer_sizes.json"

    result_counter = {}

    process_ips_fpdns(ips, output_csv_path, result_counter)
    # print(result_counter)
    write_to_json(result_counter, output_json_path)
