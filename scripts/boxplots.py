import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Define important paths do data sources

# => DNS host BAF + Buffer Size input paths
SL_buffer_size = '../data/censys_full_csv/SL_buffer_size_plus_BAF.csv'
EU_buffer_size = '../data/censys_full_csv/EU_buffer_size_plus_BAF.csv'
root_buffer_size = '../data/censys_full_csv/dns_results_plus_buffer_sizes.csv'


# => DNS host BAF + Buffer Size output paths
SL_buffer_size_output_restricted = './buffersize_boxplots/SL_boxplot_restricted.png'
EU_buffer_size_output_restricted = './buffersize_boxplots/EU_boxplot_restricted.png'
root_buffer_size_output_restricted = './buffersize_boxplots/ROOT_boxplot_restricted.png'

SL_buffer_size_output_all = './buffersize_boxplots/SL_boxplot_all.png'
EU_buffer_size_output_all = './buffersize_boxplots/EU_boxplot_all.png'
root_buffer_size_output_all = './buffersize_boxplots/ROOT_boxplot_all.png'

# => DNS host BAF + Version input paths
SL_version = '../data/censys_full_csv/SL_version_plus_BAF.csv'
EU_version = '../data/censys_full_csv/EU_version_plus_BAF.csv'
root_version = '../data/censys_full_csv/dns_results_plus_fingerprint.csv'


# => DNS host BAF + Version output paths
SL_version_output_restricted = './fingerprint_boxplots/SL_boxplot_restricted.png'
EU_version_output_restricted = './fingerprint_boxplots/EU_boxplot_restricted.png'
root_version_output_restricted = './fingerprint_boxplots/ROOT_boxplot_restricted.png'

SL_version_output_all = './fingerprint_boxplots/SL_boxplot_all.png'
EU_version_output_all = './fingerprint_boxplots/EU_boxplot_all.png'
root_version_output_all = './fingerprint_boxplots/ROOT_boxplot_all.png'

SL_vendor_output_restricted = './fingerprint_boxplots/SL_vendor_boxplot_restricted.png'
SL_vendor_output_all = './fingerprint_boxplots/SL_vendor_boxplot_all_group_size>10.png'

SL_product_output_restricted = './fingerprint_boxplots/SL_product_boxplot_restricted.png'
SL_product_output_all = './fingerprint_boxplots/SL_product_boxplot_all_group_size>10.png'


# => DNS host + information boxplot input paths
SL_network_info = '../data/censys_full_csv/network_info_dns/sl_all_info.csv'
EU_network_info = '../data/censys_full_csv/network_info_dns/eu_all_info.csv'
root_network_info = '../data/censys_full_csv/network_info_dns/root_all_info.csv'
SL_vendor_product_info = '../data/censys_full_csv/dns_SL_results_vendor_product.csv'


# => DNS host + information boxplot output paths
SL_network_info_output_restricted = './network_info/SL_boxplot_restricted.png'
EU_network_info_output_restricted = './network_info/EU_boxplot_restricted.png'
Root_network_info_output_restricted = './network_info/ROOT_boxplot_restricted.png'

SL_network_info_output_all = './network_info/SL_boxplot_all.png'
EU_network_info_output_all = './network_info/EU_boxplot_all.png'
Root_network_info_output_all = './network_info/ROOT_boxplot_all.png'

# => DNS host + buffersize/fingerprint combined output paths
SL_combined_buffer_size_restricted = './combined_plots_buffer_sizes/SL_combined_plot_restricted.png'
SL_combined_buffer_size_all = './combined_plots_buffer_sizes/SL_combined_plot_all.png'
SL_combined_version_restricted = './combined_plots_fingerprints/SL_combined_plot_restricted.png'
SL_combined_version_all = './combined_plots_fingerprints/SL_combined_plot_all.png'



