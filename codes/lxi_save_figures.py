import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import global_variables
import matplotlib.dates as mdates
from pathlib import Path
import glob
import re
import pandas as pd


def save_figures(df=None, start_time=None, end_time=None):

    # Get the Sliced Housekeeping Data from the global variable
    df = global_variables.all_file_details["df_slice_hk"]

    # Filter the data to get the data between the start and end time
    df = df.loc[start_time:end_time]

    # Get the Sliced Science Data from the global variable
    df_sci = global_variables.all_file_details["df_all_sci"]

    # Filter the data to get the data between the start and end time
    df_sci = df_sci.loc[start_time:end_time]

    start_time = df_sci.index[0]
    end_time = df_sci.index[-1]

    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # In global_variables, if hv_status is not defined, set it to False
    if "hv_status" not in global_variables.__dict__:
        global_variables.hv_status = False
    # From the indices of df, get the start and end time
    start_time = df.index[0]
    end_time = df.index[-1]

    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    default_key_list = [
        "HVsupplyTemp",
        "LEXIbaseTemp",
        "PinPullerTemp",
        "+3.3V_Imon",
        "+5.2V_Imon",
        "+10V_Imon",
        "+28V_Imon",
        "AnodeVoltMon",
        "DeltaEvntCount",
    ]

    # Make a dictionary of all the plot options and their units
    unit_dict = {
        "HK_id": "#",
        "PinPullerTemp": "(C)",
        "OpticsTemp": "(C)",
        "LEXIbaseTemp": "(C)",
        "HVsupplyTemp": "(C)",
        "+5.2V_Imon": "(mA)",
        "+10V_Imon": "(mA*)",
        "+3.3V_Imon": "(mA)",
        "AnodeVoltMon": "(V*)",
        "+28V_Imon": "(mA)",
        "ADC_Ground": "(V)",
        "Cmd_count": "#",
        "Pinpuller_Armed": "",
        "HVmcpAuto": "",
        "HVmcpMan": "",
        "DeltaEvntCount": "#",
        "DeltaDroppedCount": "#",
        "DeltaLostevntCount": "#",
    }
    nominal_values_dict_hv_on = {
        "PinPullerTemp": "-10 to 50",
        "OpticsTemp": "-10 to 50",
        "LEXIbaseTemp": "-10 to 50",
        "HVsupplyTemp": "-10 to 50",
        "+5.2V_Imon": "$68 \pm 0.5$",
        "+10V_Imon": "$2.5 \pm 0.4$",
        "+3.3V_Imon": "$42.5 \pm 0.5$",
        "AnodeVoltMon": "$3.4 \pm 0.6$",
        "+28V_Imon": "$57.6 \pm 2.2$",
        "DeltaDroppedCount": 0,
        "DeltaLostevntCount": 0,
    }
    nominal_values_dict_hv_off = {
        "PinPullerTemp": "-10 to 50",
        "OpticsTemp": "-10 to 50",
        "LEXIbaseTemp": "-10 to 50",
        "HVsupplyTemp": "-10 to 50",
        "+5.2V_Imon": "$61.5 \pm 0.5$",
        "+10V_Imon": "$0.15 \pm 0.0$",
        "+3.3V_Imon": "$47.7 \pm 0.1$",
        "AnodeVoltMon": "$0.0044 \pm 0.0$",
        "+28V_Imon": "$44.1 \pm 0.4$",
        "DeltaDroppedCount": 0,
        "DeltaLostevntCount": 0,
    }

    fontsize = 10

    # Set the font size for the plots
    font = {"family": "serif", "weight": "normal", "size": fontsize}
    plt.rc("font", **font)
    # Use dark background
    plt.style.use("dark_background")

    # Create a figure with 3 by 3 subplots
    fig, axs = plt.subplots(3, 3, figsize=(15, 6), sharex=True)
    fig.subplots_adjust(hspace=0.15, wspace=0.35, top=0.92)

    fig.suptitle(f"Housekeeping Data from {start_time} to {end_time}", fontsize=1.2 * fontsize,)

    # Plot the data
    for i, key in enumerate(default_key_list):
        # Get rid of NaN values
        df = df.dropna(subset=[key])
        # Get the 10th, 50th and 90th percentile values of the data
        key_10p_val = np.percentile(df[key], 10)
        key_50p_val = np.percentile(df[key], 50)
        key_90p_val = np.percentile(df[key], 90)

        row = i // 3
        col = i % 3

        axs[row, col].plot(df.index, df[key], ".", label=key, color="green", markersize=5, alpha=0.5,)
        axs[row, col].set_ylabel(f"{unit_dict[key]}")

        # Write the name of the key in the bottom right corner of the plot
        axs[row, col].text(
            0.98,
            0.02,
            key,
            horizontalalignment="right",
            verticalalignment="bottom",
            transform=axs[row, col].transAxes,
            color="white",
            fontsize=0.75 * fontsize,
            bbox=dict(facecolor="black", alpha=0.5),
        )

        # On the plot, display the 10, 50 and 90 percentile values of the data where mu is the mean
        # and the subscript is the 10th percentile value and the superscript is the 90th percentile
        # value
        axs[row, col].text(
            0.02,
            0.05,
            f"$\mu_{{{10}}}^{{{90}}}={key_50p_val:.2f}_{{{key_10p_val:.2f}}}^{{{key_90p_val:.2f}}}$",
            horizontalalignment="left",
            verticalalignment="bottom",
            transform=axs[row, col].transAxes,
            color="white",
            fontsize=0.75 * fontsize,
            bbox=dict(facecolor="black", alpha=0.5),
        )

        # Add a grid to the plot for better readability, separate the major and minor ticks
        axs[row, col].grid(which="major", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)
        axs[row, col].grid(which="minor", axis="both", color="c", linestyle="--", linewidth=0.2, alpha=0.5)

        try:
            if global_variables.hv_status:
                axs[row, col].text(
                    0.02,
                    0.95,
                    f"Nominal Value: {nominal_values_dict_hv_on[key]}",
                    horizontalalignment="left",
                    verticalalignment="top",
                    transform=axs[row, col].transAxes,
                    color="white",
                    fontsize=0.75 * fontsize,
                    bbox=dict(facecolor="black", alpha=0.5),
                )
            elif global_variables.hv_status is False:
                axs[row, col].text(
                    0.02,
                    0.95,
                    f"Nominal Value: {nominal_values_dict_hv_off[key]}",
                    horizontalalignment="left",
                    verticalalignment="top",
                    transform=axs[row, col].transAxes,
                    color="white",
                    fontsize=0.75 * fontsize,
                    bbox=dict(facecolor="black", alpha=0.5),
                )
        except Exception:
            pass

        # Put the tickmarks inside the plot
        axs[row, col].tick_params(axis="both", direction="in", length=8)
        # Put the tickmarks inside the plot for minor ticks
        axs[row, col].tick_params(axis="both", which="minor", direction="in", length=5)
        # Set the xlabel only if it is the last row
        if row == 2:
            # Format the x-axis to show the time
            axs[row, col].xaxis.set_major_locator(mdates.MinuteLocator(interval=20))

            # Set a 5-minute interval for minor tick marks
            axs[row, col].xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))

            # Format the x-axis to display labels only for major tick marks
            axs[row, col].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            # Ensure that the x-axis is readable
            plt.setp(axs[row, col].xaxis.get_majorticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            axs[row, col].set_xlabel("Time [UTC]", fontsize=fontsize)

        # Set the ylabel

    # Add HV status in the top right corner of the 0, 2 subplot
    axs[0, 2].text(
        0.97,
        1.05,
        "HV ON" if global_variables.hv_status else "HV OFF",
        transform=axs[0, 2].transAxes,
        horizontalalignment="right",
        verticalalignment="bottom",
        color="red" if global_variables.hv_status else "green",
        fontsize=fontsize,
        bbox=dict(facecolor="black", alpha=0.5),
    )

    # if global_variables.hv_status:
    #     fig.text(0.98, 0.98, "HV ON", horizontalalignment="right", verticalalignment="top", color="red", fontsize=fontsize, bbox=dict(facecolor="black", alpha=0.5),)
    # elif global_variables.hv_status is False:
    #     fig.text(0.98, 0.98, "HV OFF", horizontalalignment="right", verticalalignment="top", color="green", fontsize=fontsize, bbox=dict(facecolor="black", alpha=0.5),)
    # Save the figure as png file to the path
    default_folder = "../lxi_housekeeping_data/"
    Path(default_folder).mkdir(parents=True, exist_ok=True)
    # Expand the path to full path
    default_folder = Path(default_folder).expanduser()
    if global_variables.hv_status:
        # In the start and end time, replace the : with _ to avoid confusion with the file name
        start_time = start_time.replace(":", "_")
        end_time = end_time.replace(":", "_")
        # Replace space with _
        start_time = start_time.replace(" ", "_")
        end_time = end_time.replace(" ", "_")
        fig_name = f"lxi_housekeeping_data_{start_time}_{end_time}_hv_status_ON.png"
    else:
        # In the start and end time, replace the : with _ to avoid confusion with the file name
        start_time = start_time.replace(":", "_")
        end_time = end_time.replace(":", "_")
        # Replace space with _
        start_time = start_time.replace(" ", "_")
        end_time = end_time.replace(" ", "_")
        fig_name = f"lxi_housekeeping_data_{start_time}_{end_time}_hv_status_OFF.png"

    fig.savefig(default_folder / fig_name, dpi=300, bbox_inches="tight", pad_inches=0.1)
    # Close the figure
    plt.close(fig)
    print(f"Figure saved as {default_folder / fig_name}")
    """
    default_key_list = [
        "Channel1",
        "Channel2",
        "Channel3",
        "Channel4",
    ]

    fontsize = 15

    # Set the font size for the plots
    font = {"family": "serif", "weight": "normal", "size": fontsize}
    plt.rc("font", **font)
    # Use dark background
    plt.style.use("dark_background")
    # Plot the data in a 2 by 2 grid
    fig, axs = plt.subplots(2, 2, figsize=(18, 10), sharex=True, sharey=True)
    fig.subplots_adjust(hspace=0.05, wspace=0.05, top=0.92)

    fig.suptitle(f"Science Data from {start_time} to {end_time}", fontsize=1.2 * fontsize,)

    # Plot the data
    for i, key in enumerate(default_key_list):
        # Get rid of NaN values
        df_sci = df_sci.dropna(subset=[key])
        # Get the 10th, 50th and 90th percentile values of the data
        key_10p_val = np.percentile(df_sci[key], 10)
        key_50p_val = np.percentile(df_sci[key], 50)
        key_90p_val = np.percentile(df_sci[key], 90)

        row = i // 2
        col = i % 2

        axs[row, col].plot(df_sci.index, df_sci[key], ".", label=key, color="green", markersize=5, alpha=0.5,)
        axs[row, col].set_ylabel("Voltage [V]")

        # Write the name of the key in the bottom right corner of the plot
        axs[row, col].text(
            0.98,
            0.02,
            key,
            horizontalalignment="right",
            verticalalignment="bottom",
            transform=axs[row, col].transAxes,
            color="white",
            fontsize=fontsize,
            bbox=dict(facecolor="black", alpha=0.5),
        )

        # On the plot, display the 10, 50 and 90 percentile values of the data where mu is the mean
        # and the subscript is the 10th percentile value and the superscript is the 90th percentile
        # value
        axs[row, col].text(
            0.02,
            0.05,
            f"$\mu_{{{10}}}^{{{90}}}={key_50p_val:.2f}_{{{key_10p_val:.2f}}}^{{{key_90p_val:.2f}}}$",
            horizontalalignment="left",
            verticalalignment="bottom",
            transform=axs[row, col].transAxes,
            color="white",
            fontsize=1 * fontsize,
            bbox=dict(facecolor="black", alpha=0.5),
        )

        # Add a grid to the plot for better readability, separate the major and minor ticks
        axs[row, col].grid(which="major", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)
        axs[row, col].grid(which="minor", axis="both", color="c", linestyle="--", linewidth=0.2, alpha=0.5)

        # Put the tickmarks inside the plot
        axs[row, col].tick_params(axis="both", direction="in", length=8, left=True, right=True, top=True, bottom=True)
        # Put the tickmarks inside the plot for minor ticks
        axs[row, col].tick_params(axis="both", which="minor", direction="in", length=5, left=True, right=True, top=True, bottom=True)

        # Set the xlabel only if it is the last row
        if row == 1:
            # Format the x-axis to show the time
            axs[row, col].xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
            # Set a 5-minute interval for minor tick marks
            axs[row, col].xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))
            # Format the x-axis to display labels only for major tick marks
            axs[row, col].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            # Ensure that the x-axis is readable
            plt.setp(axs[row, col].xaxis.get_majorticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            axs[row, col].set_xlabel("Time [UTC]", fontsize=fontsize)
        # Set the ylabel on right side only if it is the last column
        if col == 1:
            axs[row, col].yaxis.set_label_position("right")
            axs[row, col].set_ylabel("Voltage [V]", fontsize=fontsize)
            # Show tick labels on the right side
            axs[row, col].tick_params(axis="both", which="both", direction="in", length=5, left=True, right=True, top=True, bottom=True, labelright=True, labelleft=False)

    # Save the figure as png file to the path
    default_folder = "../lxi_science_data/"
    Path(default_folder).mkdir(parents=True, exist_ok=True)
    # Expand the path to full path
    default_folder = Path(default_folder).expanduser()

    # In the start and end time, replace the : with _ to avoid confusion with the file name
    start_time = start_time.replace(":", "_")
    end_time = end_time.replace(":", "_")
    # Replace space with _
    start_time = start_time.replace(" ", "_")
    end_time = end_time.replace(" ", "_")
    fig_name = f"lxi_science_data_{start_time}_{end_time}.png"

    fig.savefig(default_folder / fig_name, dpi=300, bbox_inches="tight", pad_inches=0.1)

    print(f"Figure saved as {default_folder / fig_name}")

    long_time_series_plot()

    print("Long term time series plot saved.")
    """
    fontsize = 18
    label_factor = 1.3
    linewidth = 4.5
    mincnt = 1

    # Compute the pulse height by adding all 4 channels together
    df_sci["PulseHeight"] = df_sci["Channel1"] + df_sci["Channel2"] + df_sci["Channel3"] + df_sci["Channel4"]

    # Set the font size for the plots
    font = {"family": "serif", "weight": "normal", "size": fontsize}
    plt.rc("font", **font)
    # Use dark background
    plt.style.use("dark_background")
    # Plot the data in a 2 by 3 grid
    fig, axs = plt.subplots(3, 3, figsize=(24, 15), sharex=False, sharey=False)
    fig.subplots_adjust(hspace=0.15, wspace=0.35, top=0.95)

    fig.suptitle(f"Science Data from {start_time} to {end_time}", fontsize=1.2 * fontsize,)
    # Plot the distribution of Channel 1
    axs[0, 0].hist(df_sci["Channel1"], bins=50, color="#42f5bc", alpha=0.5, log=True, histtype="step", linewidth=linewidth)
    axs[0, 0].set_ylabel("Frequency", fontsize=fontsize)
    axs[0, 0].set_xlabel("Voltage [V]", fontsize=fontsize, labelpad=-45)
    # axs[0, 0].set_xlabel("Channel 1 [V]", fontsize=fontsize)
    axs[0, 0].set_yscale("log")
    axs[0, 0].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)
    # Add a text at the top right corner of the plot that says Channel 1
    axs[0, 0].text(
        0.98,
        0.98,
        "Channel 1",
        horizontalalignment="right",
        verticalalignment="top",
        transform=axs[0, 0].transAxes,
        color="#42f5bc",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.5),
    )

    # Plot the distribution of Channel 2
    axs[1, 0].hist(df_sci["Channel2"], bins=50, color="#42cef5", alpha=0.5, log=True, histtype="step", linewidth=linewidth)
    axs[1, 0].set_ylabel("Frequency", fontsize=fontsize)
    # Add x-label (inside the plot)
    axs[1, 0].set_xlabel("Voltage [V]", fontsize=fontsize, labelpad=-45)
    # axs[0, 1].set_xlabel("Channel 2 [V]", fontsize=fontsize)
    axs[1, 0].set_yscale("log")
    axs[1, 0].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)
    # Add a text at the top right corner of the plot that says Channel 2
    axs[1, 0].text(
        0.98,
        0.98,
        "Channel 2",
        horizontalalignment="right",
        verticalalignment="top",
        transform=axs[1, 0].transAxes,
        color="#42cef5",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.5),
    )

    # Plot the distribution of Channel 3
    axs[0, 1].hist(df_sci["Channel3"], bins=50, color="#f542ef", alpha=0.5, log=True, histtype="step", linewidth=linewidth)
    axs[0, 1].set_ylabel("Frequency", fontsize=fontsize)
    axs[0, 1].set_xlabel("Voltage [V]", fontsize=fontsize, labelpad=-45)
    # axs[1, 0].set_xlabel("Channel 3 [V]", fontsize=fontsize)
    axs[0, 1].set_yscale("log")
    axs[0, 1].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)
    # Add a text at the top right corner of the plot that says Channel 3
    axs[0, 1].text(
        0.98,
        0.98,
        "Channel 3",
        horizontalalignment="right",
        verticalalignment="top",
        transform=axs[0, 1].transAxes,
        color="#f542ef",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.5),
    )

    # Plot the distribution of Channel 4
    axs[1, 1].hist(df_sci["Channel4"], bins=50, color="#f5a742", alpha=0.5, log=True, histtype="step", linewidth=linewidth)
    axs[1, 1].set_ylabel("Frequency", fontsize=fontsize)
    axs[1, 1].set_xlabel("Voltage [V]", fontsize=fontsize, labelpad=-45)
    # axs[1, 1].set_xlabel("Channel 4 [V]", fontsize=fontsize)
    axs[1, 1].set_yscale("log")
    axs[1, 1].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)
    # Add a text at the top right corner of the plot that says Channel 4
    axs[1, 1].text(
        0.98,
        0.98,
        "Channel 4",
        horizontalalignment="right",
        verticalalignment="top",
        transform=axs[1, 1].transAxes,
        color="#f5a742",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.5),
    )

    # Plot the hexbin plot of Channel 1 and Channel 3
    axs[0, 2].hexbin(df_sci["Channel1"], df_sci["Channel3"], gridsize=50, cmap="inferno", alpha=1, norm=mpl.colors.LogNorm(vmin=mincnt),)
    # Set equal aspect ratio
    axs[0, 2].set_aspect('equal', adjustable='box')
    axs[0, 2].set_xlabel("Channel 1 [V]", fontsize=fontsize)
    axs[0, 2].set_ylabel("Channel 3 [V]", fontsize=fontsize)
    # Display the colorbar
    cb = plt.colorbar(axs[0, 2].collections[0], ax=axs[0, 2], orientation="vertical", pad=0.01, aspect=40, shrink=0.85, fraction=0.25, label="Frequency", extend="max", extendfrac=0.1, extendrect=True, location="right")
    cb.ax.xaxis.set_label_position("top")
    axs[0, 2].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)

    # Plot the hexbin plot of Channel 2 and Channel 4
    axs[1, 2].hexbin(df_sci["Channel2"], df_sci["Channel4"], gridsize=50, cmap="inferno", alpha=1, norm=mpl.colors.LogNorm(vmin=mincnt),)
    axs[1, 2].set_xlabel("Channel 2 [V]", fontsize=fontsize)
    axs[1, 2].set_ylabel("Channel 4 [V]", fontsize=fontsize)
    # Set equal aspect ratio
    axs[1, 2].set_aspect('equal', adjustable='box')
    # Display the colorbar
    cb = plt.colorbar(axs[1, 2].collections[0], ax=axs[1, 2], orientation="vertical", pad=0.01, aspect=40, shrink=0.85, fraction=0.25, label="Frequency", extend="max", extendfrac=0.1, extendrect=True, location="right")
    cb.ax.xaxis.set_label_position("top")
    axs[1, 2].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)

    # Plot the distribution of Pulse Height
    axs[2, 0].hist(df_sci["PulseHeight"], bins=50, color="w", alpha=0.5, log=True, histtype="step", linewidth=linewidth)
    axs[2, 0].set_ylabel("Frequency", fontsize=fontsize)
    axs[2, 0].set_xlabel("Voltage [V]", fontsize=fontsize, labelpad=-45)
    # axs[2, 0].set_xlabel("Pulse Height [V]", fontsize=fontsize)
    axs[2, 0].set_yscale("log")
    # Turn on the grid
    axs[2, 0].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)
    # Add a text at the top right corner of the plot that says Pulse Height
    axs[2, 0].text(
        0.98,
        0.98,
        "Pulse Height",
        horizontalalignment="right",
        verticalalignment="top",
        transform=axs[2, 0].transAxes,
        color="w",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.5),
    )

    # Select only the data where x_mcp_lin and y_mcp_lin are withing +/- 6
    df_sci = df_sci[(df_sci["x_mcp_lin"] < 6) & (df_sci["x_mcp_lin"] > -6) & (df_sci["y_mcp_lin"] < 6) & (df_sci["y_mcp_lin"] > -6)]
    # Plot the hexbin historagram of between "x_mcp_lin" and "y_mcp_lin". Ignore any bins where the
    # number of points is less than 10
    axs[2, 2].hexbin(df_sci["x_mcp_lin"], df_sci["y_mcp_lin"], gridsize=50, cmap="plasma", alpha=1, mincnt=mincnt, norm=mpl.colors.LogNorm(vmin=mincnt),)
    axs[2, 2].set_xlabel("X [cm]", fontsize=fontsize)
    axs[2, 2].set_ylabel("Y [cm]", fontsize=fontsize)
    # Set equal aspect ratio
    axs[2, 2].set_aspect('equal', adjustable='box')
    # Display the colorbar
    cb = plt.colorbar(axs[2, 2].collections[0], ax=axs[2, 2], orientation="vertical", pad=0.01, aspect=40, shrink=0.85, fraction=0.25, label="Frequency", extend="max", extendfrac=0.1, extendrect=True, location="right",)
    cb.ax.xaxis.set_label_position("top")
    axs[2, 2].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)

    # Set the x and y axes limits to -6 to 6
    axs[2, 2].set_xlim(-6, 6)
    axs[2, 2].set_ylim(-6, 6)

    # Plot a circle with radius 4 and 0.9375 * 4
    radius1 = 4
    radius2 = 0.9375 * radius1

    circle1 = axs[2, 2].add_patch(plt.Circle((0, 0), radius1, color="red", fill=False, linewidth=linewidth))
    circle2 = axs[2, 2].add_patch(plt.Circle((0, 0), radius2, color="blue", fill=False, linewidth=linewidth))

    angle_1 = np.pi / 2.7
    angle_2 = np.pi / 1.3
    # Annotate the twwo circles
    axs[2, 2].annotate("Detector Size", xy=(radius1 * np.cos(angle_1), radius1 * np.sin(angle_1)), xytext=((radius1 - 2.2) * np.cos(angle_1), (radius1 + 1.55) * np.sin(angle_1)), arrowprops=dict(arrowstyle="->", color="r", linewidth=linewidth), color="red", fontsize=0.9 * fontsize,)
    axs[2, 2].annotate("Effective Area", xy=(radius2 * np.cos(angle_2), radius2 * np.sin(angle_2)), xytext=((radius2 + 4.2) * np.cos(angle_2), (radius2 + 4.5) * np.sin(angle_2)), arrowprops=dict(arrowstyle="->", color="b", linewidth=linewidth), color="blue", fontsize=0.9 * fontsize, ha="left", va="center",)


    # Get the 10, 50 and 90 percentile values of the data (Channel 1, Channel 2, Channel 3, Channel
    # 4, Pulse Height)
    percentile_values = df_sci[["Channel1", "Channel2", "Channel3", "Channel4", "PulseHeight"]].quantile([0.1, 0.5, 0.9])

    # Get the averagee number of events per second

    total__number_of_events = df_sci.shape[0]
    total_observation_time = (df_sci.index[-1] - df_sci.index[0]).total_seconds()
    average_number_of_events_per_second = total__number_of_events / total_observation_time
    # Add the text to the plot
    axs[2, 1].text(
        0.5,
        0.85,
        f"Observation Length: {total_observation_time:.2f} seconds \n Total Number of Events: {total__number_of_events}\n Average Number of Events: {average_number_of_events_per_second:.2f} Hz",
        horizontalalignment="center",
        verticalalignment="top",
        transform=axs[2, 1].transAxes,
        color="white",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.5),
    )
    # On the plot 2, 1 display the 10, 50 and 90 percentile values of the data with the mean value of
    # the data in the middle and the 10th and 90th percentile values as the subscript and superscript
    # of the mean value respectively
    x_0 = 0.04
    y_0 = 0.45
    axs[2, 1].text(
        x_0,
        y_0,
        f"$\mu_{{10}}^{{90}}={percentile_values['Channel1'][0.5]:.2f}_{{{percentile_values['Channel1'][0.1]:.2f}}}^{{{percentile_values['Channel1'][0.9]:.2f}}}$",
        horizontalalignment="left",
        verticalalignment="top",
        transform=axs[2, 1].transAxes,
        color="#42f5bc",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.0),
    )
    axs[2, 1].text(
        x_0,
        y_0 - 0.2,
        f"$\mu_{{10}}^{{90}}={percentile_values['Channel2'][0.5]:.2f}_{{{percentile_values['Channel2'][0.1]:.2f}}}^{{{percentile_values['Channel2'][0.9]:.2f}}}$",
        horizontalalignment="left",
        verticalalignment="top",
        transform=axs[2, 1].transAxes,
        color="#42cef5",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.0),
    )
    axs[2, 1].text(
        x_0 + 0.96,
        y_0,
        f"$\mu_{{10}}^{{90}}={percentile_values['Channel3'][0.5]:.2f}_{{{percentile_values['Channel3'][0.1]:.2f}}}^{{{percentile_values['Channel3'][0.9]:.2f}}}$",
        horizontalalignment="right",
        verticalalignment="top",
        transform=axs[2, 1].transAxes,
        color="#f542ef",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.0),
    )
    axs[2, 1].text(
        x_0 + 0.96,
        y_0 - 0.2,
        f"$V4_{{10}}^{{90}}={percentile_values['Channel4'][0.5]:.2f}_{{{percentile_values['Channel4'][0.1]:.2f}}}^{{{percentile_values['Channel4'][0.9]:.2f}}}$",
        horizontalalignment="right",
        verticalalignment="top",
        transform=axs[2, 1].transAxes,
        color="#f5a742",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.0),
    )
    axs[2, 1].text(
        0.5,
        y_0 - 0.4,
        f"$\mu_{{10}}^{{90}}={percentile_values['PulseHeight'][0.5]:.2f}_{{{percentile_values['PulseHeight'][0.1]:.2f}}}^{{{percentile_values['PulseHeight'][0.9]:.2f}}}$",
        horizontalalignment="center",
        verticalalignment="top",
        transform=axs[2, 1].transAxes,
        color="white",
        fontsize=label_factor * fontsize,
        bbox=dict(facecolor="black", alpha=0.0),
    )

    # Turn off the axis for the last plot
    axs[2, 1].axis("off")
    # Save the figure as png file to the path
    default_folder = "../lxi_science_data/"
    Path(default_folder).mkdir(parents=True, exist_ok=True)
    # Expand the path to full path
    default_folder = Path(default_folder).expanduser()

    # In the start and end time, replace the : with _ to avoid confusion with the file name
    start_time = start_time.replace(":", "_")
    end_time = end_time.replace(":", "_")
    # Replace space with _
    start_time = start_time.replace(" ", "_")
    end_time = end_time.replace(" ", "_")
    fig_name = f"detailed_lxi_science_{start_time}_{end_time}.png"

    fig.savefig(default_folder / fig_name, dpi=300, bbox_inches="tight", pad_inches=0.1)

    print(f"Figure saved as {default_folder / fig_name}")


    long_time_series_plot()

    print("Long term time series plot saved.")

    return None


