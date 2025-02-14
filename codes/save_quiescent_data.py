import pandas as pd
import plotly.express as px
import colorsys
import numpy as np
from pathlib import Path
import download_and_plot_data as dapd
import importlib

from builtins import min, max

importlib.reload(dapd)

# Load the DataFrame from the pickled file
read_data = False
if read_data:
    df = dapd.get_data_dataframes()
    # Add HV_value column to df
    df["HV_value"] = df["AnodeVoltMon"] * 599
    input_key_unit = "-"
    df["operation_number"] = "Quiescent"
    df["DateTime"] = df.index
    unique_operations = sorted(df["operation_number"].unique())

    available_columns = list(df.columns)
    default_columns = [available_columns[3]]  # Default to first column

    # Save the DataFrame to a pickled file
    df.to_pickle("../data/from_LEXI/quiescent_data/processed_data.pkl")
else:
    df = pd.read_pickle("../data/from_LEXI/quiescent_data/processed_data.pkl")

input_key_unit = "-"
df.index = pd.to_datetime(df.index)
available_columns = list(df.columns)
default_columns = [available_columns[3], available_columns[5]]  # Default to first column
unique_operations = sorted(df["operation_number"].unique())

# Assign unique base colors for columns
column_colors = {
    column: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
    for i, column in enumerate(available_columns)
}


def adjust_color_brightness(hex_color, factor):
    """Darkens or lightens a color based on the factor"""
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    hls = colorsys.rgb_to_hls(*rgb)
    adjusted_rgb = colorsys.hls_to_rgb(hls[0], min(1, max(0, hls[1] * factor)), hls[2])
    return f"#{int(adjusted_rgb[0] * 255):02x}{int(adjusted_rgb[1] * 255):02x}{int(adjusted_rgb[2] * 255):02x}"


# Define a plot key list
plot_key_list = ["PinPullerTemp", "LEXIbaseTemp", "HVsupplyTemp", "+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon"]

# Define the parameters for the plot
selected_operations = [unique_operations[-1]]
selected_columns = default_columns
filtering_length = 15
hv_threshold_low = 0
hv_threshold_high = 2100
hv_threshold_check = ["hv_threshold"]
log_scale_check = []

# Loop through each key in the plot_key_list
for key in plot_key_list:
    if key not in available_columns:
        print(f"Key '{key}' not found in available columns. Skipping...")
        continue

    # Generate the figure for the current key
    fig = px.line(template="plotly_dark")

    df[f"{key}_smooth"] = df[key].rolling(f"{filtering_length}s", center=False).mean()
    filtered_df = df[df["operation_number"].isin(selected_operations)]
    filtered_df = filtered_df[(filtered_df["HV_value"] > hv_threshold_low) & (filtered_df["HV_value"] < hv_threshold_high)][filtering_length:-filtering_length]

    filtered_df[key] = filtered_df[key].round(2)
    base_color = column_colors[key]
    filtered_df["DateTime"] = filtered_df.index.strftime("%Y-%m-%d %H:%M:%S.%f")

    if "log_scale" in log_scale_check:
        filtered_df = filtered_df[filtered_df[key] > 0]

    for i, op in enumerate(selected_operations):
        temp_df = filtered_df[filtered_df["operation_number"] == op].reset_index(drop=True)
        temp_df["event_number"] = temp_df.index
        shade_factor = 1 - (i * 0.15) if (i * 0.15) < 1 else 0.85
        color_shade = adjust_color_brightness(base_color, shade_factor)
        y_axis = "y"

        hover_data = {key: True, "event_number": False, f"{key}_smooth": False, "DateTime": False, "operation_number": False, "Date": False}
        temp_fig = px.line(
            temp_df,
            x="Date",
            y=f"{key}_smooth",
            labels={"Date": "Date"},
            color_discrete_sequence=[color_shade],
            hover_data=hover_data,
        )
        for trace in temp_fig["data"]:
            trace["name"] = f"{key} - Operation {op}"
            trace["line"]["color"] = color_shade
            trace["yaxis"] = y_axis
            fig.add_trace(trace)

    fig.update_layout(
        plot_bgcolor="#121212",
        paper_bgcolor="#121212",
        font={"color": "white"},
        xaxis=dict(title="Date", title_font=dict(size=20)),
        yaxis=dict(
            title=f"{key} {input_key_unit}",
            title_font=dict(size=20),
            showline=True,
            linewidth=2,
            linecolor=column_colors[key],
            type="log" if "log_scale" in log_scale_check else "linear",
        ),
        hovermode="x unified",
    )

    fig.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
    fig.update_yaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")

    # Get the current time and add it to the title
    current_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.update_layout(title=f"{key} Operations - {'_'.join(map(str, selected_operations))} - {current_time}")
    # Save the figure
    fig_name = f"{key}_Operations_{'_'.join(map(str, selected_operations))}"
    folder_name = "~/Dropbox/quiescent_mode_figures/"
    # Expand the folder name
    folder_name = Path(folder_name).expanduser().resolve()
    # Save the figure
    fig.write_html(f"{folder_name}/{fig_name}_plot.html")
    print(f"Figure saved as \033[1;32m{fig_name}_plot.html\033[0m at \033[1;91m{current_time}\033[0m\n \n")
