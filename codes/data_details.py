import os
import pandas as pd
import csv
from pathlib import Path
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np


def list_folders_in_directory(directory_path):
    # Create a list to store folder paths
    folder_list = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory_path):
        for dir_name in dirs:
            # Create the full folder path
            folder_path = os.path.join(root, dir_name)
            folder_list.append(folder_path)

    return folder_list


def read_data_from_folder(folder_path="", save_file_name=""):
    data_folder = folder_path + "processed_data/hk/"
    # key_list = ["HK_id", "PinPullerTemp", "OpticsTemp", "LEXIbaseTemp",
    #             "HVsupplyTemp", "+5.2V_Imon", "+10V_Imon", "+3.3V_Imon",
    #             "AnodeVoltMon", "+28V_Imon", "ADC_Ground", "Cmd_count",
    #             "Pinpuller_Armed", "HVmcpAuto", "HVmcpMan", "DeltaEvntCount",
    #             "DeltaDroppedCount", "DeltaLostEvntCount"]

    key_list = ["+5.2V_Imon", "+10V_Imon", "+3.3V_Imon",
                "AnodeVoltMon", "+28V_Imon", "HVmcpMan", "DeltaEvntCount"]
    # Check if the data folder exists
    if not os.path.exists(data_folder):
        print(f"Data folder does not exist for {folder_path}.\n")
        return
    else:
        # print(f"Data folder exists for {folder_path}.\n")
        # Get the list of files in the data folder
        file_list_all = os.listdir(data_folder)
        print(len(file_list_all))
        print(f"Reading data from {data_folder}.\n")
        for file_list in file_list_all:
            # Read the data from the file
            data = pd.read_csv(data_folder + file_list)
            # For each key in the key list, find the 50th percentile, rounded to 3 decimal places
            data_dict = {}
            for key in key_list:
                data_dict[key] = round(data[key].quantile(0.5), 3)

            folder_name = folder_path.split("/")[7:]
            # Join the folder name to get the full folder name
            folder_name = "_".join(folder_name)
            if folder_name == "recovery_files":
                folder_name = folder_path.split("/")[-3]

            # If the save file doesn't exist, create it and add the folder_name and the key list as the
            # header
            if not os.path.exists(save_file_name):
                with open(save_file_name, "w") as file:
                    writer = csv.writer(file)
                    writer.writerow(["folder_name", "file_name"] + key_list)
            # Append the data to the save file
            print(f"Writing data for {folder_name} to {save_file_name}.")
            with open(save_file_name, "a") as file:
                writer = csv.writer(file)
                writer.writerow([folder_name] + [file_list] + [data_dict[key] for key in key_list])
        # return data_dict


"""
if __name__ == "__main__":
    directory_path = "~/Desktop/git/Lexi-BU/lxi_gui/data/hk_testings/"
    directory_path = os.path.expanduser(directory_path)
    folder_list = list_folders_in_directory(directory_path)

    count = 0
    for folder_path in folder_list[:]:
        count += 1
        data = read_data_from_folder(folder_path=folder_path + "/", save_file_name="../data/hk_testings/median_data.csv")
        print(f"Processed {count} folders out of {len(folder_list)}.")
        continue
"""

# Read the data from the median_data.csv file
df = pd.read_csv("../data/hk_testings/median_data.csv")

key_list = ["+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon", "HVmcpMan",
            "DeltaEvntCount"]
# If the value of all the keys in the key_list is nan, then remove the row
df = df.dropna(subset=key_list, how="all")

# Get a list of the unique folder names
folder_names = df["folder_name"].unique()

# For each folder name, select a random row corresponding to the folder name and add it to a new
# dataframe
df_filtered = pd.DataFrame()
random_seed = 11
for folder_name in folder_names:
    df_temp = df[df["folder_name"] == folder_name]
    try:
        df_temp = df_temp.sample(n=5, random_state=random_seed)
    except Exception:
        df_temp = df_temp.sample(n=1, random_state=random_seed)
    df_filtered = pd.concat([df_filtered, df_temp])

# Save the filtered data to a new csv file
df_filtered.to_csv(f"../data/hk_testings/filtered_data_{random_seed}_random_seed.csv", index=False)


