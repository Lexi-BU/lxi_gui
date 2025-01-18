import matplotlib.pyplot as plt
import numpy as np
import global_variables
import matplotlib.dates as mdates
from pathlib import Path


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

    return None
