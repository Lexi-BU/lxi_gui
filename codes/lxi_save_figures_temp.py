import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import global_variables
import matplotlib.dates as mdates
from pathlib import Path
import pandas as pd
from matplotlib.ticker import FormatStrFormatter, MaxNLocator
from functools import reduce


def save_figures(df=None, start_time=None, end_time=None, df_sci=None, start_voltage=None, end_voltage=None):

    # Get the Sliced Housekeeping Data from the global variable
    # df = global_variables.all_file_details["df_slice_hk"]

    # Filter the data to get the data between the start and end time
    df = df.loc[start_time:end_time]
    # Print the maximum and minimum value of index of the data
    # print(f"Minimum time: {df.index.min()}")
    # print(f"Maximum time: {df.index.max()}")
    # Get the Sliced Science Data from the global variable
    # df_sci = global_variables.all_file_details["df_all_sci"]

    # Filter the data to get the data between the start and end time
    df_sci = df_sci.loc[start_time:end_time]
    # return df
    start_time = df_sci.index[0]
    end_time = df_sci.index[-1]

    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # In global_variables, if hv_status is not defined, set it to False
    if "hv_status" not in global_variables.__dict__:
        global_variables.hv_status = True
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
        "HV_value",
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
        "HV_value": "(V)",
        "+28V_Imon": "(mA)",
        "ADC_Ground": "(V)",
        "Cmd_count": "#",
        "Pinpuller_Armed": "",
        "HVmcpAuto": "",
        "HVmcpMan": "",
        "DeltaEvntCount": "#",
        "DeltaDroppedCount": "#",
        "DeltaLostEvntCount": "#",
    }
    nominal_values_dict_hv_on = {
        "PinPullerTemp": "-10 to 50",
        "OpticsTemp": "-10 to 50",
        "LEXIbaseTemp": "-10 to 50",
        "HVsupplyTemp": "-10 to 50",
        "+5.2V_Imon": "$68 \pm 0.5$",
        "+10V_Imon": "$2.5 \pm 0.4$",
        "+3.3V_Imon": "$42.5 \pm 0.5$",
        # "HV_value": "$3.4 \pm 0.6$",
        "+28V_Imon": "$57.6 \pm 2.2$",
        "DeltaDroppedCount": 0,
        "DeltaLostEvntCount": 0,
    }
    nominal_values_dict_hv_off = {
        "PinPullerTemp": "-10 to 50",
        "OpticsTemp": "-10 to 50",
        "LEXIbaseTemp": "-10 to 50",
        "HVsupplyTemp": "-10 to 50",
        "+5.2V_Imon": "$61.5 \pm 0.5$",
        "+10V_Imon": "$0.15 \pm 0.0$",
        "+3.3V_Imon": "$42.5 \pm 0.5$",
        # "HV_value": "$0.0044 \pm 0.0$",
        "+28V_Imon": "$44.1 \pm 0.4$",
        "DeltaDroppedCount": 0,
        "DeltaLostEvntCount": 0,
    }

    fontsize = 10

    # Set the font size for the plots
    font = {"family": "serif", "weight": "normal", "size": fontsize}
    plt.rc("font", **font)
    # Use dark background
    plt.style.use("dark_background")

    # Create a figure with 3 by 3 subplots
    fig, axs = plt.subplots(3, 3, figsize=(15, 6), sharex=True)
    fig.subplots_adjust(hspace=0.165, wspace=0.25, top=0.92)

    fig.suptitle(f"Housekeeping Data from {start_time} to {end_time} for {start_voltage}-{end_voltage} V", fontsize=1.2 * fontsize, x=0.5, y=1.005)

    # Plot the data
    for i, key in enumerate(default_key_list):
        # Get rid of NaN values
        df = df.dropna(subset=[key])
        # Get the 10th, 50th and 90th percentile values of the data
        key_10p_val = np.percentile(df[key], 10)
        key_50p_val = np.percentile(df[key], 50)
        key_90p_val = np.percentile(df[key], 90)
        key_std = np.nanstd(df[key])

        # Set the x and y limits
        key_x_lim = [df.index[0], df.index[-1]]
        key_y_lim = [0.9 * key_10p_val, 1.05 * key_90p_val]
        # key_y_lim = [key_50p_val - 3 * key_std, key_50p_val + 3 * key_std]

        # For any data that is more than 5 standard deviations away from the median, modify it
        outliers = df[np.abs(df[key] - key_50p_val) > 4 * key_std]
        df_outliers_replaced = df.copy()
        df_outliers_replaced.loc[outliers.index, key] = key_y_lim[0]

        # If the key is "DeltaEvntCount", then ignore the outliers
        if key == "DeltaEvntCount":
            pass
        else:
            # Set the values at the outliers to NaN in the original dataframe
            df.loc[outliers.index, key] = np.nan

        row = i // 3
        col = i % 3

        axs[row, col].plot(df.index, df[key], ".", label=key, color="green", markersize=5, alpha=0.5,)
        if key != "DeltaEvntCount":
            axs[row, col].plot(outliers.index, df_outliers_replaced.loc[outliers.index, key], marker="d", color="red", ls=None, lw=0, ms=5, zorder=10)
        axs[row, col].set_ylabel(f"{unit_dict[key]}")

        # Write the name of the key in the bottom right corner of the plot
        axs[row, col].text(
            1.035,
            0.5,
            key,
            horizontalalignment="center",
            verticalalignment="center",
            rotation=270,
            transform=axs[row, col].transAxes,
            color="white",
            fontsize=0.75 * fontsize,
            bbox=dict(facecolor="black", alpha=0.5),
        )

        if key == "DeltaEvntCount":
            axs[row, col].set_ylim(0, 1.05 * df[key].max())
        else:
            axs[row, col].set_ylim(key_y_lim[0], key_y_lim[-1])

        # Set the x and y limits
        axs[row, col].set_xlim(key_x_lim[0], key_x_lim[-1])
        # On the plot, display the 10, 50 and 90 percentile values of the data where mu is the mean
        # and the subscript is the 10th percentile value and the superscript is the 90th percentile
        # value
        axs[row, col].text(
            0.982,
            1.035,
            f"$\mu_{{{10}}}^{{{90}}}={key_50p_val:.2f}_{{{key_10p_val:.2f}}}^{{{key_90p_val:.2f}}}$",
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
                    0.018,
                    1.035,
                    f"Nominal Value: {nominal_values_dict_hv_on[key]}",
                    horizontalalignment="left",
                    verticalalignment="bottom",
                    transform=axs[row, col].transAxes,
                    color="white",
                    fontsize=0.75 * fontsize,
                    bbox=dict(facecolor="black", alpha=0.5),
                )
            elif global_variables.hv_status is False:
                axs[row, col].text(
                    0.018,
                    1.035,
                    f"Nominal Value: {nominal_values_dict_hv_off[key]}",
                    horizontalalignment="left",
                    verticalalignment="bottom",
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

        # For each y-tick, set the number of significant figures to 2, and remove the leading zeros
        y_ticks = axs[row, col].get_yticks()
        y_ticks_new = []
        for y_tick in y_ticks:
            if y_tick == 0:
                y_ticks_new.append(0)
            else:
                y_ticks_new.append(round(y_tick, 2))
        axs[row, col].set_yticks(y_ticks_new)
        axs[row, col].set_yticklabels(y_ticks_new)

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
        0.982,
        1.202,
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
    default_folder = "."
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
        fig_name = f"lxi_housekeeping_data_{start_time}_{end_time}_hv_value_{start_voltage}_{end_voltage}.png"
    else:
        # In the start and end time, replace the : with _ to avoid confusion with the file name
        start_time = start_time.replace(":", "_")
        end_time = end_time.replace(":", "_")
        # Replace space with _
        start_time = start_time.replace(" ", "_")
        end_time = end_time.replace(" ", "_")
        fig_name = f"lxi_housekeeping_data_{start_time}_{end_time}_hv_value_{start_voltage}_{end_voltage}.png"

    fig.savefig(default_folder / fig_name, dpi=300, bbox_inches="tight", pad_inches=0.1)
    # Close the figure
    plt.close(fig)
    print(f"Figure saved as \033[1;31m {default_folder / fig_name} \033[0m\n")

    # Science Figure

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
    fig.subplots_adjust(hspace=0.15, wspace=0.40, top=0.95)

    fig.suptitle(f"Science Data from {start_time} to {end_time} for {start_voltage}-{end_voltage} V", fontsize=1.2 * fontsize,)
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
    # Change the color of x-axis and ticks and its labels to #42f5bc
    axs[0, 2].tick_params(axis="x", colors="#42f5bc")
    axs[0, 2].xaxis.label.set_color("#42f5bc")
    axs[0, 2].spines["bottom"].set_color("#42f5bc")

    # Change the color of y-axis and ticks and its labels to #f542ef
    axs[0, 2].tick_params(axis="y", colors="#f542ef")
    axs[0, 2].yaxis.label.set_color("#f542ef")
    axs[0, 2].spines["left"].set_color("#f542ef")

    # Display the colorbar
    cb = plt.colorbar(axs[0, 2].collections[0], ax=axs[0, 2], orientation="vertical", pad=0.01, aspect=40, shrink=0.85, fraction=0.25, label="Frequency", extend="max", extendfrac=0.1, extendrect=True, location="right")
    cb.ax.xaxis.set_label_position("top")
    axs[0, 2].grid(True, which="both", axis="both", color="white", linestyle="--", linewidth=0.2, alpha=0.75)

    # Plot the hexbin plot of Channel 2 and Channel 4
    axs[1, 2].hexbin(df_sci["Channel2"], df_sci["Channel4"], gridsize=50, cmap="inferno", alpha=1, norm=mpl.colors.LogNorm(vmin=mincnt),)
    axs[1, 2].set_xlabel("Channel 2 [V]", fontsize=fontsize)
    axs[1, 2].set_ylabel("Channel 4 [V]", fontsize=fontsize)

    # Change the color of x-axis and ticks and its labels to #42cef5
    axs[1, 2].tick_params(axis="x", colors="#42cef5")
    axs[1, 2].xaxis.label.set_color("#42cef5")
    axs[1, 2].spines["bottom"].set_color("#42cef5")

    # Change the color of y-axis and ticks and its labels to #f5a742
    axs[1, 2].tick_params(axis="y", colors="#f5a742")
    axs[1, 2].yaxis.label.set_color("#f5a742")
    axs[1, 2].spines["left"].set_color("#f5a742")

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
    # Only select the data where IsCommanded is False
    # df_sci_cmd_false = df_sci[df_sci["IsCommanded"] == False]
    df_sci_cmd_false = df_sci.copy()
    # Plot the hexbin historagram of between "x_mcp_lin" and "y_mcp_lin". Ignore any bins where the
    # number of points is less than 10
    axs[2, 2].hexbin(df_sci_cmd_false["x_mcp_lin"], df_sci_cmd_false["y_mcp_lin"], gridsize=50, cmap="plasma", alpha=1, mincnt=mincnt, norm=mpl.colors.LogNorm(vmin=mincnt),)
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
    axs[2, 2].annotate("Detector Size", xy=(radius1 * np.cos(angle_1), radius1 * np.sin(angle_1)), xytext=((radius1 - 2.2) * np.cos(angle_1), (radius1 + 1.55) * np.sin(angle_1)), arrowprops=dict(arrowstyle="->", color="w", linewidth=linewidth), color="w", fontsize=0.9 * fontsize,)
    axs[2, 2].annotate("Effective Area", xy=(radius2 * np.cos(angle_2), radius2 * np.sin(angle_2)), xytext=((radius2 + 4.2) * np.cos(angle_2), (radius2 + 4.5) * np.sin(angle_2)), arrowprops=dict(arrowstyle="->", color="w", linewidth=linewidth), color="w", fontsize=0.9 * fontsize, ha="left", va="center",)

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
    default_folder = "."
    Path(default_folder).mkdir(parents=True, exist_ok=True)
    # Expand the path to full path
    default_folder = Path(default_folder).expanduser()

    # In the start and end time, replace the : with _ to avoid confusion with the file name
    start_time = start_time.replace(":", "_")
    end_time = end_time.replace(":", "_")
    # Replace space with _
    start_time = start_time.replace(" ", "_")
    end_time = end_time.replace(" ", "_")
    fig_name = f"detailed_lxi_science_{start_time}_{end_time}_{start_voltage}_{end_voltage}.png"

    fig.savefig(default_folder / fig_name, dpi=300, bbox_inches="tight", pad_inches=0.1)

    print(f"Figure saved as \033[1;32m{default_folder / fig_name}\033[0m\n")
    # Close the figure
    plt.close(fig)
    return None


if __name__ == "__main__":

    # Pre reset files
    # hk_file_name =
    # "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/from_LEXI/L1a/hk/20250131/payload_lexi_1738335417_2491_1738344195_18776_hk_output_L1a.csv"
    # sci_file_name = "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/from_LEXI/L1b/sci/20250131/lexi_payload_1738335417_2491_1738344195_18776_sci_output_L1b.csv"

    # Post reset files
    hk_file_name = "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/from_LEXI/L1a/hk/20250131/payload_lexi_1738343895_10505_1738347224_32823_hk_output_L1a.csv"
    sci_file_name = "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/from_LEXI/L1b/sci/20250131/lexi_payload_1738343895_10505_1738347224_32823_sci_output_L1b.csv"
    df_hk = pd.read_csv(hk_file_name, index_col="Date", parse_dates=True)
    df_sci = pd.read_csv(sci_file_name, index_col="Date", parse_dates=True)

    # Add "HV_value" column to df_hk
    df_hk["HV_value"] = df_hk["AnodeVoltMon"] * 601.0

    # start_voltage_list = [0, 600, 1200, 1400, 1600, 1700, 1800, 1900, 2000, 2100]
    # end_voltage_list = [600, 1200, 1400, 1600, 1700, 1800, 1900, 2000, 2100, 2200]
    start_voltage_list = [0, 450, 550, 750, 950, 1150, 1325, 1375, 1425, 1475, 1525, 1550, 1575, 1590, 1625, 1675, 1725, 1775, 1825, 1875, 1925, 1975, 2025, 2075, 2125, 2175]
    end_voltage_list = [450, 550, 750, 950, 1150, 1325, 1375, 1425, 1475, 1525, 1550, 1575, 1590, 1625, 1675, 1725, 1775, 1825, 1875, 1925, 1975, 2025, 2075, 2125, 2175, 2225]
    start_voltage_list = [1570]
    end_voltage_list = [1590]
    for start_voltage, end_voltage in zip(start_voltage_list[0:], end_voltage_list[0:]):
        try:
            # Find all the times where the the HV_value was between start_voltage and end_voltage
            df_hv = df_hk[(df_hk["HV_value"] > start_voltage) & (df_hk["HV_value"] < end_voltage)]
            start_time_list = df_hv.index[:-1]
            end_time_list = df_hv.index[1:]
            start_time = df_hv.index[0]
            end_time = df_hv.index[-1]

            # Assign timezone to UTC to start_time and end_time
            start_time = start_time.tz_localize("UTC")
            end_time = end_time.tz_localize("UTC")
            start_time_list = start_time_list.tz_localize("UTC")
            end_time_list = end_time_list.tz_localize("UTC")

            diff_time = end_time_list - start_time_list
            # Find all the times where the difference between the start_time and end_time is greater
            # than 10 seconds
            mask = diff_time < pd.Timedelta("10 seconds")
            start_time_list = start_time_list[mask]
            end_time_list = end_time_list[mask]
            # Select only the data from df_sci that is between start_time_list and end_time_list
            # Generate boolean masks as a list of Pandas Series
            masks = [(df_sci.index >= start) & (df_sci.index <= end) for start, end in zip(start_time_list, end_time_list)]

            # Combine all masks using logical OR (`|`) with reduce
            if masks:
                combined_mask = reduce(np.logical_or, masks)
                df_sci_selected = df_sci[combined_mask]
            else:
                df_sci_selected = df_sci.iloc[:0]

            # print(f"Start Time: {start_time}\nEnd Time: {end_time}")
            # Add 10 seconds to start_time and subtract 10 seconds from end_time
            start_time = start_time + pd.Timedelta("15 seconds")
            end_time = end_time - pd.Timedelta("20 seconds")
            # print(f"Start Time: {start_time}\nEnd Time: {end_time}")
            # Select only the data from df_sci that is between start_time and end_time
            # df_sci_selected = df_sci[(df_sci.index > start_time) & (df_sci.index < end_time)]
            save_figures(df=df_hv, start_time=start_time, end_time=end_time, df_sci=df_sci_selected, start_voltage=start_voltage, end_voltage=end_voltage)
        except Exception as e:
            print(f"Error: {e} for {start_voltage}-{end_voltage} V")
            continue
