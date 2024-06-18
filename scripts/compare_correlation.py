import boxplots
import pandas as pd
import plotly.graph_objects as go




def load_and_filter_data(file_buffer_size=boxplots.SL_buffer_size, file_version=boxplots.SL_version,
                         file_asn=boxplots.SL_network_info,
                         file_vendor_product='../data/censys_full_csv/dns_SL_results_vendor_product.csv',
                         min_baf=-1,
                         which_pair=12):
    """
    Reads and processes Buffer Size(1) and Version data(2) and Network Info(3) for comparisons.
    :param file_buffer_size: the input file of IPs with Buffer Size.
    :param file_version: the input files of IPs with Version.
    :param file_asn: the input file of IPs with ASN data.
    :param file_vendor_product: the input files of IPs with Vendor Product info.
    :param which_pair: between which features to plot a heatmap

    :return: the filtered Dataframes as a tuple
    """
    df1 = pd.read_csv(file_buffer_size)
    df2 = pd.read_csv(file_version)
    df3 = pd.read_csv(file_asn)
    df4 = pd.read_csv(file_vendor_product)

    # Preprocess
    df1_filtered = df1[(df1['Buffer Size'] != 'No buffer size found') & (df1['BAF'] > min_baf)]
    df2_filtered = df2[(df2['Version'] != 'No match found') & (df2['Version'] != 'TIMEOUT') & (df2['BAF'] > min_baf)]
    df3_filtered = df3[df3['BAF'] > min_baf]
    choose = 'Vendor' if which_pair % 10 == 4 else 'Product'
    df4_filtered = df4[(df4[choose] != 'None') & (df4['BAF'] > min_baf)]

    # Keep only records with IPs that are in both files
    if which_pair == 12:
        common_ips = set(df1_filtered['IP']).intersection(set(df2_filtered['IP']))
    elif which_pair == 13:
        common_ips = set(df1_filtered['IP']).intersection(set(df3_filtered['IP']))
    elif which_pair == 23:
        common_ips = set(df2_filtered['IP']).intersection(set(df3_filtered['IP']))
    elif which_pair == 14:
        common_ips = set(df1_filtered['IP']).intersection(set(df4_filtered['IP']))
    elif which_pair == 15:
        common_ips = set(df1_filtered['IP']).intersection(set(df4_filtered['IP']))
    elif which_pair == 24:
        common_ips = set(df2_filtered['IP']).intersection(set(df4_filtered['IP']))
    elif which_pair == 25:
        common_ips = set(df2_filtered['IP']).intersection(set(df4_filtered['IP']))
    elif which_pair == 34:
        common_ips = set(df3_filtered['IP']).intersection(set(df4_filtered['IP']))
    elif which_pair == 35:
        common_ips = set(df3_filtered['IP']).intersection(set(df4_filtered['IP']))
    else:
        common_ips = set(df4_filtered['IP']).intersection(set(df4_filtered['IP']))

    df1_filtered = df1_filtered[df1_filtered['IP'].isin(common_ips)]
    df2_filtered = df2_filtered[df2_filtered['IP'].isin(common_ips)]
    df3_filtered = df3_filtered[df3_filtered['IP'].isin(common_ips)]
    df4_filtered = df4_filtered[df4_filtered['IP'].isin(common_ips)]

    return df1_filtered, df2_filtered, df3_filtered, df4_filtered


def filter_by_group_size(df, group_column, min_size=30):
    """
    Filters the DataFrame to only keep groups with a size greater than a specified minimum.
    :param df: The input DataFrame.
    :param group_column: The column to group by.
    :param min_size: The minimum size of groups to keep.
    :return: The filtered DataFrame.
    """
    group_counts = df[group_column].value_counts()
    valid_groups = group_counts[group_counts > min_size].index
    return df[df[group_column].isin(valid_groups)]


def top_10_percent_mean(series):
    """
    Computes the mean BAF of the top 10% of all BAFs.
    :param series: the input series.
    :return: the mean BAF of the top 10% of all BAFs.
    """
    top_10_percent = series.quantile(0.9)
    return series[series >= top_10_percent].mean()


