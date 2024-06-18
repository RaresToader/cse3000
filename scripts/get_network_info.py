import json
import csv


def get_network_info(json_all_info_path, input_csv_file_path, output_csv_file_path):
    """
    Retrieves the AS information from the Censys initial file.
    :param json_all_info_path: the output file from Censys.
    :param input_csv_file_path: the input CSV file path.
    :param output_csv_file_path: the output CSV file path.
    :return: None
    """
    with open(json_all_info_path, 'r') as json_file:
        json_data = json.load(json_file)

    ip_to_as_info = {}
    for entry in json_data:
        as_info = entry.get("autonomous_system", {})
        ip = entry.get("ip")
        if ip:
            ip_to_as_info[ip] = {
                "description": as_info.get("description"),
                "asn": as_info.get("asn")
            }

    with open(input_csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        data_rows = list(csv_reader)

    # Update CSV data with autonomous system details
    updated_rows = []
    headers.extend(['autonomous_system_description', 'asn'])
    for row in data_rows:
        ip = row[0]
        as_info = ip_to_as_info.get(ip, {})
        row.append(as_info.get("description", ""))
        row.append(as_info.get("asn", ""))
        updated_rows.append(row)

    # Save the updated CSV file
    with open(output_csv_file_path, 'w', newline='') as new_csv_file:
        csv_writer = csv.writer(new_csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(updated_rows)

    # print(f"Updated CSV file with AS information saved as {output_csv_file_path}")


if __name__ == '__main__':
    get_network_info('../data/censys_full/dns.json',
                     '../data/censys_full_csv/dns_SL_tld_any_results.csv',
                     '../data/censys_full_csv/network_info_dns/sl_all_info.csv')
