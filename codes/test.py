import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Sample DataFrame
# df = pd.DataFrame({
#     "operation_number": [1, 1, 2, 2],
#     "Channel_1": [10, 15, 20, 25],
#     "Channel_2": [5, 10, 15, 20],
#     "Channel_3": [1, 2, 3, 4],
#     "Channel_4": [8, 9, 10, 11],
#     "IsCommanded": [True, False, True, False],
#     "Date": pd.date_range(start="2023-01-01", periods=4)
# })

app = dash.Dash(__name__)

app.layout = html.Div(
    style={"height": "99vh", "width": "99vw", "backgroundColor": "#121212", "color": "white", "padding": "0px", "overflow": "hidden", "display": "flex", "flexDirection": "column", "alignItems": "left", "justifyContent": "center", "marginLeft": "0vw", "marginRight": "0vw", "justify": "center"},
    children=[
        # Add four check boxes corresponding to the four Channels
        html.Div(
            style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center"},
            children=[
                dcc.Checklist(
                    id="channel_checklist",
                    options=[
                        {"label": "Channel 1", "value": "Channel1"},
                        {"label": "Channel 2", "value": "Channel2"},
                        {"label": "Channel 3", "value": "Channel3"},
                        {"label": "Channel 4", "value": "Channel4"},
                    ],
                    inline=True,
                    value=["Channel1", "Channel2", "Channel3", "Channel4"],
                    style={"color": "white"},
                )
            ],
        ),
        # Add the input boxes for minimum and maximum value of each channel
        html.Div(id="input_boxes", style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center"}),
        # Add the dropdown menu and checkboxes in the same row
        html.Div(
            style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center", "marginTop": "10px"},
            children=[
                # Dropdown for operation number
                dcc.Dropdown(
                    id="operation_number_dropdown",
                    options=[{"label": f"Operation {i}", "value": i} for i in range(1, 3)],
                    value=1,
                    className="dark-dropdown",
                    style={"width": "200px", "marginRight": "20px", "color": "black"},
                ),
                # Checkbox for "IsCommanded"
                dcc.Checklist(
                    id="is_commanded_checkbox",
                    options=[{"label": "IsCommanded", "value": "is_commanded"}],
                    value=[],
                    style={"color": "white", "marginRight": "20px"},
                ),
                # Checkbox for "Linear Correction"
                dcc.Checklist(
                    id="lin_correction_checkbox",
                    options=[{"label": "Linear Correction", "value": "lin_correction"}],
                    value=[],
                    style={"color": "white"},
                ),
            ],
        ),
        # Add the graph
        dcc.Graph(id="hexbin_plot", style={"height": "70vh", "width": "95vw", "overflow": "hidden"}),
    ],
)

@app.callback(
    Output("input_boxes", "children"),
    [Input("channel_checklist", "value")]
)
def update_input_boxes(selected_channels):
    input_boxes = []
    for channel in selected_channels:
        input_boxes.append(dcc.Input(id=f"min_value_{channel}", type="number", placeholder=f"Min {channel}", style={"color": "black", "marginRight": "10px"}))
        input_boxes.append(dcc.Input(id=f"max_value_{channel}", type="number", placeholder=f"Max {channel}", style={"color": "black", "marginRight": "10px"}))
    return input_boxes


@app.callback(
    Output("hexbin_plot", "figure"),
    [
        Input("channel_checklist", "value"),
        Input("min_value_Channel1", "value"),
        Input("max_value_Channel1", "value"),
        Input("min_value_Channel2", "value"),
        Input("max_value_Channel2", "value"),
        Input("min_value_Channel3", "value"),
        Input("max_value_Channel3", "value"),
        Input("min_value_Channel4", "value"),
        Input("max_value_Channel4", "value"),
        Input("operation_number_dropdown", "value"),
        Input("is_commanded_checkbox", "value"),
        Input("lin_correction_checkbox", "value"),
    ],
)
def update_graph(
    channel_checklist,
    min_value_channel1,
    max_value_channel1,
    min_value_channel2,
    max_value_channel2,
    min_value_channel3,
    max_value_channel3,
    min_value_channel4,
    max_value_channel4,
    operation_number_dropdown,
    is_commanded_checkbox,
    lin_correction_checkbox,
):
    # Filter the data based on the operation number
    df_filtered = df[df["operation_number"] == operation_number_dropdown]

    # Filter the data based on the IsCommanded event
    # if "is_commanded" in is_commanded_checkbox:
    #     df_filtered = df_filtered
    # else:
    #     df_filtered = df_filtered[~df_filtered["IsCommanded"]]

    # Apply linear correction
    # if "lin_correction" in lin_correction_checkbox:
    #     df_filtered["Channel1"] = df_filtered["Channel1"] * 2

    # Check if exactly two channels are selected
    if "Channel1" and "Channel3" in channel_checklist:
        x_channel, y_channel = "Channel1", "Channel3"
        x_data = df_filtered[x_channel]
        y_data = df_filtered[y_channel]

        threshold = 5  # Values below this will be transparent

        # Custom colorscale:
        custom_colorscale = [
            (0.0, "rgba(0,0,0,0)"),   # Fully transparent for values below threshold
            ((threshold - 1) / 1000, "rgba(255,255,255,1)"),  # White just above threshold
            (0.2, "lightgray"),
            (0.5, "yellow"),
            (1.0, "red")
        ]

        # Create hexbin plot
        fig = go.Figure()

        # Add hexbin trace
        fig.add_trace(
            go.Histogram2dContour(
                x=x_data,
                y=y_data,
                colorscale="plasma",
                ncontours=20,
                showscale=True,
                colorbar=dict(title="Count", tickvals=np.logspace(0.01, 3, 4), ticktext=["1", "10", "100", "1000"]),
                zmin=5,
                zmax=1000,
                zauto=False,
            )
        )

        x_counts, x_bins = np.histogram(x_data, bins=100)
        y_counts, y_bins = np.histogram(y_data, bins=100)

        x_step_x = 0.5 * (x_bins[:-1] + x_bins[1:])
        # x_step_y = 0.5 * (y_bins[:-1] + y_bins[1:])

        # y_step_x = 0.5 * (y_bins[:-1] + y_bins[1:])
        y_step_y = 0.5 * (y_bins[:-1] + y_bins[1:])

        fig.add_trace(
            go.Scatter(
                x=x_step_x,
                y=x_counts,
                yaxis="y2",
                mode="lines",
                line=dict(color="green"),
                name=f"{x_channel} Histogram",
                line_shape="hvh",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=y_counts,
                y=y_step_y,
                xaxis="x2",
                mode="lines",
                line=dict(color="green"),
                name=f"{y_channel} Histogram",
                line_shape="hvh",
            )
        )
        # Update layout for subplots
        fig.update_layout(
            xaxis=dict(title=x_channel, domain=[0, 0.85], showgrid=False),
            yaxis=dict(title=y_channel, domain=[0, 0.85], showgrid=False),
            xaxis2=dict(domain=[0.85, 1], showgrid=False),
            yaxis2=dict(domain=[0.85, 1], showgrid=False),
            bargap=0,
            showlegend=False,
            title="Hexbin Plot with Histograms",
        )

        return fig

    # If not exactly two channels are selected, return an empty figure
    return go.Figure()


if __name__ == "__main__":
    host = "127.0.0.5"
    port = "8050"
    app.run_server(host=host, port=port, debug=False)
    print(f"Running on http://{host}:{port}/")