def median(series):
    """
    Computes the median of the series.
    :param series: the input series
    :return: the median of the series.
    """
    median = series.quantile(0.5)
    return median


def analyze_correlation(df1, df2, df3, df4, feature1, feature2, which_pair=12):
    """
       Analyzes the correlation between two features.
       :param df1: DataFrame containing the first feature (buffer size).
       :param df2: DataFrame containing the second feature (version).
       :param df3: DataFrame containing the third feature (autonomous system).
       :param feature1: The first feature to correlate.
       :param feature2: The second feature to correlate.
       :param which_pair: between which features to plot a heatmap
       :return: A tuple of correlation DataFrames (counts and percentages).
   """
    # Merge the dataframes on IP
    if which_pair == 12:
        merged_df = pd.merge(df1, df2, on='IP')
    elif which_pair == 13:
        merged_df = pd.merge(df1, df3, on='IP')
    elif which_pair == 23:
        merged_df = pd.merge(df2, df3, on='IP')
    elif which_pair == 14 or which_pair == 15:
        merged_df = pd.merge(df1, df4, on='IP')
    elif which_pair == 24 or which_pair == 25:
        merged_df = pd.merge(df2, df4, on='IP')
    elif which_pair == 34 or which_pair == 35:
        merged_df = pd.merge(df3, df4, on='IP')
    else:
        merged_df = df4

    if feature2 == "Version":
        merged_df[feature2] = merged_df[feature2].str.replace(r'\s*\[Old Rules\]|\s*\[New Rules\]', '',
                                                              regex=True)
    elif feature1 == "Version":
        merged_df[feature1] = merged_df[feature1].str.replace(r'\s*\[Old Rules\]|\s*\[New Rules\]', '',
                                                              regex=True)

    # if which_pair // 10 == 1:        # if we are considering the buffer size
    #     merged_df[feature1] = merged_df[feature1].astype(float).astype(int)
        # print(merged_df[feature1])

    merged_df = filter_by_group_size(merged_df, feature1)
    merged_df = filter_by_group_size(merged_df, feature2)
    merged_df = filter_by_group_size(merged_df, feature1)

    # helper = merged_df.groupby([feature1, feature2])['BAF_x'].mean().unstack(fill_value=0)
    correlation_df = merged_df.groupby([feature1, feature2]).size().unstack(fill_value=0)
    # print(merged_df)
    # correlation_df_percentage = correlation_df.div(correlation_df.sum(axis=0), axis=1) * 100
    if which_pair == 45:
        merged_df = merged_df.rename(columns={'BAF': 'BAF_x'})

    correlation_df_percentage = merged_df.groupby([feature1, feature2])['BAF_x'].apply(median).unstack(
        fill_value=0)
    return correlation_df, correlation_df_percentage