def check_folder_structure():
    # Start from the current directory and go up to 3 levels
    current_path = Path.cwd()

    for i in range(4):
        # Get the current directory by moving up 'i' levels
        check_path = current_path.parents[i] if i < len(current_path.parents) else current_path

        # Define the target folder structure
        target_folder = check_path / 'data' / 'from_LEXI' / 'L1a' / 'hk'

        if target_folder.is_dir():
            print(f"Found folder structure at: {target_folder}")
            return target_folder

    print("Folder structure not found.")
    # Cd into the target folder

    return target_folder


def read_and_plot_all_files():

    parent_folder = check_folder_structure()
    print(f"Reading files from: {parent_folder}")

    file_name_format = "payload_lexi_*_*_hk_output_L1a.csv"
    csv_files = glob.glob(
        str(parent_folder / "**" / file_name_format), recursive=True
    )
    print(f"Found {len(csv_files)} CSV files in the orbit folder.")
    # Remove files that has "_hk_hk_" in the name
    exclude_pattern = re.compile(r"_hk_hk_")
    csv_files = [file for file in csv_files if not exclude_pattern.search(file)]
    # Sort the files by name
    csv_files.sort()
    print(f"Found {len(csv_files)} CSV files in the orbit folder after excluding some files.")
    df_list = []
    if not csv_files:
        print("No CSV files found in the orbit folder.")
        return pd.DataFrame()
    for i, file in enumerate(csv_files):
        # print(f"Reading file {i + 1} of {len(csv_files)}: {file}")
        df = pd.read_csv(file)
        # Ignore first 30 rows
        df = df.iloc[30:]
        df_list.append(df)

    df_all = pd.concat(df_list)
    df_all["Date"] = pd.to_datetime(df_all["Date"])
    df_all.set_index("Date", inplace=True)
    # Sort the data by date
    df_all.sort_index(inplace=True)
    return df_all


