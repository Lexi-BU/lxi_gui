import colorsys
import importlib
import time
from builtins import max, min
from pathlib import Path

import download_and_plot_data as dapd
import numpy as np
import pandas as pd
import plotly.express as px

importlib.reload(dapd)


# Function to encapsulate the main logic
def main():
    # Load the DataFrame from the pickled file
    read_data = True

    if read_data:
        df, t_start, t_end = dapd.get_data_dataframes(
            download_data=False, time_threshold=30, all_files=True
        )
        # Add HV_value column to df
        df["HV_value"] = df["AnodeVoltMon"] * 599
        input_key_unit = "-"
        df["operation_number"] = "Quiescent"
        df["DateTime"] = df.index
        unique_operations = sorted(df["operation_number"].unique())

        available_columns = list(df.columns)
        default_columns = [available_columns[3]]  # Default to first column
        # Sort the DataFrame by the index
        df = df.sort_index()
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
    plot_key_list = [
        "PinPullerTemp",
        "LEXIbaseTemp",
        "HVsupplyTemp",
        "+5.2V_Imon",
        "+10V_Imon",
        "+3.3V_Imon",
        "AnodeVoltMon",
        "+28V_Imon",
        "DeltaEvntCount",
        "DeltaDroppedCount",
        "DeltaLostEvntCount",
        "HV_value",
    ]

    # Define the parameters for the plot
    selected_operations = [unique_operations[-1]]
    selected_columns = default_columns
    filtering_length = 120
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

        # Ignore all values that are less than 0
        df[key] = df[key].apply(lambda x: x if x > 0 else np.nan)
        df[f"{key}_smooth"] = df[key].rolling(f"{filtering_length}s", center=False).mean()
        filtered_df = df[df["operation_number"].isin(selected_operations)]
        filtered_df = filtered_df[
            (filtered_df["HV_value"] > hv_threshold_low)
            & (filtered_df["HV_value"] < hv_threshold_high)
        ][filtering_length:-filtering_length]

        filtered_df[key] = filtered_df[key].round(2)
        base_color = column_colors[key]
        filtered_df["DateTime"] = filtered_df.index.strftime("%Y-%m-%d %H:%M:%S.%f")

        # if "log_scale" in log_scale_check:
        filtered_df = filtered_df[filtered_df[key] > 0]
        # Select only those smooth key values that are greater than 0
        # if key == "PinPullerTemp":
        #     filtered_df = filtered_df[filtered_df[f"{key}"] > 0]
        #     filtered_df = filtered_df[filtered_df[f"{key}_smooth"] > 50]

        for i, op in enumerate(selected_operations):
            temp_df = filtered_df[filtered_df["operation_number"] == op].reset_index(drop=True)
            temp_df["event_number"] = temp_df.index
            shade_factor = 1 - (i * 0.15) if (i * 0.15) < 1 else 0.85
            color_shade = adjust_color_brightness(base_color, shade_factor)
            y_axis = "y"

            hover_data = {
                key: True,
                "event_number": False,
                f"{key}_smooth": False,
                "DateTime": False,
                "operation_number": False,
                "Date": False,
            }
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
        # Increase the tick label font size
        fig.update_xaxes(tickfont=dict(size=20))
        fig.update_yaxes(tickfont=dict(size=20))
        # Get the median value of the key and its maximum and minimum values
        median_value = filtered_df[key].median()
        max_value = filtered_df[key].max()
        min_value = filtered_df[key].min()

        # Add the median, maximum and minimum values to the figure at top left
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.98,
            text=f"Median: {median_value:.2f}<br>Max: {max_value:.2f}<br>Min: {min_value:.2f}",
            showarrow=False,
            font=dict(size=22, color="white"),
            bgcolor="#121212",
            bordercolor="#121212",
            borderwidth=1,
        )

        fig.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
        fig.update_yaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")

        t_start_time = filtered_df.index[0].strftime("%Y-%m-%d %H:%M:%S")
        t_end_time = filtered_df.index[-1].strftime("%Y-%m-%d %H:%M:%S")
        # Get the current time and add it to the title
        current_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.update_layout(
            title=(
                f"{key} - [{'_'.join(map(str, selected_operations))}] Data from "
                f"<span style='color: green;'>{t_start_time}</span> to "
                f"<span style='color: red;'>{t_end_time}</span> (Figure updated at "
                f"<span style='color: magenta;'>{current_time}</span> [ET])"
            ),
            title_font=dict(size=24),
        )
        # Save the figure
        fig_name = f"{key}_Operations_{'_'.join(map(str, selected_operations))}_since_start"
        folder_name = "~/Dropbox/quiescent_mode_figures/since_start/"
        # Expand the folder name
        folder_name = Path(folder_name).expanduser().resolve()
        # Create the folder if it doesn't exist
        folder_name.mkdir(parents=True, exist_ok=True)
        # Save the figure
        fig.write_html(f"{folder_name}/{fig_name}_plot.html")
        # Save figures as png as well
        fig.write_image(f"{folder_name}/{fig_name}_plot.png", width=1920, height=1080)
        print(
            f"Figure saved as \033[1;32m{fig_name}_plot.html\033[0m at \033[1;91m{current_time}\033[0m\n \n"
        )


# Run the main function every 5 minutes
while True:
    try:
        main()
        time.sleep(10)  # Sleep for 15 minutes (900 seconds)
    except Exception:
        time.sleep(10)