"""
def make_plots(df, plot_key_list, save_file_name, format="pdf", x_limit=None, random_seed=None):

    label_fontsize = 18
    # legend_fontsize = 22
    marker_size = 12
    marker_style = "h"
    alpha = 0.5

    unique_folders = df['folder_name'].unique()
    print(f"{unique_folders}\n")
    folder_color_map = {folder: plt.cm.get_cmap('tab20')(i) for i, folder in enumerate(unique_folders)}
    # Plot the data
    fig = plt.figure(
        num=None, figsize=(14, 18), dpi=200, facecolor="w", edgecolor="gray"
    )
    fig.subplots_adjust(
        left=0.01, right=0.95, top=0.95, bottom=0.01, wspace=0.02, hspace=0.1
    )

    gs = fig.add_gridspec(5, 1)
    axs1 = fig.add_subplot(gs[0, 0])
    # Plot with different colors for different folder names
    for folder in unique_folders:
        folder_df = df[df['folder_name'] == folder]
        axs1.plot(
            folder_df.index, folder_df["+5.2V_Imon"], label=f"{folder} - +5.2V_Imon", marker=marker_style, linestyle='None',
            lw=0, markersize=marker_size, color=folder_color_map[folder], alpha=alpha
        )

    # axs1.plot(
    #     df.index, df["+5.2V_Imon"], label="+5.2V_Imon", marker=marker_style, linestyle=None, lw=0, markersize=marker_size
    # )
    # # axs1.set_title("+5.2V_Imon")
    #  axs1.legend(fontsize=legend_fontsize, loc="best")
    # axs1.grid()
    # Hide the x-axis labels
    plt.setp(axs1.get_xticklabels(), visible=False)
    # Set the y-axis limits to 1.1 times the maximum annd 0.9 times the minimum value
    axs1.set_ylim(
        0.9 * df["+5.2V_Imon"].min(), 1.1 * df["+5.2V_Imon"].max()
    )
    axs1.set_ylabel("+5.2V_Imon (mA)", fontsize=label_fontsize)

    axs2 = fig.add_subplot(gs[1, 0])
    for folder in unique_folders:
        folder_df = df[df['folder_name'] == folder]
        axs2.plot(
            folder_df.index, folder_df["+10V_Imon"] / 1e3, label=f"{folder} - +10V_Imon", marker=marker_style, linestyle='None',
            lw=0, markersize=marker_size, color=folder_color_map[folder], alpha=alpha
        )

    # axs2.set_title("+10V_Imon")
    # axs2.legend(fontsize=legend_fontsize, loc="best")
    # axs2.grid()
    # Hide the x-axis labels
    plt.setp(axs2.get_xticklabels(), visible=False)
    # Set the y-axis limits to 1.1 times the maximum annd 0.9 times the minimum value
    axs2.set_ylim(
        0.9 * df["+10V_Imon"].min() / 1e3, 1.1 * df["+10V_Imon"].max() / 1e3
    )
    axs2.set_ylabel("+10V_Imon (mA)", fontsize=label_fontsize)

    axs3 = fig.add_subplot(gs[2, 0])
    for folder in unique_folders:
        folder_df = df[df['folder_name'] == folder]
        axs3.plot(
            folder_df.index, folder_df["+3.3V_Imon"], label=f"{folder} - +3.3V_Imon", marker=marker_style, linestyle='None',
            lw=0, markersize=marker_size, color=folder_color_map[folder], alpha=alpha
        )
    # axs3.set_title("+3.3V_Imon")
    # axs3.legend(fontsize=legend_fontsize, loc="lower right")
    # axs3.grid()

    # Hide the x-axis labels
    plt.setp(axs3.get_xticklabels(), visible=False)
    # Set the y-axis limits to 1.1 times the maximum annd 0.9 times the minimum value
    axs3.set_ylim(
        0.9 * df["+3.3V_Imon"].min(), 1.1 * df["+3.3V_Imon"].max()
    )
    axs3.set_ylabel("+3.3V_Imon (mA)", fontsize=label_fontsize)

    axs4 = fig.add_subplot(gs[3, 0])
    for folder in unique_folders:
        folder_df = df[df['folder_name'] == folder]
        axs4.plot(
            folder_df.index, folder_df["AnodeVoltMon"] / 1e3 , label=f"{folder} - AnodeVoltMon", marker=marker_style, linestyle='None',
            lw=0, markersize=marker_size, color=folder_color_map[folder], alpha=alpha
        )

    # axs4.set_title("AnodeVoltMon")
    # axs4.legend(fontsize=legend_fontsize, loc="best")
    # axs4.grid()
    # Hide the x-axis labels
    plt.setp(axs4.get_xticklabels(), visible=False)
    # Set the y-axis limits to 1.1 times the maximum annd 0.9 times the minimum value
    axs4.set_ylim(
        0.9 * df["AnodeVoltMon"].min() / 1e3, 1.1 * df["AnodeVoltMon"].max() / 1e3
    )
    axs4.set_ylabel("AnodeVoltMon (V)", fontsize=label_fontsize)

    axs5 = fig.add_subplot(gs[4, 0])
    for folder in unique_folders:
        folder_df = df[df['folder_name'] == folder]
        axs5.plot(
            folder_df.index, folder_df["+28V_Imon"], label=f"{folder} - +28V_Imon", marker=marker_style, linestyle='None',
            lw=0, markersize=marker_size, color=folder_color_map[folder], alpha=alpha
        )

    # axs5.set_title("+28V_Imon")
    # axs5.legend(fontsize=0.25 * legend_fontsize, loc="best")
    # axs5.grid()
    # Hide the x-axis labels
    plt.setp(axs5.get_xticklabels(), rotation=45, ha="right")
    # Set the y-axis limits to 1.1 times the maximum annd 0.9 times the minimum value
    axs5.set_ylim(
        0.9 * df["+28V_Imon"].min(), 1.1 * df["+28V_Imon"].max()
    )
    axs5.set_ylabel("+28V_Imon (mA)", fontsize=label_fontsize)

    # For each y-axis, set the label and tick label font size
    for ax in fig.get_axes():
        # ax.set_ylabel("Current (mA)", fontsize=label_fontsize)
        ax.tick_params(axis="both", which="major", labelsize=label_fontsize)

    # Set the x-axis limits
    if x_limit is not None:
        for ax in fig.get_axes():
            ax.set_xlim(x_limit)

    # Add another axis for the legend in two columns
    # axs6 = fig.add_subplot(gs[5, 0])
    # axs6.axis("off")
    # handles, labels = axs1.get_legend_handles_labels()
    # axs6.legend(handles, labels, fontsize=0.5 * legend_fontsize, loc="center", ncol=2)

    # Save the figure
    save_file_name = save_file_name + f"{random_seed}.{format}"
    plt.savefig(save_file_name, dpi=200, bbox_inches="tight", pad_inches=0.1, format=format)


def make_plots_indiv(df_no_hv, df_hv, plot_key_list, save_file_name, format="pdf", x_limit=None, random_seed=None):

    label_fontsize = 18
    # legend_fontsize = 22
    marker_size = 12
    marker_style = "h"
    alpha = 0.5

    unique_folders_no_hv = df_no_hv['folder_name'].unique()
    folder_color_map = {folder: plt.cm.get_cmap('tab20')(i) for i, folder in enumerate(unique_folders_no_hv)}

    unique_folders_hv = df_hv['folder_name'].unique()
    folder_color_map_hv = {folder: plt.cm.get_cmap('tab20')(i) for i, folder in enumerate(unique_folders_hv)}

    for plot_key in plot_key_list:
        # Plot the data
        fig = plt.figure(
            num=None, figsize=(15, 8.5), dpi=200, facecolor="w", edgecolor="gray"
        )
        fig.subplots_adjust(
            left=0.01, right=0.95, top=0.95, bottom=0.01, wspace=0.02, hspace=0.05
        )

        gs = fig.add_gridspec(2, 1)
        axs1 = fig.add_subplot(gs[0, 0])
        # Plot with different colors for different folder names
        for folder in unique_folders_no_hv:
            folder_df_no_hv = df_no_hv[df_no_hv['folder_name'] == folder]
            if plot_key == "+10V_Imon" or plot_key == "AnodeVoltMon":
                folder_df_no_hv[plot_key] = folder_df_no_hv[plot_key] / 1e3
            axs1.plot(
                folder_df_no_hv.index, folder_df_no_hv[plot_key], label=f"{folder} - plot_key", marker=marker_style, linestyle='None',
                lw=0, markersize=marker_size, color=folder_color_map[folder], alpha=alpha
            )

        # Hide the x-axis labels
        plt.setp(axs1.get_xticklabels(), visible=False)
        # Set the y-axis limits to 1.1 times the maximum annd 0.9 times the minimum value
        if plot_key == "+10V_Imon" or plot_key == "AnodeVoltMon":
            axs1.set_ylim(
                0.9 * df_no_hv[plot_key].min() / 1e3, 1.1 * df_no_hv[plot_key].max() / 1e3
            )
        else:
            axs1.set_ylim(
                0.9 * df_no_hv[plot_key].min(), 1.1 * df_no_hv[plot_key].max()
            )
        axs1.set_ylabel(f"{plot_key} (mA)", fontsize=label_fontsize)
        # For each y-axis, set the label and tick label font size
        for ax in fig.get_axes():
            # ax.set_ylabel("Current (mA)", fontsize=label_fontsize)
            ax.tick_params(axis="both", which="major", labelsize=label_fontsize)

        # On the top right, add a box that says "No HV" in white color with green background
        axs1.text(0.95, 0.95, "HV OFF", fontsize=2 * label_fontsize, color="white",
                  backgroundcolor="green", transform=axs1.transAxes, ha="right", va="top")

        axs2 = fig.add_subplot(gs[1, 0], sharex=axs1)
        # Plot with different colors for different folder names
        for folder in unique_folders_hv:
            folder_df_hv = df_hv[df_hv['folder_name'] == folder]
            if plot_key == "+10V_Imon" or plot_key == "AnodeVoltMon":
                folder_df_hv[plot_key] = folder_df_hv[plot_key] / 1e3
            axs2.plot(
                folder_df_hv.index, folder_df_hv[plot_key], label=f"{folder} - plot_key", marker=marker_style, linestyle='None',
                lw=0, markersize=marker_size, color=folder_color_map_hv[folder], alpha=alpha
            )

        # Set the y-axis limits to 1.1 times the maximum annd 0.9 times the minimum value
        if plot_key == "+10V_Imon" or plot_key == "AnodeVoltMon":
            axs2.set_ylim(
                0.9 * df_hv[plot_key].min() / 1e3, 1.1 * df_hv[plot_key].max() / 1e3
            )
        else:
            axs2.set_ylim(
                0.9 * df_hv[plot_key].min(), 1.1 * df_hv[plot_key].max()
            )
        axs2.set_ylabel(f"{plot_key} (mA)", fontsize=label_fontsize)
        # Set the x-axis label
        axs2.set_xlabel("Time", fontsize=label_fontsize)
        # For each y-axis, set the label and tick label font size
        for ax in fig.get_axes():
            # ax.set_ylabel("Current (mA)", fontsize=label_fontsize)
            ax.tick_params(axis="both", which="major", labelsize=label_fontsize,)
            # Rotate the tick labels by 45 degrees
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # On the top right, add a box that says "HV" in white color with red background
        axs2.text(0.95, 0.95, "HV ON", fontsize=2 * label_fontsize, color="white",
                  backgroundcolor="red", transform=axs2.transAxes, ha="right", va="top")
        # Set the x-axis limits
        if x_limit is not None:
            for ax in fig.get_axes():
                ax.set_xlim(x_limit)

        # Save the figure
        save_file_name_new = save_file_name + f"{plot_key}_{random_seed}.{format}"
        plt.savefig(save_file_name_new, dpi=200, bbox_inches="tight", pad_inches=0.1, format=format)
        plt.close(fig)
        print(f"Saved {save_file_name_new}.")


# The HV file
file_name_hv = f"../data/hk_testings/filtered_data_{random_seed}_random_seed-hv.csv"
df_hv = pd.read_csv(file_name_hv)

# Convert the date column from YYYYMMDD format to datetime format
df_hv["datetime"] = pd.to_datetime(df_hv["date"], format="%Y%m%d")

# If the consecutive datetimes are same, then add 4 hours to the next datetime
for i in range(1, len(df_hv)):
    if df_hv["datetime"][i] == df_hv["datetime"][i - 1]:
        df_hv["datetime"][i] = df_hv["datetime"][i] + pd.Timedelta(hours=4)

# Set the datetime column as the index
df_hv = df_hv.set_index("datetime")

plot_key_list_hv = ["+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon"]

# The non-HV file
file_name_no_hv = f"../data/hk_testings/filtered_data_{random_seed}_random_seed-no_hv.csv"
df_no_hv = pd.read_csv(file_name_no_hv)

# Convert the date column from YYYYMMDD format to datetime format
df_no_hv["datetime"] = pd.to_datetime(df_no_hv["date"], format="%Y%m%d")

# If the consecutive datetimes are same, then add 4 hours to the next datetime
for i in range(1, len(df_no_hv)):
    if df_no_hv["datetime"][i] == df_no_hv["datetime"][i - 1]:
        df_no_hv["datetime"][i] = df_no_hv["datetime"][i] + pd.Timedelta(hours=4)

# Set the datetime column as the index
df_no_hv = df_no_hv.set_index("datetime")

# Sort the dataframe by the datetime index
df_no_hv = df_no_hv.sort_index()

plot_key_list_no_hv = ["+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon"]

# Define the x-limit for the plots
x_limit_hv = (df_hv.index.min(), df_hv.index.max())
x_limit_no_hv = (df_no_hv.index.min(), df_no_hv.index.max())

# Set the x-limit to the minimum and maximum of the two x-limits
x_limit = (min(x_limit_hv[0], x_limit_no_hv[0]), max(x_limit_hv[1], x_limit_no_hv[1]))

# Add 2 weeks to the maximum x-limit and subtract 2 weeks from the minimum x-limit
x_limit = (x_limit[0] - pd.Timedelta(weeks=2), x_limit[1] + pd.Timedelta(weeks=5))

# Make the plots
make_plots(df_hv, plot_key_list_hv, "../data/hk_testings/hv_plots", format="png", x_limit=x_limit)
make_plots(df_no_hv, plot_key_list_no_hv, "../data/hk_testings/no_hv_plots", format="png", x_limit=x_limit)

# make_plots_indiv(df_no_hv, df_hv, plot_key_list_no_hv, "../data/hk_testings/figures/", format="png", x_limit=x_limit)
"""