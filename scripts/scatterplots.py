import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import boxplots  # access to relevant paths!

SYMBOLS = [
    'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
    'triangle-left', 'triangle-right', 'pentagon', 'hexagon', 'star', 'star-square'
]

PLOTLY_COLORS = px.colors.qualitative.Plotly

FIGURE_DIMENSIONS = {
    'dns_scatter_buffer_size': (1000, 1000),
    'dns_scatter_version_restricted': (1800, 1200),
    'dns_scatter_version_all': (2600, 1800),
    'ntp_scatter': (1500, 1500),
    'network_scatter': (2000, 1000)
}


def load_data(file_path):
    """
    Load CSV data from the given file path.
    :param file_path: Path to the CSV file
    :returns the read dataframe
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return pd.DataFrame()


def filter_data(data, feature, min_baf=-1, exclude_values=None):
    """
    Filter data based on feature, minimum BAF, and exclude specific values.

    :param data: Data to filter
    :param feature: Feature to filter
    :param min_baf: Minimum baf
    :param exclude_values: Exclude values array
    :returns filtered data
    """
    if exclude_values is None:
        exclude_values = ['No match found', 'TIMEOUT', 'No buffer size found']

    filtered_data = data[~data[feature].isin(exclude_values)]
    filtered_data = filtered_data[filtered_data['BAF'] > min_baf]
    return filtered_data


def create_scatter_plot(data, feature, output_path, width, height, mincount_per_group=0):
    """
    Create and save a scatter plot.

    :param data: Data to plot
    :param feature: Feature to plot
    :param output_path: Output path for the scatter plot
    :param width: Width of the plot
    :param height: Height of the plot
    :mincount_per_group: Minimum count per group
    :returns None
    """
    version_counts = data[feature].value_counts()
    valid_versions = version_counts[version_counts >= mincount_per_group].index
    filtered_data = data[data[feature].isin(valid_versions)]

    mean_baf_per_version = filtered_data.groupby(feature)['BAF'].mean().sort_values(ascending=False)
    sorted_valid_versions = mean_baf_per_version.index

    fig = go.Figure()

    for i, version in enumerate(sorted_valid_versions):
        version_data = filtered_data[filtered_data[feature] == version]
        version_label = f"{int(float(version)) if ((not (isinstance(version, str))) and isinstance(float(version), float)) else version} ({version_counts[version]})"
        fig.add_trace(go.Scatter(
            y=version_data['BAF'],
            x=[version_label] * len(version_data),
            mode='markers',
            name=int(float(version)) if (
                        (not (isinstance(version, str))) and isinstance(float(version), float)) else version,
            marker=dict(
                color=PLOTLY_COLORS[valid_versions.tolist().index(version) % len(PLOTLY_COLORS)],
                symbol=SYMBOLS[i % len(SYMBOLS)], size=18
            )
        ))

    fig.update_layout(
        xaxis=dict(title=feature, showticklabels=True, title_font=dict(size=36),
                   tickfont=dict(size=30), ),
        yaxis=dict(title="BAF", title_font=dict(size=36),
                   tickfont=dict(size=30), ),
        legend=dict(font=dict(size=24), x=0.99, y=0.99, xanchor='right', yanchor='top'),
        width=width,
        height=height,
    )

    fig.write_image(output_path)


def dns_scatter_plot(output_path, file_path=boxplots.SL_version, feature="Version",
                     dns_dimensions="dns_scatter_version_all"):
    """
    Create and save a scatter plot.
    :param output_path: the output path for the scatter plot
    :param file_path: the input file path
    :param feature: the feature that is considered
    :param dns_dimensions: the dimensions of figure
    :return: None
    """
    data = load_data(file_path)
    filtered_data = filter_data(data, feature)
    create_scatter_plot(filtered_data, feature, output_path, *FIGURE_DIMENSIONS[dns_dimensions])


def ntp_scatter_plots(input_path_with_os, amplification_files, output_path):
    """
    Create and save a scatter plot with NTP BAF per OS.
    :param input_path_with_os: input files with IPs and OSs
    :param amplification_files: the files that have the IPs plus the results.
    :param output_path: where the scatter plot will be saved
    :return: None
    """
    df_system = load_data(input_path_with_os)

    dfs_amplification = []
    for file, label in amplification_files:
        df = load_data(file)
        df['Query Strategy'] = label
        dfs_amplification.append(df)

    df_combined = pd.concat(dfs_amplification)
    df_max_amplification = df_combined.groupby(['IP', 'Query Strategy'], as_index=False)['BAF'].max()
    df_merged = pd.merge(df_system, df_max_amplification, on="IP")

    df_merged['System'] = df_merged['System'].replace('FreeBSDJNPR', 'FreeBSD')

    df_filtered = df_merged[(df_merged['System'] != 'None') & (df_merged['BAF'] >= 0)]

    count_per_group = df_filtered.groupby('System').size().reset_index(name='Count')
    df_filtered = pd.merge(df_filtered, count_per_group, on='System')
    df_filtered['System'] = df_filtered['System'] + ' (' + df_filtered['Count'].astype(str) + ')'

    fig = px.scatter(df_filtered, x='System', y='BAF', color='Query Strategy', symbol='Query Strategy',
                     labels={'System': 'Operating System', 'BAF': 'BAF'},
                     category_orders={'Query Strategy': ['monlist', 'peer list', 'peer list sum', 'get restrict']})

    fig.update_traces(marker=dict(size=40))

    fig.update_layout(
        xaxis=dict(
            title=dict(font=dict(size=66, family='Arial Black')),
            tickfont=dict(size=66, family='Arial Black'),
            tickangle=70
        ),
        yaxis=dict(
            title=dict(font=dict(size=66, family='Arial Black')),
            tickfont=dict(size=66, family='Arial Black')
        ),
        legend=dict(font=dict(size=70, family='Arial Black'),
                    itemsizing='constant',
                    x=0.99,
                    y=0.99,
                    xanchor='right',
                    yanchor='top',
                    bgcolor='rgba(255, 255, 255, 0.3)',
                    ),
        width=FIGURE_DIMENSIONS['ntp_scatter'][0],
        height=FIGURE_DIMENSIONS['ntp_scatter'][1],
        # tickangle=-90
    )

    fig.write_image(output_path)


def scatter_plot_network_info(output_path, file_path=boxplots.SL_network_info):
    """
    Create and save a scatter plot with Network Info vs BAF for DNS hosts.
    :param output_path: the output path for the scatter plot
    :param file_path: the input files with IPs and network info
    :return: None
    """
    df = load_data(file_path)
    df = df[df['BAF'] > 1]

    asn_counts = df['asn'].value_counts()
    df_filtered = df[df['asn'].isin(asn_counts[asn_counts >= 10].index)]
    mean_baf = df_filtered.groupby('asn')['BAF'].mean().sort_values(ascending=False)

    fig = go.Figure()

    asn_descriptions = df_filtered[['asn', 'autonomous_system_description']].drop_duplicates().set_index('asn')

    for i, (asn, mean) in enumerate(mean_baf.items()):
        asn_data = df_filtered[df_filtered['asn'] == asn]
        asn_description = asn_descriptions.loc[asn, 'autonomous_system_description']
        fig.add_trace(go.Scatter(
            y=asn_data['BAF'],
            x=[asn] * len(asn_data),
            mode='markers',
            marker=dict(symbol=SYMBOLS[i % len(SYMBOLS)], color=PLOTLY_COLORS[i % len(PLOTLY_COLORS)], size=10),
            name=asn_description
        ))

    fig.update_layout(
        xaxis_title="ASN",
        yaxis_title="BAF",
        xaxis=dict(type='category', categoryorder='array', categoryarray=mean_baf.index.astype(str),
                   title=dict(font=dict(size=30)),
                   tickfont=dict(size=26)
                   ),
        yaxis=dict(title=dict(font=dict(size=30)),
                   tickfont=dict(size=26)),
        showlegend=True,
        width=FIGURE_DIMENSIONS['network_scatter'][0],
        height=FIGURE_DIMENSIONS['network_scatter'][1],
        legend=dict(font=dict(size=18),
                    itemsizing='constant',
                    x=0.99,
                    y=0.99,
                    xanchor='right',
                    yanchor='top',
                    ),
    )

    fig.write_image(output_path)


ntp_input_path_with_os = '../data/censys_full_csv/ntp_monlist_plus_system_processed.csv'
ntp_monlist_input_baf = '../data/censys_full_csv/ntp_filtered_monlist_results.csv'
ntp_peer_list_input_baf = '../data/censys_full_csv/ntp_filtered_monlist_peer_list_results.csv'
ntp_peer_list_sum_input_baf = '../data/censys_full_csv/ntp_filtered_monlist_peer_list_sum_results.csv'
ntp_get_restrict_input_baf = '../data/censys_full_csv/ntp_filtered_monlist_get_restrict_results.csv'

ntp_output_path_restricted = './ntp_scatterplots/ntp_systems_processed.png'
ntp_output_path_all = './ntp_scatterplots/ntp_systems_processed_all.png'

SL_network_scatterplot_restricted = './network_info/SL_scatterplot_restricted.png'

SL_buffer_size_output_restricted = './buffersize_scatterplots/SL_scatterplot_restricted.png'
SL_buffer_size_output_all = './buffersize_scatterplots/SL_scatterplot_all.png'

SL_version_output_restricted = './fingerprint_scatterplots/SL_scatterplot_restricted.png'
SL_version_output_all = './fingerprint_scatterplots/SL_scatterplot_all.png'

if __name__ == '__main__':
    ntp_scatter_plots(
        ntp_input_path_with_os,
        [
            (ntp_monlist_input_baf, "Monlist"),
            (ntp_peer_list_input_baf, "Peer List"),
            (ntp_peer_list_sum_input_baf, "Peer List Sum"),
            (ntp_get_restrict_input_baf, "Get Restrict")
        ],
        ntp_output_path_all
    )
