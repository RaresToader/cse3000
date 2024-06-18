import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# File paths
DNS_EU_RESULTS = '../data/censys_full_csv/dns_filtered_eu_cctld_results.csv'
DNS_SL_RESULTS = '../data/censys_full_csv/dns_SL_tld_any_results.csv'
DNS_ROOT_RESULTS = '../data/censys_full_csv/dns_VE_tld_any_results.csv'
NTP_RESULTS = '../data/censys_full_csv/ntp_merged_all_results.csv'
SL_BUFFER_SIZE_BAF = '../data/censys_full_csv/SL_buffer_size_plus_BAF.csv'
SL_VERSION_BAF = '../data/censys_full_csv/SL_version_plus_BAF.csv'

COMPARISON_FILE_PATHS = [DNS_EU_RESULTS, DNS_SL_RESULTS, DNS_ROOT_RESULTS]

# Directory for saving plots
SAVE_DIR = './histograms_barplots/'


def read_and_filter_data(file_path, filter_column, filter_value):
    """
    Reads data from CSV file and filters data based on filter column.
    :param file_path: the input file path
    :param filter_column: the column to filter
    :param filter_value: the value based on which to filter
    :return: the updated data
    """
    data = pd.read_csv(file_path)
    return data[data[filter_column] > filter_value]


def save_plot(fig, file_name):
    """
    Helper function to save the plot.
    :param fig: the figure to save
    :param file_name: the path to save the plot to
    :return: None
    """
    file_path = f"{SAVE_DIR}{file_name}"
    fig.write_image(file_path)


def generate_histogram_buffer_sizes(output_path='SL_buffer_size_histogram.png'):
    """
    Generates a histogram of BAF for the SL ANY query (frequency on the y-axis, BAF ranges as bins on x-axis).
    :return: None
    """
    data = pd.read_csv(SL_BUFFER_SIZE_BAF)
    data['Buffer Size'] = pd.to_numeric(data['Buffer Size'], errors='coerce')
    filtered_data = data[data['BAF'] > 1]
    mean_baf_per_buffer_size = filtered_data.groupby('Buffer Size')['BAF'].mean().reset_index()
    mean_baf_per_buffer_size = mean_baf_per_buffer_size.sort_values(by='BAF', ascending=False)

    fig = px.bar(mean_baf_per_buffer_size, x='Buffer Size', y='BAF',
                 labels={'Buffer Size': 'EDNS0 Buffer Size (IP Count)', 'BAF': 'Mean BAF'},
                 text_auto=True, )

    fig.update_layout(xaxis=dict(type='category', title_font=dict(size=24), tickfont=dict(size=20)),
                      yaxis=dict(title_font=dict(size=24), tickfont=dict(size=20)), bargap=0.2)
    fig.update_traces(marker_color='dodgerblue', textfont=dict(size=16))
    save_plot(fig, output_path)


def generate_comparison_histograms(width=1500, height=1500):
    """
    Generates a comparison between histograms.
    :param width: the width of the plot
    :param height: the height of the plot
    :return: None
    """
    colors = ['dodgerblue', 'tomato', 'forestgreen']
    names = ['EU', 'SL', 'VE']
    fig = go.Figure()

    for i, file_path in enumerate(COMPARISON_FILE_PATHS):
        data = read_and_filter_data(file_path, 'BAF', 1)
        fig.add_trace(go.Histogram(
            x=data['BAF'],
            nbinsx=15,
            opacity=1,
            name=names[i],
            marker=dict(color=colors[i % len(colors)]),
            # texttemplate='%{y}',
            # textposition='outside',
            # textfont=dict(size=16)
        ))

    fig.update_layout(
        barmode='group',
        xaxis_title='BAF',
        yaxis_title='Frequency',
        xaxis=dict(title_font=dict(size=64, family='Arial Black'), tickfont=dict(size=64, family='Arial Black'), tickvals=[i for i in range(0, 151, 10)],
                   ticktext=[str(i) for i in range(0, 151, 10)]),
        yaxis=dict(title_font=dict(size=64, family='Arial Black'), tickfont=dict(size=64, family='Arial Black'
                                                                                                 )),
        width=width, height=height,
        legend=dict(title='TLD Domain', font=dict(size=60, family='Arial Black'), bordercolor='black', borderwidth=1,
                    x=0.99,
                    y=0.99,
                    xanchor='right',
                    yanchor='top',
                    itemsizing='constant',
                    ),
    )
    fig.update_traces(marker_line_width=4, selector=dict(type='histogram'))

    save_plot(fig, 'dns_histogram_comparison.png')


