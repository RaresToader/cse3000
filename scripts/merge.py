import pandas as pd


def merge_dataframes(file_1, file_2):
    """
    Merges two dataframes based on IP and saves the result to a CSV.
    :param: file_1 - the first input file path
    :param: file_2 - the second input file path
    :returns: None
    """
    file1 = pd.read_csv(file_1)  # ip and version / buffersize
    file2 = pd.read_csv(file_2)  # ip and baf

    file1 = file1.drop_duplicates(subset=['IP'])
    file2 = file2.drop_duplicates(subset=['IP'])

    merged_df = pd.merge(file1, file2, on='IP', how='inner')

    # merged_df['Version'].fillna('No buffer size found', inplace=True)
    merged_df['Vendor'].fillna('None', inplace=True)
    merged_df['Product'].fillna('None', inplace=True)
    # merged_df['BAF'].fillna(0, inplace=True)

    merged_df.to_csv('../data/censys_full_csv/dns_SL_results_vendor_product.csv', index=False)


def merge_ntp_results(files):
    """
    Merges the results from the four private mode NTP queries. 
    :param: files - a list with four file paths, corresponding to each query. 
    :returns: None
    """
    combined_df = pd.DataFrame()
    for file in files:
        df = pd.read_csv(file)
        combined_df = pd.concat([combined_df, df])

    max_baf_df = combined_df.groupby('IP', as_index=False).max()
    max_baf_df.to_csv('../data/censys_full_csv/ntp_merged_all_results.csv', index=False)


if __name__ == '__main__':
    merge_dataframes('../data/censys_full_csv/dns_SL_tld_any_results.csv', '../data/censys_full_csv/all_dns_plus_vendor_product.csv')
