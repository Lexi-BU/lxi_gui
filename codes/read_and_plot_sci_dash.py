import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from pathlib import Path
import glob
import pandas as pd

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

    for i in range(4):
        # Get the current directory by moving up 'i' levels
        check_path = current_path.parents[i] if i < len(current_path.parents) else current_path

        # Define the target folder structure
        target_folder = check_path / "data" / "from_LEXI" / "L1c" / "sci"

        if target_folder.is_dir():
            print(f"Found folder structure at: \033[1;32m {target_folder}\033[0m\n")
            return target_folder

    print("\033[1;91m Folder structure not found.\033[0m\n")
    # Cd into the target folder

    return target_folder


# Function to process each chunk of the dataframe
def process_chunk(chunk, start_idx, end_idx):
    operation_number = 1
    number_of_data_points = 1
    chunk_results = []

    for i in range(start_idx, end_idx):
        if i > 0 and (chunk.index[i] - chunk.index[i - 1]).total_seconds() > 10800:
            operation_number += 1
            number_of_data_points = 1
        else:
            number_of_data_points += 1

        chunk_results.append((chunk.index[i], operation_number, number_of_data_points))

    return chunk_results


# Function to split the dataframe into chunks and process in parallel
def parallelize_data_processing(df, num_threads=10):
    chunk_size = len(df) // num_threads
    chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_threads)]

    # Adjust the last chunk to cover any remaining rows
    if len(df) % num_threads != 0:
        chunks[-1] = (chunks[-1][0], len(df))

    results = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_chunk = {executor.submit(process_chunk, df, start, end): (start, end) for start, end in chunks}

        for future in as_completed(future_to_chunk):
            chunk_start, chunk_end = future_to_chunk[future]
            try:
                chunk_results = future.result()
                results.extend(chunk_results)
            except Exception as e:
                print(f"Error processing chunk ({chunk_start}, {chunk_end}): {e}")

    # Create a dataframe with the results
    operation_number_col = [result[1] for result in results]
    number_of_data_points_col = [result[2] for result in results]

    # Ensure the lists have the same length as the original df
    assert len(operation_number_col) == len(df), "Mismatch in the length of the results"
    assert len(number_of_data_points_col) == len(df), "Mismatch in the length of the results"

    df['operation_number'] = operation_number_col
    df['number_of_data_points'] = number_of_data_points_col

    return df


def read_sci_l1c_data():
    parent_folder = check_folder_structure()
    print(f"Reading data from: {parent_folder}\n")

    file_name_format = "lexi_payload_*_*_*_*_sci_output_L1c.csv"
    csv_files = np.sort(glob.glob(str(parent_folder / "**" / file_name_format), recursive=True))

    print(f"Found \033[1;31m{len(csv_files)}\033[0m CSV files in the {parent_folder}\n")

    # Define the number of threads (adjust as needed based on the number of files)
    num_threads = 4
    chunk_size = len(csv_files) // num_threads
    chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_threads)]

    # Ensure the last chunk covers all remaining files
    if len(csv_files) % num_threads != 0:
        chunks[-1] = (chunks[-1][0], len(csv_files))

    def read_files_chunk(start_idx, end_idx):
        chunk_list = []
        for i in range(start_idx, end_idx):
            print(f"Reading file ==> \x1b[1;32;255m {np.round(i / len(csv_files) * 100, 3)}\x1b[0m % complete", end="\r")
            df = pd.read_csv(csv_files[i])
            chunk_list.append(df)
        return chunk_list

    # Use ThreadPoolExecutor to read CSV files in parallel
    df_list = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_chunk = {executor.submit(read_files_chunk, start, end): (start, end) for start, end in chunks}

        for future in as_completed(future_to_chunk):
            try:
                chunk_data = future.result()
                df_list.extend(chunk_data)  # Combine the results from each chunk
            except Exception as e:
                print(f"Error processing chunk: {e}")

    # Concatenate all dataframes from the chunks
    df_all = pd.concat(df_list)

    # Set the Date column as the index
    df_all["Date"] = pd.to_datetime(df_all["Date"])
    # Set the timezones to UTC (optional)
    # df_all["Date"] = df_all["Date"].dt.tz_localize("UTC")
    df_all = df_all.set_index("Date", inplace=False)

    return df_all


read_data = True
if read_data:
    # Check the folder structure
    df = read_sci_l1c_data()
    # Add operation number to the data
    df["operation_number"] = 1
    df["number_of_data_points"] = 1
    operation_number = 1
    number_of_data_points = 1

    # Process the dataframe in parallel
    df = parallelize_data_processing(df)

    # Print the progress (optional, could be done more efficiently in parallel with a callback or progress bar)
    for i in range(1, len(df)):
        print(f"Adding operation number ==> \x1b[1;32;255m {np.round(i / len(df) * 100, 6)}\x1b[0m % complete", end="\r")
    # for i in range(1, len(df)):
    #     if (df.index[i] - df.index[i - 1]).total_seconds() > 10800:
    #         operation_number += 1
    #         number_of_data_points = 1
    #     else:
    #         number_of_data_points += 1
    #     df.loc[df.index[i], "number_of_data_points"] = number_of_data_points
    #     df.loc[df.index[i], "operation_number"] = operation_number

    #     # Print the progress
    #     print(f"Adding operation number ==> \x1b[1;32;255m {np.round(i / len(df) * 100, 6)}\x1b[0m % complete", end="\r")