def box_plot(feature="Version", input_path=SL_version,
             output_path=SL_version_output_restricted,
             width=1400, height=1400):
    """
    Creates and saves a boxplot of DNS Version/ Buffer Size against BAF.

    :param feature: the feature we are going to plot the boxplot for
    :param input_path: the input csv file path
    :param output_path: the output png file path
    :param width: the width of the boxplot
    :param height: the height of the boxplot
    :return: void
    """
    data = pd.read_csv(input_path)

    filtered_data = data[~data[feature].isin(['No match found', 'TIMEOUT', 'No buffer size found'])]
    filtered_data = filtered_data[filtered_data['BAF'] > 1]  # Filter to only keep records with BAF > 1

    # cleansing data => we only keep versions / buffer size records that have a count of >= 10

    if feature == "Version":
        filtered_data[feature] = filtered_data[feature].str.replace(r'\s*\[Old Rules\]|\s*\[New Rules\]', '',
                                                                    regex=True)
    version_counts = filtered_data[feature].value_counts()
    valid_versions = version_counts[version_counts >= 14].index
    filtered_data = filtered_data[filtered_data[feature].isin(valid_versions)]

    mean_baf_per_version = filtered_data.groupby(feature)['BAF'].mean().sort_values(ascending=False)
    sorted_valid_versions = mean_baf_per_version.index

    fig = go.Figure()
    version_labels = {}
    short_version_map = {}  # Map to hold short to full version mappings for legend

    for i, version in enumerate(sorted_valid_versions):
        version_data = filtered_data[filtered_data[feature] == version]

        color = px.colors.qualitative.Plotly[
            valid_versions.tolist().index(version) % len(px.colors.qualitative.Plotly)]
        participant_count = len(version_data)
        short_version = version[:3]

        words = version.split()
        if len(words) >= 2:
            version = ' '.join(words[:2])

        legend_label = f"{short_version};{version} ({participant_count})"
        version_labels[short_version] = legend_label
        short_version_map[short_version] = version

        fig.add_trace(go.Box(
            y=version_data['BAF'],
            x=[short_version] * len(version_data),  # Short names for x-axis
            name=legend_label,  # Full names for legend
            boxmean=True,  # show mean
            marker=dict(color=color, opacity=0.8, size=18),  # Larger outliers
            line=dict(color=color, width=5)  # Thicker line for the box outline
        ))
    # print(version_labels.keys())
    fig.update_layout(
        xaxis=dict(
            title=feature,
            title_font=dict(size=70, family='Arial Black'),
            tickfont=dict(size=70, family='Arial Black'),
            tickmode='array',
            tickvals=list(short_version_map.keys()),
            ticktext=list(short_version_map.keys()),
            tickangle=-270  # Make the labels vertical
        ),
        yaxis=dict(
            title="BAF",
            title_font=dict(size=70, family='Arial Black'),
            tickfont=dict(size=70, family='Arial Black'),
        ),
        legend=dict(
            font=dict(
                size=54, family='Arial Black'
            ),
            itemsizing='constant',
            # itemwidth=40,  # Increase the width of legend items
            x=1.4,  # X position of the legend
            y=0.99,  # Y position of the legend
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.7)'
        ),
        width=width,
        height=height,
    )

    # for trace in fig['data']:
    #     if trace['showlegend']:
    #         trace['name'] = version_labels[trace['name']]

    fig.write_image(output_path)
def box_plot_network_info(input_path=SL_network_info,
                          output_path=SL_network_info_output_restricted,
                          width=1500,
                          height=1500, short_legend=True):
    """
    Creates and saves of network info against BAF.
    :param input_path: the input path to the network_info csv file
    :param output_path: the output path to the network_info png file
    :param width: the width of the network_info png
    :param height: the height of the network_info png
    :return: void
    """
    df = pd.read_csv(input_path)
    df = df[df['BAF'] > 1]

    asn_counts = df['asn'].value_counts()
    df_filtered = df[df['asn'].isin(asn_counts[asn_counts >= 10].index)]

    mean_baf = df_filtered.groupby('asn')['BAF'].mean().sort_values(ascending=False)
    top_asns = mean_baf.head(5).index
    df_filtered = df_filtered[df_filtered['asn'].isin(top_asns)]
    mean_baf = mean_baf.head(5)

    fig = go.Figure()

    asn_descriptions = df_filtered[['asn', 'autonomous_system_description']].drop_duplicates()
    asn_descriptions = asn_descriptions.set_index('asn')
    tick_labels = []

    for i, asn in enumerate(mean_baf.index):
        asn_data = df_filtered[df_filtered['asn'] == asn]
        asn_description = asn_descriptions.loc[asn, 'autonomous_system_description']
        ip_count = len(asn_data)
        tick_labels.append(f"{int(asn)} ({ip_count})")

        if short_legend:
            asn_description = asn_description.split()[0]

        fig.add_trace(go.Box(
            y=asn_data['BAF'],
            x=[asn] * len(asn_data),
            name=asn_description,
            boxmean=True,
            marker=dict(color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)], opacity=0.8, size = 18),
            line=dict(color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)], width=5)
            # marker=dict(color=color, opacity=0.8, size=18),  # Larger outliers
            # line=dict(color=color, width=5)  # Thicker line for the box outline
        ))

    fig.update_layout(
        xaxis_title="ASN",
        yaxis_title="BAF",
        xaxis=dict(type='category', categoryorder='array', categoryarray=mean_baf.index.astype(str),
                   title_font=dict(size=80, family='Arial Black'),
                   tickfont=dict(size=80, family='Arial Black'),
                   tickvals=mean_baf.index,
                   ticktext=tick_labels,
                   ),
        yaxis=dict(title_font=dict(size=80, family='Arial Black'),
                   tickfont=dict(size=80, family='Arial Black'),
                   ),
        showlegend=True,
        width=width,
        height=height,
        legend = dict(
            font=dict(
                size=80,
                family='Arial Black'
            ),
        itemsizing='constant',
        x=0.01,
        y=0.01,
        xanchor='left',
        yanchor='bottom',
        bgcolor='rgba(255, 255, 255, 0.6)'
        ),
    )

    fig.write_image(output_path)

