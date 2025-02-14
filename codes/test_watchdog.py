import time
import numpy as np
import pandas as pd
import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import threading


# Global dataframe to store the data
df_all = pd.DataFrame()


def check_folder_structure():
    # Start from the current directory and go up to 3 levels
    current_path = Path.cwd()

    for i in range(5):
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
    try:
        # Attempt to read the file
        df = pd.read_csv(csv_file)
        if df.empty:
            print(f"File is empty: {csv_file}")
            return None
        return df
    except pd.errors.EmptyDataError:
        print(f"File is empty or corrupted: {csv_file}")
        return None
    except Exception as e:
        print(f"Error reading file {csv_file}: {e}")
        return None


def read_sci_l1c_data(parent_folder):
    # parent_folder = check_folder_structure()
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
                if df is not None:
                    df_list.append(df)
                    print(f"Reading file ==> \x1b[1;32;255m {np.round((i + 1) / len(csv_files) * 100, 3)}\x1b[0m % complete", end="\r")
            except Exception as e:
                print(f"Error reading file {csv_file}: {e}")

    df_all = pd.concat(df_list)

    # Set the Date column as the index
    # Try parsing with fractional seconds first
    df_all["Date"] = pd.to_datetime(df_all["Date"], format="%Y-%m-%d %H:%M:%S.%f%z", errors="coerce")

    # Fill NaT values by parsing without fractional seconds
    df_all["Date"] = df_all["Date"].fillna(pd.to_datetime(df_all["Date"], format="%Y-%m-%d %H:%M:%S%z", errors="coerce"))

    # Drop the rows with NaT values in the Date column
    df_all = df_all.dropna(subset=["Date"])

    # try:
    #     df_all["Date"] = pd.to_datetime(df_all["Date"])
    # except Exception:
    #     # Try the mixed format
    #     df_all["Date"] = pd.to_datetime(df_all["Date"], format="ISO8601", errors="coerce")
    df_all = df_all.set_index("Date", inplace=False)
    # Sort the data based on the Date index
    df_all = df_all.sort_index()

    return df_all


def add_operation_numbers(df, last_operation_number=0):
    """Add operation numbers and data points."""
    if last_operation_number == 0:
        operation_number = last_operation_number + 1
        number_of_data_points = 1
    else:
        operation_number = last_operation_number + 1
        number_of_data_points = 1
    start_time = time.time()  # Track start time

    # Initialize columns if they don't exist
    if "operation_number" not in df.columns:
        df["operation_number"] = 1
    if "number_of_data_points" not in df.columns:
        df["number_of_data_points"] = 1

    # Iterate through the dataframe and update operation numbers
    for i in range(1, len(df)):
        if (df.index[i] - df.index[i - 1]).total_seconds() > 10800:
            operation_number += 1
            number_of_data_points = 1
        else:
            number_of_data_points += 1
        df.loc[df.index[i], "operation_number"] = operation_number
        df.loc[df.index[i], "number_of_data_points"] = number_of_data_points

        # Calculate elapsed time and estimated time remaining
        elapsed_time = time.time() - start_time

        # Improved progress message with time estimates
        print(
            f"Progress: {np.round(i / len(df) * 100, 3)}% complete | "
            f"Elapsed: {np.round(elapsed_time, 6)}s | ",
            end="\r"
        )

    return df


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        global df_all
        if event.is_directory:
            return
        if event.src_path.endswith(".csv"):
            print(f"New file detected: \033[1;91m{event.src_path}\033[0m\n")
            # Wait for the file to be fully written
            time.sleep(15)  # Adjust the delay as needed
            retries = 3
            for attempt in range(retries):
                try:
                    new_df = read_csv_file(event.src_path)
                    if new_df is not None:
                        new_df["Date"] = pd.to_datetime(new_df["Date"])
                        new_df = new_df.set_index("Date", inplace=False)
                        # Get the last operation number from the existing dataframe
                        last_operation_number = np.max(df_all["operation_number"].unique())
                        # Add the operation numbers to the new dataframe
                        new_df = add_operation_numbers(new_df, last_operation_number)
                        df_all = pd.concat([df_all, new_df])
                        df_all = df_all.sort_index()
                        print(f"Dataframe updated with new file: \033[1;32m {event.src_path}\033[0m\n")
                        # Recalculate operation numbers for the entire dataframe
                        # df_all = add_operation_numbers(df_all)
                        break
                    else:
                        print(f"File is empty or could not be read: {event.src_path}")
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for file {event.src_path}: {e}")
                    time.sleep(1)  # Wait before retrying
            else:
                print(f"Failed to read file after {retries} attempts: {event.src_path}")


def start_watching(target_folder):
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=target_folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Initialize Dash app
app = dash.Dash(__name__)