app = dash.Dash(__name__)

app.layout = html.Div(
    style={"height": "90vh", "width": "99vw", "backgroundColor": "#121212", "color": "white", "padding": "0px", "overflow": "scroll", "display": "flex", "flexDirection": "column", "alignItems": "left", "justifyContent": "center", "marginLeft": "0vw", "marginRight": "0vw", "justify": "center"},
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
                    value=["lin_correction"],
                    style={"color": "white"},
                ),
                # Add two input boxes for zmin and zmax
                html.Label("Zmin", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="zmin", type="number", placeholder="Zmin", style={"color": "black", "marginRight": "10px"}),
                html.Label("Zmax", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="zmax", type="number", placeholder="Zmax", style={"color": "black"}),
                html.Label("Zmin (x, y)", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="zmin_xy", type="number", placeholder="Zmin", style={"color": "black", "marginRight": "10px"}),
                html.Label("Zmax (x, y)", style={"color": "white", "marginLeft": "10px", "marginRight": "10px"}),
                dcc.Input(id="zmax_xy", type="number", placeholder="Zmax", style={"color": "black"}),
            ],
        ),
        # Add tabs for additional graphs
        dcc.Tabs(
            id="tabs",
            value="tab-1",
            children=[
                dcc.Tab(
                    label="Channel Graphs",
                    value="graphs",
                    style={"backgroundColor": "#121212", "color": "white", "border": "1px solid white", "borderRadius": "5px", "width": "100%", "height": "100%"},
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
                    style={"backgroundColor": "#121212", "color": "white", "border": "1px solid white", "borderRadius": "5px", "width": "100%", "height": "100%"},
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
        input_boxes.append(dcc.Input(id=f"min_value_{channel}", type="number", placeholder=f"Min {channel}", style={"color": "black", "marginRight": "10px"}))
        input_boxes.append(dcc.Input(id=f"max_value_{channel}", type="number", placeholder=f"Max {channel}", style={"color": "black", "marginRight": "10px"}))
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

    # Print the min max value of each channel
    print(min_value_channel1, max_value_channel1, min_value_channel2, max_value_channel2, min_value_channel3, max_value_channel3, min_value_channel4, max_value_channel4)

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
        bin_numbers = 100

        # If zmin and zmax are not provided, set them to 1 and 120 respectively
        if zmin is None:
            zmin = 1
        if zmax is None:
            zmax = 120

        # Define the tick values dynamically using log scale
        tickvals = np.logspace(np.log10(zmin), np.log10(zmax), num=4)
        ticktext = [str(int(i)) for i in tickvals]
        # Create hexbin plot
        fig = go.Figure()

        # Add hexbin trace
        fig.add_trace(
            go.Histogram2dContour(
                x=x_data,
                y=y_data,
                colorscale=custom_colorscale,
                ncontours=bin_numbers,
                showscale=True,
                colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext),
                zmin=zmin,
                zmax=zmax,
                zauto=False,
            )
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
        bin_numbers = 100
        # If zmin and zmax are not provided, set them to 1 and 120 respectively
        if zmin is None:
            zmin = 1
        if zmax is None:
            zmax = 120

        # Define the tick values dynamically using log scale
        tickvals = np.logspace(np.log10(zmin), np.log10(zmax), num=4)
        ticktext = [str(int(i)) for i in tickvals]
        # Create hexbin plot
        fig = go.Figure()

        # Add hexbin trace
        fig.add_trace(
            go.Histogram2dContour(
                x=x_data,
                y=y_data,
                colorscale=custom_colorscale,
                ncontours=bin_numbers,
                showscale=True,
                colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext),
                zmin=zmin,
                zmax=zmax,
                zauto=False,
            )
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

    threshold = 5

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
    bin_numbers = 100

    if zmin is None:
        zmin = 1
    if zmax is None:
        zmax = 120

    # Define the tick values dynamically using log scale
    tickvals = np.logspace(np.log10(zmin), np.log10(zmax), num=4)
    ticktext = [str(int(i)) for i in tickvals]
    # Create hexbin plot
    fig = go.Figure()

    # Add a histogram trace
    fig.add_trace(
        go.Histogram2d(
            x=df_filtered[x_plot_key],
            y=df_filtered[y_plot_key],
            colorscale=custom_colorscale,
            nbinsx=bin_numbers,
            nbinsy=bin_numbers,
            showscale=True,
            colorbar=dict(title="Count", tickvals=tickvals, ticktext=ticktext),
            zmin=zmin,
            zmax=zmax,
            zauto=False,
        )
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
    host = "127.0.0.5"
    port = "8050"
    app.run_server(host=host, port=port, debug=False)
    print(f"Running on http://{host}:{port}/")