def combined_plot(feature="Buffer Size", input_path=SL_buffer_size, output_path=SL_combined_buffer_size_restricted,
                  width=1600, height=1600):
    """
    Creates and saves a combined plot (scatter plot + box plot) for DNS hosts.
    :param feature: the feature to be considered
    :param input_path: the path to the input file
    :param output_path: the output path to the combined plot
    :param width: the width of the plot
    :param height: the height of the plot
    :return: void
    """
    data = pd.read_csv(input_path)
    filtered_data = data[~data[feature].isin(['No match found', 'TIMEOUT', 'No buffer size found'])]
    filtered_data = filtered_data[filtered_data['BAF'] > 1]  # Filter to only keep records with BAF > 1

    version_counts = filtered_data[feature].value_counts()
    valid_versions = version_counts[version_counts >= 10].index
    filtered_data = filtered_data[filtered_data[feature].isin(valid_versions)]

    mean_baf_per_version = filtered_data.groupby(feature)['BAF'].mean().sort_values(ascending=False)
    top_5_versions = mean_baf_per_version.head(5).index
    filtered_data = filtered_data[filtered_data[feature].isin(top_5_versions)]

    symbols = [
        'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
        'triangle-left', 'triangle-right', 'pentagon', 'hexagon', 'star', 'star-square'
    ]

    fig = go.Figure()

    for i, version in enumerate(top_5_versions):
        version_data = filtered_data[filtered_data[feature] == version]
        version_label = f"{version} ({len(version_data)})"

        fig.add_trace(go.Scatter(
            y=version_data['BAF'],
            x=[version_label] * len(version_data),
            mode='markers',
            name=f'{version} Scatter',
            marker=dict(
                color=px.colors.qualitative.Plotly[
                    valid_versions.tolist().index(version) % len(px.colors.qualitative.Plotly)],
                symbol=symbols[i % len(symbols)],
                size=6,
                opacity=0.6
            ),
            showlegend=False
        ))
        fig.add_trace(go.Box(
            y=version_data['BAF'],
            name=f'{version_label} Box',
            marker_color=px.colors.qualitative.Plotly[
                valid_versions.tolist().index(version) % len(px.colors.qualitative.Plotly)],
            boxmean=True,  # show mean
            showlegend=True
        ))

    fig.update_layout(
        xaxis=dict(
            title=feature,
            showticklabels=True,
            title_font=dict(size=32),
            tickfont=dict(size=26),
        ),
        yaxis=dict(
            title="BAF",
            title_font=dict(size=32),
            tickfont=dict(size=26),
        ),
        legend=dict(
            font=dict(
                size=24
            ),
            itemsizing='constant',
            x=0.99,
            y=0.99,
            xanchor='right',
            yanchor='top',
        ),
        width=width,
        height=height,
    )
    fig.write_image(output_path)



if __name__ == '__main__':
    box_plot()
    # box_plot_network_info()