def create_app_layout(df_all):
    return html.Div(
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
            # Add a button to manually update the layout
            html.Button("Update Layout", id="update-layout-button", n_clicks=0, style={"margin": "10px"}),
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
                    ),
                    dcc.Checklist(
                        id="channel_value_checklist",
                        options=[
                            {"label": "Channel Min", "value": "channel_min"},
                            {"label": "Channel Max", "value": "channel_max"},
                        ]
                        ,
                        inline=True,
                        value=["channel_min", "channel_max"],
                        style={"color": "white"},
                    ),
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
                        options=[{"label": f"Operation {i}", "value": i} for i in range(1, len(df_all["operation_number"].unique()) + 1)],
                        # Set the default value to the last operation number
                        value=df_all["operation_number"].unique()[-1],
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
        Input("channel_value_checklist", "value"),
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
    channel_value_checklist,
    operation_number_dropdown,
    is_commanded_checkbox,
    lin_correction_checkbox,
    zmin,
    zmax,
    nbins,
):
    # Filter data based on operation number
    df_all_filtered = df_all[df_all["operation_number"] == operation_number_dropdown]

    # Define default min/max values
    default_min, default_max = 1.3, 3.3
    override_min, override_max = 0, 4.51

    # Map channel names to min/max values
    channel_limits = {
        "Channel1": [min_value_channel1, max_value_channel1],
        "Channel2": [min_value_channel2, max_value_channel2],
        "Channel3": [min_value_channel3, max_value_channel3],
        "Channel4": [min_value_channel4, max_value_channel4],
    }

    # Update limits based on user selection
    for channel, limits in channel_limits.items():
        if limits[0] is None:
            limits[0] = override_min if "channel_min" in channel_value_checklist else default_min
        if limits[1] is None:
            limits[1] = override_max if "channel_max" in channel_value_checklist else default_max

    # Unpack updated values
    min_value_channel1, max_value_channel1 = channel_limits["Channel1"]
    min_value_channel2, max_value_channel2 = channel_limits["Channel2"]
    min_value_channel3, max_value_channel3 = channel_limits["Channel3"]
    min_value_channel4, max_value_channel4 = channel_limits["Channel4"]

    # Filter the data based on the min and max values of each channel
    df_all_filtered = df_all_filtered[df_all_filtered["Channel1"].between(min_value_channel1, max_value_channel1) & df_all_filtered["Channel2"].between(min_value_channel2, max_value_channel2) & df_all_filtered["Channel3"].between(min_value_channel3, max_value_channel3) & df_all_filtered["Channel4"].between(min_value_channel4, max_value_channel4)]

    # Filter the data based on the IsCommanded event
    if "is_commanded" in is_commanded_checkbox:
        df_all_filtered = df_all_filtered
    else:
        df_all_filtered = df_all_filtered[~df_all_filtered["IsCommanded"]]

    if "Channel1" and "Channel3" in channel_checklist:
        x_channel, y_channel = "Channel1", "Channel3"
        x_data = df_all_filtered[x_channel]
        y_data = df_all_filtered[y_channel]

        # If zmin and zmax are not provided, set them to 1 and 120 respectively
        if zmin is None:
            zmin = 1
        if zmax is None:
            zmax = 120
        if nbins is None:
            nbins = 50
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
        Input("channel_value_checklist", "value"),
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
    channel_value_checklist,
    operation_number_dropdown,
    is_commanded_checkbox,
    lin_correction_checkbox,
    zmin,
    zmax,
    nbins,
):
    # Filter data based on operation number
    df_all_filtered = df_all[df_all["operation_number"] == operation_number_dropdown]

    # Define default min/max values
    default_min, default_max = 1.3, 3.3
    override_min, override_max = 0, 4.51

    # Map channel names to min/max values
    channel_limits = {
        "Channel1": [min_value_channel1, max_value_channel1],
        "Channel2": [min_value_channel2, max_value_channel2],
        "Channel3": [min_value_channel3, max_value_channel3],
        "Channel4": [min_value_channel4, max_value_channel4],
    }

    # Update limits based on user selection
    for channel, limits in channel_limits.items():
        if limits[0] is None:
            limits[0] = override_min if "channel_min" in channel_value_checklist else default_min
        if limits[1] is None:
            limits[1] = override_max if "channel_max" in channel_value_checklist else default_max

    # Unpack updated values
    min_value_channel1, max_value_channel1 = channel_limits["Channel1"]
    min_value_channel2, max_value_channel2 = channel_limits["Channel2"]
    min_value_channel3, max_value_channel3 = channel_limits["Channel3"]
    min_value_channel4, max_value_channel4 = channel_limits["Channel4"]

    # Filter the data based on the min and max values of each channel
    df_all_filtered = df_all_filtered[df_all_filtered["Channel1"].between(min_value_channel1, max_value_channel1) & df_all_filtered["Channel2"].between(min_value_channel2, max_value_channel2) & df_all_filtered["Channel3"].between(min_value_channel3, max_value_channel3) & df_all_filtered["Channel4"].between(min_value_channel4, max_value_channel4)]


    # Filter the data based on the IsCommanded event
    if "is_commanded" in is_commanded_checkbox:
        df_all_filtered = df_all_filtered
    else:
        df_all_filtered = df_all_filtered[~df_all_filtered["IsCommanded"]]

    if "Channel2" and "Channel4" in channel_checklist:
        x_channel, y_channel = "Channel2", "Channel4"
        x_data = df_all_filtered[x_channel]
        y_data = df_all_filtered[y_channel]

        threshold = 5

        # If zmin and zmax are not provided, set them to 1 and 120 respectively
        if zmin is None:
            zmin = 1
        if zmax is None:
            zmax = 120
        if nbins is None:
            nbins = 50

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
        )

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
        Input("channel_value_checklist", "value"),
        Input("operation_number_dropdown", "value"),
        Input("is_commanded_checkbox", "value"),
        Input("lin_correction_checkbox", "value"),
        Input("zmin", "value"),
        Input("zmax", "value"),
        Input("nbins", "value"),
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
    channel_value_checklist,
    operation_number_dropdown,
    is_commanded_checkbox,
    lin_correction_checkbox,
    zmin,
    zmax,
    nbins,
):
    # Filter the data based on the operation number
    df_all_filtered = df_all[df_all["operation_number"] == operation_number_dropdown]

    # Define default min/max values
    default_min, default_max = 1.3, 3.3
    override_min, override_max = 0, 4.51

    # Map channel names to min/max values
    channel_limits = {
        "Channel1": [min_value_channel1, max_value_channel1],
        "Channel2": [min_value_channel2, max_value_channel2],
        "Channel3": [min_value_channel3, max_value_channel3],
        "Channel4": [min_value_channel4, max_value_channel4],
    }

    # Update limits based on user selection
    for channel, limits in channel_limits.items():
        if limits[0] is None:
            limits[0] = override_min if "channel_min" in channel_value_checklist else default_min
        if limits[1] is None:
            limits[1] = override_max if "channel_max" in channel_value_checklist else default_max

    # Unpack updated values
    min_value_channel1, max_value_channel1 = channel_limits["Channel1"]
    min_value_channel2, max_value_channel2 = channel_limits["Channel2"]
    min_value_channel3, max_value_channel3 = channel_limits["Channel3"]
    min_value_channel4, max_value_channel4 = channel_limits["Channel4"]

    # Filter the data based on the min and max values of each channel
    df_all_filtered = df_all_filtered[df_all_filtered["Channel1"].between(min_value_channel1, max_value_channel1) & df_all_filtered["Channel2"].between(min_value_channel2, max_value_channel2) & df_all_filtered["Channel3"].between(min_value_channel3, max_value_channel3) & df_all_filtered["Channel4"].between(min_value_channel4, max_value_channel4)]


    # Filter the data based on the IsCommanded event
    if "is_commanded" in is_commanded_checkbox:
        df_all_filtered = df_all_filtered
    else:
        df_all_filtered = df_all_filtered[~df_all_filtered["IsCommanded"]]

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
    # Define the tick values dynamically using log scale
    tickvals = np.logspace(np.log10(zmin), np.log10(zmax), num=4)
    ticktext = [str(int(i)) for i in tickvals]

    hist, x_edges, y_edges = np.histogram2d(df_all_filtered[x_plot_key], df_all_filtered[y_plot_key], bins=nbins)
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

    x_counts, x_bins = np.histogram(df_all_filtered[x_plot_key], bins=100)
    y_counts, y_bins = np.histogram(df_all_filtered[y_plot_key], bins=100)

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


# Callback to update the app layout when the button is clicked
@app.callback(
    Output("app-layout", "children"),
    [Input("update-layout-button", "n_clicks")],
    [State("app-layout", "children")]
)
def update_layout(n_clicks, current_layout):
    global df_all
    return create_app_layout(df_all)


if __name__ == "__main__":
    # Load initial data
    target_folder = check_folder_structure()
    if target_folder:
        df_all = read_sci_l1c_data(target_folder)
        # If the maximum value of operation number is not 1, add operation numbers
        df_all = add_operation_numbers(df_all)

        # Set the initial app layout
        app.layout = html.Div(id="app-layout", children=create_app_layout(df_all))

        # Start the file watcher in a separate thread
        watcher_thread = threading.Thread(target=start_watching, args=(target_folder,))
        watcher_thread.daemon = True
        watcher_thread.start()

        # Run the Dash app
        host = "127.0.0.5"
        port = "8050"
        app.run_server(host=host, port=port, debug=False)
        print(f"Running on http://{host}:{port}/")
