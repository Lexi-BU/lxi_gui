import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

# Load and preprocess data
import lxi_save_figures as lsf
import importlib
importlib.reload(lsf)

read_data = True
if read_data:
    df = lsf.read_and_plot_all_files()
    # selected_columns = ["PinPullerTemp"]
    selected_columns = ["+10V_Imon"]
    input_key = selected_columns[0]
    input_key_unit = "mA"
    df = df[selected_columns]
    df["operation_number"] = 1
    df["number_of_data_points"] = 1
    operation_number = 1
    number_of_data_points = 1
    for i in range(1, len(df)):
        if (df.index[i] - df.index[i - 1]).total_seconds() > 10800:
            operation_number += 1
            number_of_data_points = 1
            df.loc[df.index[i], "number_of_data_points"] = number_of_data_points
            df.loc[df.index[i], "operation_number"] = operation_number
        else:
            number_of_data_points += 1
            df.loc[df.index[i], "number_of_data_points"] = number_of_data_points
            df.loc[df.index[i], "operation_number"] = operation_number
        if i % 1000 == 0:
            print(f"Progress: {i}/{len(df)}")

    df = df.dropna()
    df["operation_number"] = df["operation_number"].astype(int)
    df["number_of_data_points"] = df["number_of_data_points"] / 60
    df["Date"] = df.index
    # Smooth out the input key
    df[f"{input_key}_smooth"] = df[input_key].rolling(window=60, center=True).median()
    # Unique operation numbers
    unique_operations = df["operation_number"].unique()

    # Add Date as a column
    df["Date"] = df.index

    # Define fixed colors for each operation number
    unique_operations = sorted(df["operation_number"].unique())

color_map = {
    operation: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
    for i, operation in enumerate(unique_operations)
}

# Default to the latest operation
default_operation = unique_operations[-1]

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    style={"height": "100vh", "width": "100vw", "backgroundColor": "#121212", "color": "white", "padding": "10px"},
    children=[
        html.H1(f"{input_key} vs Time since start for each operation",
                style={"textAlign": "center", "color": "white"}),
        html.Div([
            html.Label("Select Operations:", style={"color": "white"}),
            dcc.Checklist(
                id="operation_filter",
                options=[{"label": f"Operation {op}", "value": op} for op in unique_operations],
                value=[default_operation],  # Default to the latest operation
                inline=True,
                style={"maxHeight": "150px", "overflowY": "scroll"}
            )
        ]),
        dcc.Graph(
            id="line_plot",
            style={"height": "85vh", "width": "100%"}
        ),
    ]
)


@app.callback(
    Output("line_plot", "figure"),
    [Input("operation_filter", "value")]
)
def update_plot(selected_operations):
    filtered_df = df[df["operation_number"].isin(selected_operations)]
    fig = px.line(
        filtered_df,
        x="number_of_data_points",
        y=f"{input_key}_smooth",
        color="operation_number",
        # title="PinPullerTemp vs Time since start for each operation",
        labels={
            "number_of_data_points": "Time since start [Minutes]",
            f"{input_key}_smooth": f"{input_key} {input_key_unit}",
            "operation_number": "Operation Number"
        },
        color_discrete_map=color_map,  # Fixed color mapping
        template="plotly_dark",
        hover_data={"Date": True, input_key: True, "number_of_data_points": True}
    )
    fig.update_xaxes(range=[0, 130])
    # fig.update_yaxes(range=[60, 70])
    # Display the x and y-axes lines in the plot
    fig.update_xaxes(showline=True, linewidth=2, linecolor="white", mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor="white", mirror=True)
    # Set the grid color and opacity
    fig.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
    fig.update_yaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
    fig.update_layout(
        plot_bgcolor="#121212",
        paper_bgcolor="#121212",
        font={"color": "white"},
        # legend={"title": {"text": "Operation Number", "side": "right"}}
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