def long_time_series_plot():
    df_all = read_and_plot_all_files()

    # Extract the time portion from the index
    df_all["Time"] = df_all.index.time

    # Convert the time to seconds from midnight for aggregation
    df_all["seconds"] = df_all["Time"].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)

    # Group by the date part (just the date)
    daily_grouped = df_all.groupby(df_all.index.date)["seconds"]

    # Calculate the min, max and median seconds for each day
    time_stats_seconds = daily_grouped.agg(["min", "max", "median"])

    # Convert the results back to datetime.time
    time_stats_seconds["min"] = pd.to_datetime(
        time_stats_seconds["min"], unit="s"
    ).dt.time
    time_stats_seconds["max"] = pd.to_datetime(
        time_stats_seconds["max"], unit="s"
    ).dt.time
    time_stats_seconds["median"] = pd.to_datetime(
        time_stats_seconds["median"], unit="s"
    ).dt.time

    # Add the date part to the median time (combine date and median time)
    time_stats_seconds["median_with_date"] = time_stats_seconds.index.to_series().apply(
        lambda x: pd.to_datetime(str(x) + " " + str(time_stats_seconds["median"][x]))
    )

    numeric_df = df_all.select_dtypes(include=['number'])
    # For each day, calculate the median, 10th percentile, and 90th percentile for each key
    daily_median = numeric_df.groupby(df_all.index.date).quantile(0.5)
    daily_10p = numeric_df.groupby(df_all.index.date).quantile(0.1)
    daily_90p = numeric_df.groupby(df_all.index.date).quantile(0.9)

    default_key_list = [
        "HVsupplyTemp",
        "LEXIbaseTemp",
        "PinPullerTemp",
        "+3.3V_Imon",
        "+5.2V_Imon",
        "+10V_Imon",
        "+28V_Imon",
        "AnodeVoltMon",
        "DeltaEvntCount",
    ]

    # Make a dictionary of all the plot options and their units
    unit_dict = {
        "HK_id": "#",
        "PinPullerTemp": "(C)",
        "OpticsTemp": "(C)",
        "LEXIbaseTemp": "(C)",
        "HVsupplyTemp": "(C)",
        "+5.2V_Imon": "(mA)",
        "+10V_Imon": "(mA*)",
        "+3.3V_Imon": "(mA)",
        "AnodeVoltMon": "(V*)",
        "+28V_Imon": "(mA)",
        "ADC_Ground": "(V)",
        "Cmd_count": "#",
        "Pinpuller_Armed": "",
        "HVmcpAuto": "",
        "HVmcpMan": "",
        "DeltaEvntCount": "#",
        "DeltaDroppedCount": "#",
        "DeltaLostevntCount": "#",
    }
    nominal_values_dict_hv_on = {
        "PinPullerTemp": "-10 to 50",
        "OpticsTemp": "-10 to 50",
        "LEXIbaseTemp": "-10 to 50",
        "HVsupplyTemp": "-10 to 50",
        "+5.2V_Imon": "$68 \pm 0.5$",
        "+10V_Imon": "$2.5 \pm 0.4$",
        "+3.3V_Imon": "$42.5 \pm 0.5$",
        "AnodeVoltMon": "$3.4 \pm 0.6$",
        "+28V_Imon": "$57.6 \pm 2.2$",
        "DeltaDroppedCount": 0,
        "DeltaLostevntCount": 0,
    }
    nominal_values_dict_hv_off = {
        "PinPullerTemp": "-10 to 50",
        "OpticsTemp": "-10 to 50",
        "LEXIbaseTemp": "-10 to 50",
        "HVsupplyTemp": "-10 to 50",
        "+5.2V_Imon": "$61.5 \pm 0.5$",
        "+10V_Imon": "$0.15 \pm 0.0$",
        "+3.3V_Imon": "$47.7 \pm 0.1$",
        "AnodeVoltMon": "$0.0044 \pm 0.0$",
        "+28V_Imon": "$44.1 \pm 0.4$",
        "DeltaDroppedCount": 0,
        "DeltaLostevntCount": 0,
    }

    start_time = df_all.index[0]
    end_time = df_all.index[-1]

    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # In global_variables, if hv_status is not defined, set it to False
    if "hv_status" not in global_variables.__dict__:
        global_variables.hv_status = False

    fontsize = 10

    # Set the font size for the plots
    font = {"family": "serif", "weight": "normal", "size": fontsize}
    plt.rc("font", **font)
    # Use dark background
    plt.style.use("dark_background")

    # Create a figure with 3 by 3 subplots
    fig, axs = plt.subplots(3, 3, figsize=(15, 6), sharex=True)
    fig.subplots_adjust(hspace=0.15, wspace=0.35, top=0.92)

    fig.suptitle(f"Long Term Housekeeping Data from {start_time} to {end_time}", fontsize=1.2 * fontsize,)

    color_list = ["red", "red", "red", "green", "green", "green", "green", "green", "white"]
    # Plot the data
    for i, key in enumerate(default_key_list):
        # Get rid of NaN values
        df_all = df_all.dropna(subset=[key])

        row = i // 3
        col = i % 3

        axs[row, col].plot(df_all.index, df_all[key], ".", label=key, color=color_list[i], markersize=1, alpha=0.05,)
        # axs[row, col].scatter(
        #     df_all.index,
        #     df_all[key],
        #     c=df_all.index,
        #     cmap='inferno',
        #     label=key,
        #     s=1,
        #     alpha=0.7
        # )
        axs[row, col].set_ylabel(f"{unit_dict[key]}")

        # Write the name of the key in the bottom right corner of the plot
        axs[row, col].text(
            0.98,
            0.05,
            key,
            horizontalalignment="right",
            verticalalignment="bottom",
            transform=axs[row, col].transAxes,
            color="white",
            fontsize=0.75 * fontsize,
            bbox=dict(facecolor="black", alpha=0.5),
        )

        # Add a grid to the plot for better readability, separate the major and minor ticks
        axs[row, col].grid(which="major", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)
        axs[row, col].grid(which="minor", axis="both", color="c", linestyle="--", linewidth=0.2, alpha=0.5)

        try:
            if global_variables.hv_status:
                axs[row, col].text(
                    0.02,
                    0.95,
                    f"Nom Val: {nominal_values_dict_hv_on[key]}",
                    horizontalalignment="left",
                    verticalalignment="top",
                    transform=axs[row, col].transAxes,
                    color="white",
                    fontsize=0.75 * fontsize,
                    bbox=dict(facecolor="black", alpha=0.5),
                )
            elif global_variables.hv_status is False:
                axs[row, col].text(
                    0.02,
                    0.95,
                    f"Nom Val: {nominal_values_dict_hv_off[key]}",
                    horizontalalignment="left",
                    verticalalignment="top",
                    transform=axs[row, col].transAxes,
                    color="white",
                    fontsize=0.75 * fontsize,
                    bbox=dict(facecolor="black", alpha=0.5),
                )
        except Exception:
            pass

        # Put the tickmarks inside the plot
        axs[row, col].tick_params(axis="both", direction="in", length=8)
        # Put the tickmarks inside the plot for minor ticks
        axs[row, col].tick_params(axis="both", which="minor", direction="in", length=5)
        # Set the xlabel only if it is the last row
        if row == 2:
            # Format the x-axis to show the time
            axs[row, col].xaxis.set_major_locator(mdates.HourLocator(interval=24))

            # Set a 5-minute interval for minor tick marks
            axs[row, col].xaxis.set_minor_locator(mdates.HourLocator(interval=6))

            # Format the x-axis to display labels only for major tick marks
            # axs[row, col].xaxis.set_major_formatter(mdates.DateFormatter("%M/%D %H:%M"))
            # Ensure that the x-axis is readable
            plt.setp(axs[row, col].xaxis.get_majorticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            axs[row, col].set_xlabel("Time [UTC]", fontsize=fontsize)

        #  Plot the daily stats, with median in red diamond and 10th-90th percentile as error bars in
        #  cyan color. Also add text beside the error bar to show the 10th and 90th percentile values
        axs[row, col].errorbar(
            time_stats_seconds["median_with_date"],
            daily_median[key],
            yerr=[daily_median[key] - daily_10p[key], daily_90p[key] - daily_median[key]],
            fmt="d",
            color="white",
            ecolor="magenta",
            label="10th-90th Percentile",
            markersize=2,
        )

        # Add text annotations for 90th and 10th percentiles
        for i, x in enumerate(time_stats_seconds["median_with_date"]):
            y = daily_median[key][i]
            y_10p = daily_10p[key][i]
            y_90p = daily_90p[key][i]

            # Add text annotation for 10th percentile at the bottom of the error bar
            axs[row, col].text(
                x, y_10p, f"{y_10p:.2f}", ha='left', va='bottom', color="c", fontsize=0.6 * fontsize, rotation=90
            )

            # Add text annotation for 90th percentile at the top of the error bar
            axs[row, col].text(
                x, y_90p, f"{y_90p:.2f}", ha='right', va='top', color="c", fontsize=0.6 * fontsize, rotation=90
            )

    # Add HV status in the top right corner of the 0, 2 subplot
    axs[0, 2].text(
        0.97,
        1.05,
        "HV ON" if global_variables.hv_status else "HV OFF",
        transform=axs[0, 2].transAxes,
        horizontalalignment="right",
        verticalalignment="bottom",
        color="red" if global_variables.hv_status else "green",
        fontsize=fontsize,
        bbox=dict(facecolor="black", alpha=0.5),
    )

    default_folder = "../lxi_housekeeping_data/long_term_trends/"
    Path(default_folder).mkdir(parents=True, exist_ok=True)
    # Expand the path to full path
    default_folder = Path(default_folder).expanduser()
    if global_variables.hv_status:
        # In the start and end time, replace the : with _ to avoid confusion with the file name
        start_time = start_time.replace(":", "_")
        end_time = end_time.replace(":", "_")
        # Replace space with _
        start_time = start_time.replace(" ", "_")
        end_time = end_time.replace(" ", "_")
        fig_name = f"lxi_housekeeping_data_{start_time}_{end_time}_hv_status_ON.png"
    else:
        # In the start and end time, replace the : with _ to avoid confusion with the file name
        start_time = start_time.replace(":", "_")
        end_time = end_time.replace(":", "_")
        # Replace space with _
        start_time = start_time.replace(" ", "_")
        end_time = end_time.replace(" ", "_")
        fig_name = f"lxi_housekeeping_data_{start_time}_{end_time}_hv_status_OFF.png"

    fig.savefig(default_folder / fig_name, dpi=300, bbox_inches="tight", pad_inches=0.1)
    # Close the figure
    # plt.close(fig)
    print(f"Figure saved as {default_folder / fig_name}")

    return daily_median, daily_10p, daily_90p


# if __name__ == "__main__":
#     save_figures()
#     save_figures()
