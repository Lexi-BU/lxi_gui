import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from pathlib import Path
import glob
import pandas as pd
import time
# import matplotlib
# matplotlib.use("Agg")

from concurrent.futures import ThreadPoolExecutor, as_completed


def forward(y):
    """Custom forward scale function"""
    return np.where(np.abs(y) <= 1, y, np.sign(y) * (1 + np.log10(np.abs(y))))


def inverse(y):
    """Custom inverse scale function"""
    return np.where(np.abs(y) <= 1, y, np.sign(y) * 10 ** (np.abs(y) - 1))


def check_folder_structure():
    # Start from the current directory and go up to 3 levels
    current_path = Path.cwd()

    for i in range(10):
        # Get the current directory by moving up 'i' levels
        check_path = current_path.parents[i] if i < len(current_path.parents) else current_path

        # Define the target folder structure
        target_folder = check_path / "data" / "from_LEXI" / "L1c" / "sci"

        if target_folder.is_dir():
            print(f"Found folder structure at: \033[1;32m {target_folder}\033[0m\n")
            return target_folder

    print("\033[1;91m Folder structure not found.\033[0m\n")
    return target_folder


def read_csv_file(csv_file):
    """Helper function to read a single CSV file."""
    return pd.read_csv(csv_file)


def read_sci_l1c_data():
    parent_folder = check_folder_structure()
    print(f"Reading data from: {parent_folder}\n")

    file_name_format = "lexi_payload_*_*_*_*_sci_output_L1c.csv"
    csv_files = np.sort(glob.glob(str(parent_folder / "**" / file_name_format), recursive=True))[:]

    print(f"Found \033[1;31m{len(csv_files)}\033[0m CSV files in the {parent_folder}\n")

    df_list = []
    with ThreadPoolExecutor() as executor:
        # Submit tasks to read CSV files in parallel
        future_to_file = {executor.submit(read_csv_file, csv_file): csv_file for csv_file in csv_files}

        for i, future in enumerate(as_completed(future_to_file)):
            csv_file = future_to_file[future]
            try:
                df = future.result()
                df_list.append(df)
                print(f"Reading file ==> \x1b[1;32;255m {np.round((i + 1) / len(csv_files) * 100, 3)}\x1b[0m % complete", end="\r")
            except Exception as e:
                print(f"Error reading file {csv_file}: {e}")

    df_all = pd.concat(df_list)

    # Set the Date column as the index
    try:
        df_all["Date"] = pd.to_datetime(df_all["Date"])
    except Exception:
        # Try the mixed format
        df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce", format="%Y-%m-%d %H:%M:%S.%f")
    df_all = df_all.set_index("Date", inplace=False)
    # Sort the data based on the Date index
    df_all = df_all.sort_index()

    return df_all


def add_operation_numbers(df):
    """Add operation numbers and data points in parallel."""
    operation_number = 1
    # number_of_data_points = 1
    start_time = time.time()  # Track start time

    def process_row(i):
        nonlocal operation_number # , number_of_data_points
        if (df.index[i] - df.index[i - 1]).total_seconds() > 10800:
            operation_number += 1
            # number_of_data_points = 1
        # else:
            # number_of_data_points += 1
        return i, operation_number # , number_of_data_points

    with ThreadPoolExecutor() as executor:
        # Submit tasks to process rows in parallel
        future_to_index = {executor.submit(process_row, i): i for i in range(1, len(df))}

        for future in as_completed(future_to_index):
            i, data_points = future.result()
            df.loc[df.index[i], "number_of_data_points"] = data_points
            # df.loc[df.index[i], "operation_number"] = op_num

            # Calculate elapsed time and estimated time remaining
            elapsed_time = time.time() - start_time
            avg_time_per_row = elapsed_time / i if i > 0 else 0
            estimated_total_time = avg_time_per_row * len(df)
            remaining_time = estimated_total_time - elapsed_time

            # Improved progress message with time estimates
            print(
                f"Progress: {np.round(i / len(df) * 100, 3)}% complete | "
                # f"Operation {op_num} of {len(df)} | "
                f"Elapsed: {np.round(elapsed_time, 3)}s | ",
                # f"Remaining: {np.round(remaining_time, 2)}s",
                end="\r"
            )

    return df


