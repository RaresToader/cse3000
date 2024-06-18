import numpy as np
import pandas as pd
import plotly.graph_objects as go
import boxplots

SL_buffersize_output = './cdfs/SL_buffer_size_cdf.png'
SL_version_output = './cdfs/SL_version_cdf.png'

marker_symbols = ['circle', 'square', 'diamond', 'cross', 'x']


def generate_cdf_plots(feature='Version', input_path=boxplots.SL_version, output_path=SL_version_output,
                       height=1500,
                       width=1500):
    """
    Generates a CDF plot for a given feature (buffer size or version).
    :param feature: the feature being plotted
    :param input_path: the path of the input file
    :param output_path: the path of the output png
    :param height: the height of the plot
    :param width: the width of the plot
    :return: None
    """
    df = pd.read_csv(input_path)

    # Filter out rows with 'No buffer size found' if the feature is 'Buffer Size'
    if feature == 'Buffer Size':
        df = df[df['Buffer Size'] != 'No buffer size found']
    elif feature == 'Version':
        df = df[~df['Version'].isin(['TIMEOUT', 'No match found'])]
        df[feature] = df[feature].str.replace(r'\s*\[Old Rules\]|\s*\[New Rules\]', '', regex=True)
        df[feature] = df[feature].str.replace(r'\s*\[recursion enabled\]', ' [rec. en.]', regex=True)
    # Calculate mean BAF per feature and sort in descending order

    group_counts = df[feature].value_counts()
    valid_groups = group_counts[group_counts >= 10].index
    df = df[df[feature].isin(valid_groups)]

    version_means = df.groupby(feature)['BAF'].mean().sort_values(ascending=False)
    # Consider only the top 5 versions/buffer sizes
    top_versions = version_means.head(5).index
    top_data = df[df[feature].isin(top_versions)]

    fig = go.Figure()
    for i, version in enumerate(top_versions):
        # Sort BAF values and calculate the cumulative density
        version_data = top_data[top_data[feature] == version]['BAF'].sort_values()
        cdf = np.linspace(0, 1, len(version_data), endpoint=False)

        extended_version_data = np.insert(version_data.values, 0, version_data.values[0])
        extended_version_data = np.append(extended_version_data, version_data.values[-1])
        extended_cdf = np.insert(cdf, 0, 0)
        extended_cdf = np.append(extended_cdf, 1)

        count_per_group = len(version_data)
        legend_label = f"{int(float(version)) if feature == 'Buffer Size' else version} ({count_per_group})"

        fig.add_trace(go.Scatter(
            x=extended_version_data, y=extended_cdf,
            mode='lines+markers',
            name=legend_label,
            marker=dict(size=14, symbol=marker_symbols[i % len(marker_symbols)]),
            line=dict(width=18)
        ))

    fig.update_layout(
        xaxis_title='BAF',
        yaxis_title='CDF',
        yaxis=dict(tickformat=".0%", title_font=dict(size=72, family='Arial Black'),
                   tickfont=dict(size=72, family='Arial Black'), ),
        xaxis=dict(tickfont=dict(size=72, family='Arial Black'), title_font=dict(size=72, family='Arial Black'), ),
        legend_title=f"{feature} (IP Count)",
        height=height,
        width=width,
        legend=dict(x=0.99, y=0.01, xanchor='right', yanchor='bottom', bordercolor='Black', borderwidth=1,
                    font=dict(size=60, family='Arial Black'), bgcolor='rgba(255,255,255,0.8)')
    )
    fig.write_image(output_path)


if __name__ == '__main__':
    generate_cdf_plots()
