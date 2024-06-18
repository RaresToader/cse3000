import subprocess
import csv


def read(file_path):
    """
    Reads TLDs from a file.
    :param file_path: path to the file containing TLDs (one TLD per row)
    :return: list of TLDs
    """
    with open(file_path, 'r') as file:
        tlds = file.read().splitlines()
    return tlds


def find_msg_size(tld):
    """
    Runs the dig command on the given TLD to retrieve the MSG SIZE.
    :param tld: the top-level domain
    :return: the message size if found, otherwise None
    """
    try:
        command = ['dig', '@8.8.8.8', tld, 'ANY']
        result = subprocess.check_output(command, text=True)

        for line in result.split('\n'):
            if 'MSG SIZE  rcvd:' in line:
                msg_size = line.split('MSG SIZE  rcvd:', 1)[1].strip()
                return msg_size
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running dig for {tld}: {str(e)}")
        return None


def process_ips(inputs, output_csv_path, process_function, input_type = 'IP'):
    """
    Processes the given list of TLDs, retrieving the message size for each one.
    :param inputs: the given list of TLDs / or IP addresses
    :param output_csv_path: the output CSV file path
    :param process_function: the function to process the input (IP or TLD)
    :param input_type: the input type (IP or TLD)
    :return: nothing
    """
    with open(output_csv_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([input_type, 'System'])
        init_size = len(inputs)
        for i in range(len(inputs)):
            cur = inputs[i]
            msg_size = process_function(cur)
            if msg_size is None:
                msg_size = "None"
            csv_writer.writerow([cur, msg_size])

            if i % 30 == 0:
                print(f"Processed {i}/{init_size}")


# Read the data from the CSV

def sort_and_save_tlds(input_csv_path, output_csv_path):
    """
    Sorts and saves TLDs based on the BAF achieved.
    :param: input_csv_path: input file path
    :param: output_csv_path: output file path
    :returns: None
    """
    data = []
    with open(input_csv_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # print(row[1])
            if(row[1] == 'None'):
                data.append([row[0], 0])
            else:
                data.append([row[0], int(row[1])])

    for row in data:
        tld = row[0]
        msg_size = row[1]
        new_msg_size = msg_size / (29 + len(tld))  # Request size!!! => we actually compute the BAF
        row[1] = new_msg_size

    sorted_data = sorted(data, key=lambda x: x[1], reverse=True)

    with open(output_csv_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['TLD', 'Max BAF'])
        csv_writer.writerows(sorted_data)


def find_system(ip):
    """
    Runs the ntpq command on the given IP to retrieve the system information. (OS fingerprinting)
    :param ip: the IP address of the host running NTP)
    :return: the system information if found, otherwise None
    """
    try:
        command = ['ntpq', '-c', 'rv' , f'{ip}']
        result = subprocess.run(command, text=True, capture_output=True)

        for line in result.stdout.split('\n'):
            if 'system=' in line:
                system_info = line.split('system=', 1)[1].split(',')[0].replace('"', '').strip()
                return system_info
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running ntpq for {ip}: {str(e)}")
        return None



if __name__ == '__main__':
    sort_and_save_tlds("../data/tld/tlds_msg_sizes_google_resolver.csv", output_csv_path="../data/tld/tlds_sorted_google_dns.csv")
