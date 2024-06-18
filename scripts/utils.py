import csv
import json
import pandas as pd


def read_ips(csv_filename):
    """
    Reads IP addresses from a CSV file and returns a list of IP addresses.
    :param csv_filename: the name of the CSV file
    :return: the list of IP addresses read from the CSV file
    """
    with open(csv_filename, newline='') as csv_file:
        ip_reader = csv.reader(csv_file)
        return [row[0] for row in ip_reader]


def save_ips(data, filename, baf=False):
    """
    Saves the list of IP addresses (and potentially BAFs) to a CSV file.
    :param data: the filtered list of IP addresses
    :param filename: the name of the file where the IP addresses will be saved
    :param baf: whether there are BAFs to save
    :return: nothing
    """
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if baf:
            writer.writerow(['IP', 'BAF'])
            writer.writerows(data)
        else:
            # writer.writerow(['IP'])
            for row in data:
                writer.writerow([row])


def write_to_json(data, file_path):
    """
    Write the data (dict) into a JSON file.

    :param data: the data to write
    :param file_path: the output file path
    """
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def read_json(file_path):
    """
    Read nameservers and their corresponding domains from a JSON file.

    :param file_path: the path to the JSON file
    :return: a dictionary mapping nameservers to lists of domains they are authoritative for
    """
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data


def read_domains_from_csv(file_path):
    """
    Read domains from a CSV file.
    :param file_path: Path to the CSV file containing domain names.
    :return: List of domain names.
    """
    with open(file_path, newline='') as csv_file:
        domain_reader = csv.reader(csv_file)
        return [row[0] for row in domain_reader]


def process_json_files(input_file, output_csv):
    """
    Extract Censys information about DNS/NTP servers.
    :param input_file: the path to the input file
    :param output_csv: the path to the output path
    :return: None
    """
    fieldnames = ["ip", "vendor", "product"]

    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        with open(input_file, 'r') as json_file:
            data = json.load(json_file)

            for item in data:
                ip = item.get("ip", "None")
                vendor = item.get("operating_system", {}).get("vendor", "None")
                product = item.get("operating_system", {}).get("product", "None")

                writer.writerow({
                    "IP": ip,
                    "Vendor": vendor,
                    "Product": product
                })


def print_unique_values(csv_file_path, column_name):
    """
    Prints the unique values in a CSV file for a given column.
    :param csv_file_path: the path to the CSV file
    :param column_name:  the name of the column
    :return: None
    """
    df = pd.read_csv(csv_file_path)

    if column_name not in df.columns:
        print(f"Column '{column_name}' does not exist in the CSV file.")
        return

    unique_values = df[column_name].dropna().unique()
    if column_name.lower() != "none":
        print(f"Unique values in column '{column_name}':")
        for value in unique_values:
            print(value)
    else:
        print("Column name is 'None', no unique values to display.")


if __name__ == '__main__':
    print_unique_values('../data/censys_full_csv/all_dns_plus_vendor_product.csv', 'Product')
    # process_json_files('../data/censys_full/dns.json', '../data/censys_full_csv/all_dns_plus_vendor_product.csv')
