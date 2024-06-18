import pandas as pd


def read_and_filter_json(data):
    """
    Reads and filter a dictionary.
    :param data: the dictionary
    :return: the filtered data.
    """
    all_values = []
    for ip, domains in data.items():
        for domain, value in domains.items():
            if value > 2:
                all_values.append(value)

    filtered_data = pd.DataFrame(all_values, columns=['BAF'])
    return filtered_data


def read_and_filter_data(file_path):
    """
    Reads and filters a data from a CSV file.
    :param file_path: the path to the CSV file.
    :return: the filtered data
    """
    data = pd.read_csv(file_path)
    filtered_data = data[data['BAF'] > -1]
    return filtered_data


def print_statistics(data, label, feature='Buffer Size', check_version_flag=True):
    """
    Prints statistics for a given protocol (label).
    :param data: the data
    :param label: the name of the protocol
    :param check_version_flag: to check which percentage of the top 250 hosts are Raiden DNSD or MikroTik
    :return: None
    """
    mean_val = data['BAF'].mean()
    var_val = data['BAF'].var()
    std_dev = data['BAF'].std()
    median_val = data['BAF'].median()
    max_val = data['BAF'].max()
    df_sorted = data.sort_values(by=['BAF'], ascending=False)
    top_50_percent_mean = df_sorted.head(int(len(df_sorted) * 0.5))['BAF'].mean()
    top_10_percent_mean = df_sorted.head(int(len(df_sorted) * 0.1))['BAF'].mean()
    top_250 = df_sorted.head(250)
    top_250_sum = top_250['BAF'].sum() if len(df_sorted) >= 250 else "Less than 250 values available"

    print(f"Statistics for {label}:")
    print(f"Mean: {mean_val}")
    print(f"Variance: {var_val}")
    print(f"Standard Deviation: {std_dev}")
    print(f"Median: {median_val}")
    print(f"Maximum: {max_val}")
    print(f"Mean of Top 50%: {top_50_percent_mean}")
    print(f"Mean of Top 10%: {top_10_percent_mean}\n")
    print(f"Sum of Top 250 values: {top_250_sum}\n")

    if check_version_flag and len(df_sorted) >= 250:
        versions_to_check = []
        if feature == "Version":
            versions_to_check.extend(["Mikrotik dsl/cable  [Old Rules]", "Raiden DNSD  [Old Rules]"])
        elif feature == 'asn':
            versions_to_check.extend([57794, 29247, 12361])
        elif feature == "Buffer Size":
            versions_to_check.extend(['4000.0', '4096.0'])

        # top_250_versions = top_250['Version'].value_counts()

        count_specific_versions = top_250[top_250[feature].isin(versions_to_check)].shape[0]
        other_versions = top_250[~top_250[feature].isin(versions_to_check)][feature].value_counts()

        print(f"Count of specific versions in Top 250: {count_specific_versions}")
        print("Counts of other versions in Top 250:")
        for version, count in other_versions.items():
            print(f"{version}: {count}")


def count_baf_ranges_dns(data):
    """
    Counts the BAF ranges for DNS servers. Important data for the piechart.
    :param data: the DNS data
    :return: None
    """
    ranges = {
        "<=2": (data['BAF'] <= 2).sum(),
        ">2 and <=20": ((data['BAF'] > 2) & (data['BAF'] <= 20)).sum(),
        ">20 and <=50": ((data['BAF'] > 20) & (data['BAF'] <= 50)).sum(),
        ">50 and <=80": ((data['BAF'] > 50) & (data['BAF'] <= 80)).sum(),
        ">80": (data['BAF'] > 80).sum(),
    }
    print("Number of hosts in each BAF range (DNS):")
    for key, count in ranges.items():
        print(f"{key}: {count}")


def count_baf_ranges_ntp(data):
    """
       Counts the BAF ranges for NTP servers. Important data for the piechart.
       :param data: the NTP data
       :return: None
       """
    ranges = {
        "<2": (data['BAF'] < 2).sum(),
        ">=2 and <20": ((data['BAF'] >= 2) & (data['BAF'] < 20)).sum(),
        ">=20": (data['BAF'] >= 20).sum(),
    }
    print("Number of hosts in each BAF range (NTP):")
    for key, count in ranges.items():
        print(f"{key}: {count}")


def main():
    input_file = input("Please enter the path to the input file: ")
    data1 = pd.read_csv(input_file)
    print_statistics(data1, 'DNS data')
    count_baf_ranges_dns(data1)


if __name__ == "__main__":
    main()

# ../data/censys_full_csv/SL_buffer_size_plus_BAF.csv
# ../data/censys_full_csv/SL_version_plus_BAF.csv
# ../data/censys_full_csv/network_info_dns/sl_all_info.csv