import plotly.graph_objects as go


def generate_funnel_chart():
    """
    Creates a funnel chart to show how the initial list of servers is filtered down.
    :return: void
    """
    file_path = "./plots/" + input("Please enter the file path where you want the plot to be saved: ")

    stages = ['Initial DNS Hosts', 'Open Resolvers', 'Amplification <= 2',
              'Amplification > 2 and <= 20', 'Amplification > 20 and <= 50',
              'Amplification > 50 and <= 80', 'Amplification > 80']
    values = [8000, 2000, 500, 500, 500, 300, 200]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial"
    ))

    fig.update_layout(
        title='Funnel Chart of DNS Hosts Analysis in Greece',
        title_x=0.5,
        xaxis_title='Number of Hosts',
        yaxis_title='Stage'
    )

    fig.write_image(file_path)


if __name__ == '__main__':
    generate_funnel_chart()