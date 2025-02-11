import numpy as np
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import matplotlib.dates as mdates
from pathlib import Path
import glob
import pandas as pd
from matplotlib.ticker import FormatStrFormatter, MaxNLocator
from matplotlib.scale import FuncScale


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


def read_sci_l1c_data():
    parent_folder = check_folder_structure()
    print(f"Reading data from: {parent_folder}\n")

    file_name_format = "lexi_payload_*_*_*_*_sci_output_L1c.csv"
    csv_files = np.sort(glob.glob(str(parent_folder / "**" / file_name_format), recursive=True))

    print(f"Found \033[1;31m{len(csv_files)}\033[0m CSV files in the {parent_folder}\n")

    df_list = []
    for i, csv_file in enumerate(csv_files[0:2]):
        # Print the progress
        print(f"Reading file ==> \x1b[1;32;255m {np.round(i / len(csv_files) * 100, 3)}\x1b[0m % complete", end="\r")
        df = pd.read_csv(csv_file)
        df_list.append(df)

    df_all = pd.concat(df_list)
    print(df_all.head())

    # Set the Date column as the index
    df_all["Date"] = pd.to_datetime(df_all["Date"])
    # Set the timezones to UTC
    # df_all["Date"] = df_all["Date"].dt.tz_localize("UTC")
    df_all = df_all.set_index("Date", inplace=False)

    print(df_all.head())

    return df_all


read_data = False
if read_data:
    # Check the folder structure
    df = read_sci_l1c_data()
    # Add operation number to the data
    df["operation_number"] = 1
    df["number_of_data_points"] = 1
    operation_number = 1
    number_of_data_points = 1

    for i in range(1, len(df)):
        if (df.index[i] - df.index[i - 1]).total_seconds() > 10800:
            operation_number += 1
            number_of_data_points = 1
        else:
            number_of_data_points += 1
        df.loc[df.index[i], "number_of_data_points"] = number_of_data_points
        df.loc[df.index[i], "operation_number"] = operation_number

        # Print the progress
        print(f"Adding operation number ==> \x1b[1;32;255m {np.round(i / len(df) * 100, 6)}\x1b[0m % complete", end="\r")


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
                    value=["Channel1", "", "Channel3", ""],
                    style={"color": "white"},
                )
            ],
        ),
        # Add the input boxes for minimum and maximum value of each channel
        html.Div(
            style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center"},
            children=[
                dcc.Input(id="min_value_channel_1", type="number", placeholder="Min Value", style={"color": "black"}),
                dcc.Input(id="max_value_channel_1", type="number", placeholder="Max Value", style={"color": "black"}),
                dcc.Input(id="min_value_channel_2", type="number", placeholder="Min Value", style={"color": "black"}),
                dcc.Input(id="max_value_channel_2", type="number", placeholder="Max Value", style={"color": "black"}),
                dcc.Input(id="min_value_channel_3", type="number", placeholder="Min Value", style={"color": "black"}),
                dcc.Input(id="max_value_channel_3", type="number", placeholder="Max Value", style={"color": "black"}),
                dcc.Input(id="min_value_channel_4", type="number", placeholder="Min Value", style={"color": "black"}),
                dcc.Input(id="max_value_channel_4", type="number", placeholder="Max Value", style={"color": "black"}),
            ],
        ),

        # Add the dropdown menu for to select the operation number
        html.Div(
            style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center"},
            children=[
                dcc.Dropdown(
                    id="operation_number_dropdown",
                    options=[{"label": f"Operation {i}", "value": i} for i in range(1, operation_number + 1)],
                    value=1,
                    className="dark-dropdown",
                    style={"width": "50%", "marginBottom": "2px", "marginTop": "2px", "marginLeft": "5px", "marginRight": "5px"},
                )
            ],
        ),
        # Add a checkbox for "IsCommanded" event to be considered or not
        html.Div(
            style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center"},
            children=[
                dcc.Checklist(
                    id="is_commanded_checkbox",
                    options=[{"label": "IsCommanded", "value": "is_commanded"}],
                    value=[],
                    style={"color": "white"},
                )
            ],
        ),
        # Add a checkbox for "lin_correction" to be applied or not
        html.Div(
            style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center"},
            children=[
                dcc.Checklist(
                    id="lin_correction_checkbox",
                    options=[{"label": "Linear Correction", "value": "lin_correction"}],
                    value=[],
                    style={"color": "white"},
                )
            ],
        ),
        # Add the graph
        dcc.Graph(id="line_plot", style={"height": "70vh", "width": "95vw", "overflow": "hidden"}),
    ],
)


@app.callback(
    Output("line_plot", "figure"),
    [
        Input("channel_checklist", "value"),
        Input("min_value_channel_1", "value"),
        Input("max_value_channel_1", "value"),
        Input("min_value_channel_2", "value"),
        Input("max_value_channel_2", "value"),
        Input("min_value_channel_3", "value"),
        Input("max_value_channel_3", "value"),
        Input("min_value_channel_4", "value"),
        Input("max_value_channel_4", "value"),
        Input("operation_number_dropdown", "value"),
        Input("is_commanded_checkbox", "value"),
        Input("lin_correction_checkbox", "value"),
    ],
)
def update_graph(
    channel_checklist,
    min_value_channel_1,
    max_value_channel_1,
    min_value_channel_2,
    max_value_channel_2,
    min_value_channel_3,
    max_value_channel_3,
    min_value_channel_4,
    max_value_channel_4,
    operation_number_dropdown,
    is_commanded_checkbox,
    lin_correction_checkbox,
):
    # Filter the data based on the operation number
    df_filtered = df[df["operation_number"] == operation_number_dropdown]

    # Filter the data based on the IsCommanded event
    if "is_commanded" in is_commanded_checkbox:
        df_filtered = df_filtered
    else:
        df_filtered = df_filtered[~df_filtered["IsCommanded"]]

    # Apply linear correction
    if "lin_correction" in lin_correction_checkbox:
        df_filtered["Channel_1"] = df_filtered["Channel_1"] * 2

    # Create a figure
    fig = px.line(df_filtered, x=df_filtered.index, y=channel_checklist, title="Line Plot")

    # Update the x-axis
    fig.update_xaxes(title_text="Date", tickformat="%H:%M:%S", tickangle=45, tickfont=dict(size=10), showgrid=True, gridwidth=1, gridcolor="gray")

    # Update the y-axis
    fig.update_yaxes(title_text="Value", showgrid=True, gridwidth=1, gridcolor="gray")

    return fig


if __name__ == "__main__":
    host = "127.0.0.5"
    port = "8050"
    app.run_server(host=host, port=port, debug=False)
    print(f"Running on http://{host}:{port}/")