start_time = time.time()
read_data = True
if read_data:
    # Check the folder structure
    df = read_sci_l1c_data()
    # Add operation number to the data
    df["operation_number"] = 1
    # df["number_of_data_points"] = 1

    # Parallelize the operation number assignment
    df = add_operation_numbers(df)

    end_time = time.time()

    print(f"\n\nTotal time taken: {np.round(end_time - start_time, 3)} seconds\n")

    # Save the data to a pickle file
    df.to_pickle("../data/df_all.pkl")
else:
    # Load the data from the pickle file
    # df = pd.read_pickle("../data/df_all.pkl")
    pass


app = dash.Dash(__name__)

app.layout = html.Div(
    style={
        "height": "100vh",
        "width": "99vw",
        "backgroundColor": "#121212",
        "color": "white",
        "padding": "0px",
        "overflow": "scroll",
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "left",
        "justifyContent": "flex-start",
        "marginLeft": "0vw",
        "marginRight": "0vw",
        "justify": "center"},
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
                    options=[{"label": f"Operation {i}", "value": i} for i in range(1, len(df["operation_number"].unique()) + 1)],
                    # Set the default value to the last operation number
                    value=df["operation_number"].unique()[-1],
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
                    value=["lin_correction"],
                    style={"color": "white"},
                ),
                # Add two input boxes for zmin and zmax
                html.Label("Zmin", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="zmin", type="number", placeholder="Zmin", style={"color": "black", "marginRight": "10px", "width": "70px"}),
                html.Label("Zmax", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="zmax", type="number", placeholder="Zmax", style={"color": "black", "width": "70px"}),
                html.Label("Zmin (x, y)", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="zmin_xy", type="number", placeholder="Zmin", style={"color": "black", "marginRight": "10px", "width": "70px"}),
                html.Label("Zmax (x, y)", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="zmax_xy", type="number", placeholder="Zmax", style={"color": "black", "width": "70px"}),
                html.Label("Bins (v)", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="nbins", type="number", placeholder="Bins", style={"color": "black", "width": "70px"}),
                html.Label("Bins (x, y)", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="nbins_xy", type="number", placeholder="Bins", style={"color": "black", "width": "70px"}),
            ],
        ),
        # Add tabs for additional graphs
        dcc.Tabs(
            id="tabs",
            value="tab-2",
            children=[
                dcc.Tab(
                    label="Channel Graphs",
                    value="graphs",
                    style={"backgroundColor": "#121212", "color": "white", "border": "1px solid white", "borderRadius": "5px", "width": "100%", "height": "20%"},
                    children=[
                        html.Div(
                            style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center"},
                            children=[
                                dcc.Graph(id="channel_1_3", style={"width": "50%", "height": "100%"}),
                                dcc.Graph(id="channel_2_4", style={"width": "50%", "height": "100%"}),
                            ],
                        ),
                    ],
                ),
                dcc.Tab(
                    label="X-Y Positions",
                    value="tab-2",
                    style={"backgroundColor": "#121212", "color": "white", "border": "1px solid white", "borderRadius": "5px", "width": "100%", "height": "20%"},
                    children=[
                        # Content for the second tab
                        html.Div(
                            style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center"},
                            children=[
                                dcc.Graph(id="x_y_positions", style={"width": "100%", "height": "100%"}),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("input_boxes", "children"),
    [Input("channel_checklist", "value")]
)
def update_input_boxes(selected_channels):
    input_boxes = []
    for channel in selected_channels:
        input_boxes.append(dcc.Input(id=f"min_value_{channel}", type="number", placeholder=f"Min {channel[-1]}", style={"color": "black", "marginRight": "10px", "width": "70px"}))
        input_boxes.append(dcc.Input(id=f"max_value_{channel}", type="number", placeholder=f"Max {channel[-1]}", style={"color": "black", "marginRight": "10px", "width": "70px"}))
    return input_boxes


@app.callback(
    Output("channel_1_3", "figure"),
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
        Input("zmin", "value"),
        Input("zmax", "value"),
        Input("nbins", "value"),
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
    zmin,
    zmax,
    nbins,
):
    # Filter the data based on the operation number
    df_filtered = df[df["operation_number"] == operation_number_dropdown]

    # If the min or max values are not provided, set them to 0 and 4.51 respectively
    for channel in channel_checklist:
        if channel == "Channel1":
            if min_value_channel1 is None:
                min_value_channel1 = 1.3
            if max_value_channel1 is None:
                max_value_channel1 = 3.3
        elif channel == "Channel2":
            if min_value_channel2 is None:
                min_value_channel2 = 1.3
            if max_value_channel2 is None:
                max_value_channel2 = 3.3
        elif channel == "Channel3":
            if min_value_channel3 is None:
                min_value_channel3 = 1.3
            if max_value_channel3 is None:
                max_value_channel3 = 3.3
        elif channel == "Channel4":
            if min_value_channel4 is None:
                min_value_channel4 = 1.3
            if max_value_channel4 is None:
                max_value_channel4 = 3.3
    # Filter the data based on the min and max values of each channel
    df_filtered = df_filtered[df_filtered["Channel1"].between(min_value_channel1, max_value_channel1) & df_filtered["Channel2"].between(min_value_channel2, max_value_channel2) & df_filtered["Channel3"].between(min_value_channel3, max_value_channel3) & df_filtered["Channel4"].between(min_value_channel4, max_value_channel4)]

    # Filter the data based on the IsCommanded event
    if "is_commanded" in is_commanded_checkbox:
        df_filtered = df_filtered
    else:
        df_filtered = df_filtered[~df_filtered["IsCommanded"]]

    if "Channel1" and "Channel3" in channel_checklist:
        x_channel, y_channel = "Channel1", "Channel3"
        x_data = df_filtered[x_channel]
        y_data = df_filtered[y_channel]

        threshold = 5  # Values below this will be transparent


        # If zmin and zmax are not provided, set them to 1 and 120 respectively
        if zmin is None:
            zmin = 1
        if zmax is None:
            zmax = 120
        if nbins is None:
            nbins = 50
        # Custom colorscale:
        custom_colorscale = [
            (0.0, "rgba(0,0,0,0)"),  # Fully transparent for values below threshold
            ((zmin - 1) / 1000, "white"),  # White just above threshold
            (0.1, "#0d0887"),  # Dark purple (Plasma colormap start)
            (0.3, "#5a01a7"),  # Purple
            (0.5, "#9c179e"),  # Magenta
            (0.7, "#e16462"),  # Orange-red
            (0.9, "#fca636"),  # Orange-yellow
            (1.0, "#f0f921")   # Bright yellow (Plasma colormap end)
        ]
        # Define the tick values dynamically using log scale
        tickvals = np.logspace(np.log10(zmin), np.log10(zmax), num=4)
        ticktext = [f"{val:.1f}" for val in tickvals]
        # Create hexbin plot

        hist, x_edges, y_edges = np.histogram2d(x_data, y_data, bins=nbins)
        # x_edges = np.append(x_edges, x_edges[-1] + (x_edges[-1] - x_edges[-2]))
        # y_edges = np.append(y_edges, y_edges[-1] + (y_edges[-1] - y_edges[-2]))
        # x_data = np.repeat(x_edges[:-1], hist.flatten())
        # y_data = np.repeat(y_edges[:-1], hist.flatten())
        # Filter out values below the threshold
        hist[hist < zmin] = 0
        fig = go.Figure()

        fig.add_trace(
            go.Heatmap(
                x=x_edges,
                y=y_edges,
                z=hist.T,
                colorscale="inferno",
                showscale=True,
                colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext, tickmode="array", thickness=15),
                zmin=zmin,
                zmax=zmax,
                zauto=False,
            )
            # go.Histogram2d(
            #     x=x_data,
            #     y=y_data,
            #     z=hist.flatten(),
            #     colorscale="inferno_r",
            #     # ncontours=bin_numbers,
            #     nbinsx=nbins,
            #     nbinsy=nbins,
            #     showscale=True,
            #     colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext),
            #     zmin=zmin,
            #     zmax=zmax,
            #     zauto=True,
            # )
        )

        # Set the x and y aspect ratio to be equal
        # fig.update_layout(aspectmode="equal")

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
                line=dict(color="rgba(120, 240, 189, 1)"),
                name=f"{x_channel} Histogram",
                line_shape="hvh",
                # Set the y-axis scale to log
            )
        )
        fig.add_trace(
            go.Scatter(
                x=y_counts,
                y=y_step_y,
                xaxis="x2",
                mode="lines",
                line=dict(color="rgba(224, 83, 230, 1)"),
                name=f"{y_channel} Histogram",
                line_shape="hv",
            )
        )
        # Update layout for subplots
        fig.update_layout(
            height=900,
            xaxis=dict(title=x_channel, domain=[0, 0.85], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", scaleanchor="y", range=[min_value_channel1, max_value_channel1]),
            yaxis=dict(title=y_channel, domain=[0, 0.85], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", scaleanchor="x", range=[min_value_channel3, max_value_channel3]),
            xaxis2=dict(domain=[0.85, 1], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", type="log"),
            yaxis2=dict(domain=[0.85, 1], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", type="log"),
            bargap=0,
            showlegend=False,
            # title="Hexbin Plot with Histograms",
            plot_bgcolor="#121212",
            paper_bgcolor="#121212",
            # Set the font color to white
            font=dict(color="white"),
        )

        return fig
    else:
        return go.Figure()


@app.callback(
    Output("channel_2_4", "figure"),
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
        Input("zmin", "value"),
        Input("zmax", "value"),
        Input("nbins", "value"),
    ],
)
def update_histogram(
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
    zmin,
    zmax,
    nbins,
):
    # Filter the data based on the operation number
    df_filtered = df[df["operation_number"] == operation_number_dropdown]

    # If the min or max values are not provided, set them to 0 and 4.51 respectively
    for channel in channel_checklist:
        if channel == "Channel1":
            if min_value_channel1 is None:
                min_value_channel1 = 1.3
            if max_value_channel1 is None:
                max_value_channel1 = 3.3
        elif channel == "Channel2":
            if min_value_channel2 is None:
                min_value_channel2 = 1.3
            if max_value_channel2 is None:
                max_value_channel2 = 3.3
        elif channel == "Channel3":
            if min_value_channel3 is None:
                min_value_channel3 = 1.3
            if max_value_channel3 is None:
                max_value_channel3 = 3.3
        elif channel == "Channel4":
            if min_value_channel4 is None:
                min_value_channel4 = 1.3
            if max_value_channel4 is None:
                max_value_channel4 = 3.3

    # Filter the data based on the min and max values of each channel
    df_filtered = df_filtered[df_filtered["Channel1"].between(min_value_channel1, max_value_channel1) & df_filtered["Channel2"].between(min_value_channel2, max_value_channel2) & df_filtered["Channel3"].between(min_value_channel3, max_value_channel3) & df_filtered["Channel4"].between(min_value_channel4, max_value_channel4)]

    # Filter the data based on the IsCommanded event
    if "is_commanded" in is_commanded_checkbox:
        df_filtered = df_filtered
    else:
        df_filtered = df_filtered[~df_filtered["IsCommanded"]]

    if "Channel2" and "Channel4" in channel_checklist:
        x_channel, y_channel = "Channel2", "Channel4"
        x_data = df_filtered[x_channel]
        y_data = df_filtered[y_channel]

        threshold = 5

        # If zmin and zmax are not provided, set them to 1 and 120 respectively
        if zmin is None:
            zmin = 1
        if zmax is None:
            zmax = 120
        if nbins is None:
            nbins = 50
        # Custom colorscale:
        custom_colorscale = [
            (0.0, "rgba(0,0,0,0)"),  # Fully transparent for values below threshold
            ((threshold - 1) / 1000, "white"),  # White just above threshold
            (0.1, "#0d0887"),  # Dark purple (Plasma colormap start)
            (0.3, "#5a01a7"),  # Purple
            (0.5, "#9c179e"),  # Magenta
            (0.7, "#e16462"),  # Orange-red
            (0.9, "#fca636"),  # Orange-yellow
            (1.0, "#f0f921")   # Bright yellow (Plasma colormap end)
        ]

        # Define the tick values dynamically using log scale
        tickvals = np.logspace(np.log10(zmin), np.log10(zmax), num=4)
        ticktext = [str(int(i)) for i in tickvals]

        hist, x_edges, y_edges = np.histogram2d(x_data, y_data, bins=nbins)
        # Filter out values below the threshold
        hist[hist < zmin] = 0

        fig = go.Figure()

        fig.add_trace(
            go.Heatmap(
                x=x_edges,
                y=y_edges,
                z=hist.T,
                colorscale="inferno",
                showscale=True,
                colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext, tickmode="array", thickness=15),
                zmin=zmin,
                zmax=zmax,
                zauto=False,
            )
            # go.Histogram2d(
            #     x=x_data,
            #     y=y_data,
            #     z=hist.flatten(),
            #     colorscale="inferno_r",
            #     # ncontours=bin_numbers,
            #     nbinsx=nbins,
            #     nbinsy=nbins,
            #     showscale=True,
            #     colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext),
            #     zmin=zmin,
            #     zmax=zmax,
            #     zauto=True,
            # )
        )


        # Set the x and y aspect ratio to be equal
        # fig.update_layout(aspectmode="equal")

        x_counts, x_bins = np.histogram(x_data, bins=100)
        y_counts, y_bins = np.histogram(y_data, bins=100)

        x_step_x = 0.5 * (x_bins[:-1] + x_bins[1:])
        # x_step_y = 0.5 * (y_bins[:-1] + y_bins[1:])
        y_step_y = 0.5 * (y_bins[:-1] + y_bins[1:])
        # y_step_x = 0.5 * (y_bins[:-1] + y_bins[1:])

        fig.add_trace(
            go.Scatter(
                x=x_step_x,
                y=x_counts,
                yaxis="y2",
                mode="lines",
                line=dict(color="rgba(107, 202, 240, 1)"),
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
                line=dict(color="rgba(231, 169, 86, 1)"),
                name=f"{y_channel} Histogram",
                line_shape="hv",
            )
        )
        # Update layout for subplots
        fig.update_layout(
            height=900,
            xaxis=dict(title=x_channel, domain=[0, 0.85], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", scaleanchor="y", range=[min_value_channel2, max_value_channel2]),
            yaxis=dict(title=y_channel, domain=[0, 0.85], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", scaleanchor="x", range=[min_value_channel4, max_value_channel4]),
            xaxis2=dict(domain=[0.85, 1], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", type="log"),
            yaxis2=dict(domain=[0.85, 1], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", type="log"),
            bargap=0,
            showlegend=False,
            # title="Hexbin Plot with Histograms",
            plot_bgcolor="#121212",
            paper_bgcolor="#121212",
            # Set the font color to white
            font=dict(color="white"),
        )

        return fig
    else:
        return go.Figure()


@app.callback(
    Output("x_y_positions", "figure"),
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
        Input("zmin_xy", "value"),
        Input("zmax_xy", "value"),
        Input("nbins_xy", "value"),
    ],
)
def update_x_y_positions(
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
    zmin,
    zmax,
    nbins,
):
    # Filter the data based on the operation number
    df_filtered = df[df["operation_number"] == operation_number_dropdown]

    # If the min or max values are not provided, set them to 0 and 4.51 respectively
    for channel in channel_checklist:
        if channel == "Channel1":
            if min_value_channel1 is None:
                min_value_channel1 = 1.3
            if max_value_channel1 is None:
                max_value_channel1 = 3.3
        elif channel == "Channel2":
            if min_value_channel2 is None:
                min_value_channel2 = 1.3
            if max_value_channel2 is None:
                max_value_channel2 = 3.3
        elif channel == "Channel3":
            if min_value_channel3 is None:
                min_value_channel3 = 1.3
            if max_value_channel3 is None:
                max_value_channel3 = 3.3
        elif channel == "Channel4":
            if min_value_channel4 is None:
                min_value_channel4 = 1.3
            if max_value_channel4 is None:
                max_value_channel4 = 3.3

    # Filter the data based on the min and max values of each channel
    df_filtered = df_filtered[df_filtered["Channel1"].between(min_value_channel1, max_value_channel1) & df_filtered["Channel2"].between(min_value_channel2, max_value_channel2) & df_filtered["Channel3"].between(min_value_channel3, max_value_channel3) & df_filtered["Channel4"].between(min_value_channel4, max_value_channel4)]

    # Filter the data based on the IsCommanded event
    if "is_commanded" in is_commanded_checkbox:
        df_filtered = df_filtered
    else:
        df_filtered = df_filtered[~df_filtered["IsCommanded"]]

    # Check if lin_correction is selected
    if "lin_correction" in lin_correction_checkbox:
        x_plot_key = "x_mcp_lin"
        y_plot_key = "y_mcp_lin"
    else:
        x_plot_key = "x_mcp"
        y_plot_key = "y_mcp"

    if zmin is None:
        zmin = 1
    if zmax is None:
        zmax = 120
    if nbins is None:
        nbins = 50

    # Custom colorscale:
    custom_colorscale = [
        (0.0, "rgba(0,0,0,0)"),  # Fully transparent for values below threshold
        ((zmin - 1) / 1000, "white"),  # White just above threshold
        (0.1, "#0d0887"),  # Dark purple (Plasma colormap start)
        (0.3, "#5a01a7"),  # Purple
        (0.5, "#9c179e"),  # Magenta
        (0.7, "#e16462"),  # Orange-red
        (0.9, "#fca636"),  # Orange-yellow
        (1.0, "#f0f921")   # Bright yellow (Plasma colormap end)
    ]

    # Define the tick values dynamically using log scale
    tickvals = np.logspace(np.log10(zmin), np.log10(zmax), num=4)
    ticktext = [str(int(i)) for i in tickvals]

    hist, x_edges, y_edges = np.histogram2d(df_filtered[x_plot_key], df_filtered[y_plot_key], bins=nbins)
    # Filter out values below the threshold
    hist[hist < zmin] = 0

    fig = go.Figure()

    # Add a histogram trace
    fig.add_trace(
        go.Heatmap(
            x=x_edges,
            y=y_edges,
            z=hist.T,
            colorscale="inferno",
            showscale=True,
            colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext, tickmode="array", thickness=15),
            zmin=zmin,
            zmax=zmax,
            zauto=False,
        )
        # go.Histogram2d(
        #     x=df_filtered[x_plot_key],
        #     y=df_filtered[y_plot_key],
        #     colorscale=custom_colorscale,
        #     nbinsx=nbins,
        #     nbinsy=nbins,
        #     showscale=True,
        #     colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext),
        #     zmin=zmin,
        #     zmax=zmax,
        #     zauto=False,
        # )
    )

    # Add a circle of radius 5 around the origin
    theta = np.linspace(0, 2 * np.pi, 100)  # Angles for the circle
    circle_x = 5 * np.cos(theta)  # x-coordinates of the circle
    circle_y = 5 * np.sin(theta)  # y-coordinates of the circle

    fig.add_trace(
        go.Scatter(
            x=circle_x,
            y=circle_y,
            mode="lines",
            line=dict(color="cyan", width=2),  # Customize circle color and line width
            name="Circle (r=5)",
        )
    )

    # Add annotation with text and arrow
    fig.add_annotation(
        x=5 * np.cos(np.pi / 4),  # x-coordinate of the arrow tip (edge of the circle)
        y=5 * np.sin(np.pi / 4),  # y-coordinate of the arrow tip (edge of the circle)
        text="Effective area",  # Text to display
        showarrow=True,  # Show arrow
        ax=50,  # Arrow length in x-direction (positive = right, negative = left)
        ay=-50,  # Arrow length in y-direction (positive = down, negative = up)
        arrowhead=2,  # Arrowhead style
        arrowsize=1.5,  # Arrow size
        font=dict(size=14, color="white"),  # Font settings for the text
        bordercolor="white",  # Border color of the text box
        borderwidth=1,  # Border width of the text box
        borderpad=4,  # Padding between text and border
        bgcolor="black",  # Background color of the text box
    )

    # Set the x and y aspect ratio to be equal
    # fig.update_layout(aspectmode="equal")

    x_counts, x_bins = np.histogram(df_filtered[x_plot_key], bins=100)
    y_counts, y_bins = np.histogram(df_filtered[y_plot_key], bins=100)

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
            name="X",
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
            name="Y",
            line_shape="hvh",
        )
    )

    # Update layout for subplots
    fig.update_layout(
        height=900,
        xaxis=dict(title="X [cm]", domain=[0, 0.85], gridcolor="rgba(255, 255, 255, 0.2)", showgrid=True, scaleanchor="y", range=[-5, 5], autorange=False),
        yaxis=dict(title="Y [cm]", domain=[0, 0.85], gridcolor="rgba(255, 255, 255, 0.2)", showgrid=True, scaleanchor="x", range=[-5, 5], autorange=False),
        xaxis2=dict(domain=[0.85, 1], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", type="log", range=[-5, 5], autorange=False),
        yaxis2=dict(domain=[0.85, 1], showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", type="log", range=[-5, 5], autorange=False),
        bargap=0,
        showlegend=False,
        # title="Hexbin Plot with Histograms",
        plot_bgcolor="#121212",
        paper_bgcolor="#121212",
        # Set the font color to white
        font=dict(color="white"),
    )

    return fig


if __name__ == "__main__":
    host = "127.0.0.6"
    port = "8050"
    app.run_server(host=host, port=port, debug=False)
    print(f"Running on http://{host}:{port}/")
