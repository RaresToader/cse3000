import plotly.graph_objects as go

dns_version_info = {
    "Mikrotik dsl/cable [Old Rules]": 319,
    "Simon Kelley dnsmasq [Old Rules]": 119,
    "No match found": 882,
    "Microsoft Windows DNS 2000 [New Rules]": 123,
    "Microsoft Windows DNS 2003 [New Rules]": 49,
    "Unlogic Eagle DNS 1.1.1 [New Rules]": 15,
    "sheerdns [Old Rules]": 1,
    "TIMEOUT": 235,
    "ISC BIND 9.6.3 -- 9.7.3 [New Rules]": 19,
    "Meilof Veeningen Posadis [Old Rules]": 125,
    "Microsoft Windows DNS 2003 R2 [New Rules]": 1,
    "Microsoft Windows DNS 2008 [New Rules]": 3,
    "ISC BIND 9.2.3rc1 -- 9.4.0a4 [Old Rules]": 30,
    "Unlogic Eagle DNS 1.0 -- 1.0.1 [New Rules]": 270,
    "Axis video server [Old Rules]": 2,
    "ISC BIND 9.2.0 -- 9.2.2-P3 [New Rules]": 1,
    "ISC BIND 9.2.3rc1 -- 9.4.0a4 [recursion enabled] [Old Rules]": 2,
    "Microsoft Windows DNS 2003 [Old Rules]": 1,
    "ATOS Stargate ADSL [Old Rules]": 15,
    "Raiden DNSD [Old Rules]": 148,
    "vermicelli totd [Old Rules]": 7,
    "VeriSign ATLAS [Old Rules]": 14,
    "ISC BIND 9.7.2 [New Rules]": 2,
    "ISC BIND 9.3.0 -- 9.3.6-P1 [New Rules]": 1,
    "ISC BIND 9.2.3 -- 9.2.9 [New Rules]": 7,
    "JHSOFT simple DNS plus [Old Rules]": 4,
    "NLnetLabs Unbound 1.4.10 -- 1.4.12 [New Rules]": 3
}


def create_pie_chart(labels, values, file_path, font_size=20, legend_title='Legend', width=800, height=800):
    """
    Creates and saves a pie chart with the given labels and values.

    :labels: list of labels for the pie chart segments
    :values: list of values corresponding to the labels
    :file_path: path to save the generated pie chart image
    :font_size: font size for the text inside the pie chart
    :legend_title: title for the legend
    :width: width of the chart
    :height: height of the chart
    :returns: None
    """
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        textinfo='label+percent+value',
        insidetextfont={'size': font_size, 'family':'Arial Black'}
    ))

    fig.update_layout(
        showlegend=True,
        legend_title_text=legend_title,
        font=dict(
            family="Arial Black",
            size=font_size,
            color="black"
        ),
        width=width,
        height=height
    )

    fig.write_image(file_path)


def generate_ntp_pie_chart(file_path):
    """
    Generates a pie chart for the distribution of NTP resolvers.
    :file_path: path to save the generated pie chart image
    :returns: None
    """
    labels = [
        'Closed NTP Hosts',
        'Did not respond to "monlist"',
        'BAF < 2',
        'BAF >= 2 and < 20',
        'BAF >= 20'
    ]
    values = [832, 24498, 564, 48, 20]

    create_pie_chart(labels, values, file_path, width=800, height=600)


def generate_dns_pie_chart(file_path):
    """
    Generates a pie chart for the distribution of DNS resolvers.
    :file_path: path to save the generated pie chart image
    :returns: None
    """
    labels = [
        'Closed DNS Resolvers',
        'BAF <= 2',
        'BAF > 2 and <= 20',
        'BAF > 20 and <= 50',
        'BAF > 50 and <= 80',
        'BAF > 80'
    ]
    values = [5135, 1861, 135, 115, 22, 265]

    create_pie_chart(labels, values, file_path)


def generate_dns_fingerprinting_pie_chart(file_path):
    """
    Generates a pie chart for the distribution of fingerprinted DNS resolvers (of the versions).
    :file_path: path to save the generated pie chart image
    :returns: None
    """
    total_values = sum(dns_version_info.values())
    filtered_data = {label: value for label, value in dns_version_info.items() if (value / total_values) > 0.01}

    labels = list(filtered_data.keys())
    values = list(filtered_data.values())

    create_pie_chart(labels, values, file_path, width=1200, height=900)


ntp_pie_chart_path = './piecharts/ntp_piechart_merged.png'
dns_pie_chart_path = './piecharts/dns_sl_piechart.png'
dns_versions_path = './piecharts/dns_versions.png'

if __name__ == '__main__':
    # generate_dns_fingerprinting_pie_chart(dns_versions_path)
    # generate_dns_pie_chart(dns_pie_chart_path)
    generate_ntp_pie_chart(ntp_pie_chart_path)