def add_line_breaks(text, max_length=6):
    """
    Adds line breaks to the text. Used in the heatmap for "wrap-around" effect.
    :param text: the dataframe with the text
    :param max_length: determines when to split
    :return: the updated dataframe
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            current_line += " " + word
        else:
            lines.append(current_line.strip())
            current_line = word
    if current_line:
        lines.append(current_line.strip())
    return "<br>".join(lines)

def visualize_correlation(correlation_df, correlation_df_percentage, feature1, feature2):
    """
       Visualizes the correlation between two features (two of the three: Buffer Size/ Version / autonomous system description).
       :param correlation_df: DataFrame containing the counts of the correlations.
       :param correlation_df_percentage: DataFrame containing the percentages of the correlations.
       :param feature1: The first feature to correlate.
       :param feature2: The second feature to correlate.
   """
    feature2_totals = correlation_df.sum(axis=0)
    feature2_percentages = correlation_df.div(feature2_totals, axis=1) * 100

    annotation_df = correlation_df_percentage.copy()

    for col in annotation_df.columns:
        for row in annotation_df.index:
            count = correlation_df.at[row, col]
            percentage = feature2_percentages.at[row, col]
            median_baf = correlation_df_percentage.at[row, col]
            annotation_df.at[row, col] = f"{median_baf:.2f}\n({percentage:.1f}%)"

    # fig = px.imshow(correlation_df_percentage,
    #                 labels=dict(x=feature2, y=feature1, color="Median BAF"),
    #                 x=correlation_df_percentage.columns,
    #                 y=correlation_df_percentage.index,
    #                 text_auto=True,
    #                 color_continuous_scale=[(0, 'white'), (1, 'darkred')],
    #                 text=annotation_df)
    annotation_df_wrapped = annotation_df.applymap(lambda x: add_line_breaks(x, max_length=10))

    fig = go.Figure(data=go.Heatmap(
        z=correlation_df_percentage.values,
        x=correlation_df_percentage.columns.map(lambda x: x.split()[0]),
        y=correlation_df_percentage.index.astype(float).astype(int).astype(str),
        colorscale=[(0, 'white'), (1, 'darkred')],
        text=annotation_df_wrapped.values,
        textfont=dict(size=36, family='Arial Black'),
        # textangle=0,  # Keep the text horizontal, you can adjust this if needed
        # showscale=False,
        texttemplate="%{text}",
        hoverinfo="skip"
    ))

    fig.update_layout(
        xaxis_title=feature2,
        yaxis_title=feature1,
        height=1400,
        width=1400,
        font=dict(size=40, family='Arial Black'))

    # Add count annotations on the x-axis (e.g. for each version)
    for i, col in enumerate(correlation_df.columns):
        count = correlation_df[col].sum()
        fig.add_annotation(dict(
            font=dict(color="black", size=40, family='Arial Black'),
            x=i,
            y=len(correlation_df),
            showarrow=False,
            text=str(count),
            xanchor='center',
            yanchor='bottom',
            xref="x",
            yref="y"
        ))

    # Add count annotations on the y-axis (e.g. for each buffer size)
    for i, row in enumerate(correlation_df.index):
        count = correlation_df.loc[row].sum()
        fig.add_annotation(dict(
            font=dict(color="black", size=40, family='Arial Black'),
            x=-0.5,
            y=i,
            showarrow=False,
            text=str(count),
            xanchor='right',
            yanchor='middle',
            xref="x",
            yref="y"
        ))

    fig.show()
    fig.write_image(f'./compare_correlation/filtered_{feature1}_vs_{feature2}.png')


if __name__ == '__main__':
    df1, df2, df3, df4 = load_and_filter_data(which_pair=13)

    correlation_df, correlation_df_percentage = analyze_correlation(df1, df2, df3, df4, 'Buffer Size', 'autonomous_system_description',
                                                                    which_pair=13)
    visualize_correlation(correlation_df, correlation_df_percentage, 'Buffer Size', 'autonomous_system_description')

    # correlation_df, correlation_df_percentage = analyze_correlation(df1, df2, df3, 'Buffer Size',
    #                                                                 'autonomous_system_description', which_pair=13)
    # visualize_correlation(correlation_df, correlation_df_percentage, 'Buffer Size', 'autonomous_system_description')

    # correlation_df, correlation_df_percentage = analyze_correlation(df1, df2, df3, 'Version',
    #                                                                 'autonomous_system_description', which_pair=23)
    # visualize_correlation(correlation_df, correlation_df_percentage, 'Version', 'autonomous_system_description')


# Version against Product. (25)     Buffer Size against Product. (15)
# Buffer Size against Version. (12)  Buffer Size against AS. (13)



# 1 is Buffer Size
# 2 is Version (DNS Implementation)
# 3 is ASN
# 4 is Vendor
# 5 is Product (OS)
# 10 pairs => 20 plots (filtered + all)

# 12. Buffer Size vs Version [x]
# 13. Buffer Size vs AS [x]
# 14. Buffer Size vs Vendor [x]
# 15. Buffer Size vs Product [x]

# 23. Version vs ASN
# 24. Version vs Vendor [x]
# 25. Version vs Product [x]

# 34. ASN vs Vendor [x]
# 35. ASN vs Product [x]

# 45. Vendor vs Product [x]