def generate_barplot_ntp():
    """
    Generates a barplot of NTP results.
    :return: None
    """
    data = pd.read_csv(NTP_RESULTS)
    data['BAF'] = pd.to_numeric(data['BAF'], errors='coerce')
    data = data.dropna(subset=['BAF'])

    value_counts = data['BAF'].value_counts().sort_index().reset_index()
    value_counts.columns = ['BAF', 'Frequency']

    fig = px.bar(value_counts, x='BAF', y='Frequency',
                 labels={'BAF': 'BAF', 'Frequency': 'Frequency'},
                 text_auto=True)
    fig.update_traces(marker_color='dodgerblue', textfont=dict(size=16))
    fig.update_layout(xaxis=dict(type='category', title_font=dict(size=24), tickfont=dict(size=20)),
                      yaxis=dict(title_font=dict(size=24), tickfont=dict(size=20)), bargap=0.2)
    save_plot(fig, 'ntp_hist_merged_results.png')


def generate_histogram(data, x_column, nbins, color, x_title, y_title, file_name):
    """
    Helper function to generate a histogram.
    :param data: the data to plot
    :param x_column: the column that contains the x-axis
    :param nbins: number of bins
    :param color: the color
    :param x_title: the OX title
    :param y_title: the OY title
    :param file_name: the path to save the plot to
    :return: None
    """
    fig = go.Figure(data=[go.Histogram(
        x=data[x_column],
        nbinsx=nbins,
        opacity=1,
        texttemplate='%{y}',
        textposition='outside',
        marker=dict(color=color),
        textfont=dict(size=14)

    )])
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        xaxis=dict(tickvals=[i for i in range(0, 151, 10)], ticktext=[str(i) for i in range(0, 151, 10)])
    )
    fig.update_layout(
        xaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
        yaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
        width=1000, height=500
    )

    save_plot(fig, file_name)


def generate_histogram_dns_sl():
    """
    Generates a histogram of DNS SL results.
    :return: None
    """
    non_labeled_dns_resolvers = read_and_filter_data(DNS_SL_RESULTS, 'BAF', 1)
    authoritative_data = read_and_filter_data('../data/results/dns_auth_max_baf.csv', 'BAF', -1)

    authoritative_ips = set(authoritative_data['IP'])
    non_labeled_dns_resolvers = non_labeled_dns_resolvers[~non_labeled_dns_resolvers['IP'].isin(authoritative_ips)]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=non_labeled_dns_resolvers['BAF'],
        nbinsx=15,
        opacity=0.75,
        marker=dict(color='dodgerblue'),
        name='Non-authoritative DNS'
    ))

    fig.add_trace(go.Histogram(
        x=authoritative_data['BAF'],
        nbinsx=15,
        opacity=0.75,
        marker=dict(color='orange'),
        name='Authoritative DNS'
    ))

    fig.update_layout(
        barmode='overlay',
        xaxis_title='BAF',
        yaxis_title='Frequency',
        xaxis=dict(tickvals=[i for i in range(0, 151, 10)], ticktext=[str(i) for i in range(0, 151, 10)]),
        yaxis=dict(title_font=dict(size=60, family='Arial Black'), tickfont=dict(size=60, family='Arial Black')),
        width=1300, height=1300,
        legend=dict(
            font=dict(size=60, family='Arial Black'),
            x=0, y=1,
            xanchor='left',
            yanchor='top'
        )
    )
    fig.update_layout(
        xaxis=dict(title_font=dict(size=60, family='Arial Black'), tickfont=dict(size=60, family='Arial Black')))

    save_plot(fig, 'dns_sl_histogram_incl_auth3.png')


def generate_bar_plot_fingerprinted():
    """
    Generetes a barplot of BAF per version.
    :return: None
    """
    data = pd.read_csv(SL_VERSION_BAF)
    filtered_data = data[~data['Version'].isin(['No match found', 'TIMEOUT'])]
    df_mean_baf = filtered_data.groupby('Version', as_index=False)['BAF'].mean()
    top_5_versions = df_mean_baf.sort_values(by='BAF', ascending=False).head(5)

    fig = px.bar(top_5_versions, x='Version', y='BAF', color='Version',
                 color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(
        xaxis=dict(showticklabels=False, title_font=dict(size=32), tickfont=dict(size=28)),
        yaxis=dict(title_font=dict(size=32), tickfont=dict(size=28)),
        legend=dict(font=dict(size=24), bordercolor='black', borderwidth=1,
                    x=0.99,
                    y=0.99,
                    xanchor='right',
                    yanchor='top',
                    ),
        width=2200,
        height=1000
    )
    save_plot(fig, 'SL_mean_baf_fingerprint_hist_top_5.png')


if __name__ == '__main__':
    generate_comparison_histograms()
