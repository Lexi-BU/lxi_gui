import os
import pandas as pd
import csv
from pathlib import Path
from matplotlib import pyplot as plt
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

    key_list = [
        "+5.2V_Imon",
        "+10V_Imon",
        "+3.3V_Imon",
        "AnodeVoltMon",
        "+28V_Imon",
        "HVmcpMan",
        "DeltaEvntCount",
    ]
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
                writer.writerow(
                    [folder_name] + [file_list] + [data_dict[key] for key in key_list]
                )
        # return data_dict


if __name__ == "__main__":
    directory_path = "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/hk_testings/"
    folder_list = list_folders_in_directory(directory_path)

    count = 0
    for folder_path in folder_list[:]:
        count += 1
        data = read_data_from_folder(
            folder_path=folder_path + "/",
            save_file_name="../data/hk_testings/median_data.csv",
        )
        print(f"Processed {count} folders out of {len(folder_list)}.")
        continue

# Read the data from the median_data.csv file
df = pd.read_csv("../data/hk_testings/median_data.csv")

key_list = [
    "+5.2V_Imon",
    "+10V_Imon",
    "+3.3V_Imon",
    "AnodeVoltMon",
    "+28V_Imon",
    "HVmcpMan",
    "DeltaEvntCount",
]
# If the value of all the keys in the key_list is nan, then remove the row
df = df.dropna(subset=key_list, how="all")

# Get a list of the unique folder names
folder_names = df["folder_name"].unique()

# For each folder name, select a random row corresponding to the folder name and add it to a new
# dataframe
df_filtered = pd.DataFrame()
random_seed = 42
for folder_name in folder_names:
    df_temp = df[df["folder_name"] == folder_name]
    try:
        df_temp = df_temp.sample(n=5, random_state=random_seed)
    except Exception:
        df_temp = df_temp.sample(n=1, random_state=random_seed)
    df_filtered = pd.concat([df_filtered, df_temp])

# Save the filtered data to a new csv file
df_filtered.to_csv(
    f"../data/hk_testings/filtered_data_{random_seed}_random_seed.csv", index=False
)


file_name_hv = "../data/hk_testings/filtered_data_42_random_seed-hv.csv"
df = pd.read_csv(file_name_hv)

# Convert the date column from YYYYMMDD format to datetime format
df["datetime"] = pd.to_datetime(df["date"], format="%Y%m%d")

# If the consecutive datetimes are same, then add 4 hours to the next datetime
for i in range(1, len(df)):
    if df["datetime"][i] == df["datetime"][i - 1]:
        df["datetime"][i] = df["datetime"][i] + pd.Timedelta(hours=4)

# Set the datetime column as the index
df = df.set_index("datetime")

ploit_key_list = ["+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon"]

# Plot the data
fig, ax = plt.subplots(5, 1, figsize=(20, 15))
for i, key in enumerate(ploit_key_list):
    ax[i].plot(
        df.index, df[key], label=key, marker="o", linestyle=None, lw=0, markersize=5
    )
    ax[i].set_title(key)
    ax[i].legend()
    ax[i].grid()
# plt.show()
plt.savefig("../data/hk_testings/filtered_data_42_random_seed-hv.png")


file_name_no_hv = "../data/hk_testings/filtered_data_42_random_seed-no_hv.csv"
df = pd.read_csv(file_name_no_hv)

# Convert the date column from YYYYMMDD format to datetime format
df["datetime"] = pd.to_datetime(df["date"], format="%Y%m%d")

# If the consecutive datetimes are same, then add 4 hours to the next datetime
for i in range(1, len(df)):
    if df["datetime"][i] == df["datetime"][i - 1]:
        df["datetime"][i] = df["datetime"][i] + pd.Timedelta(hours=4)

# Set the datetime column as the index
df = df.set_index("datetime")

ploit_key_list = ["+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon"]

# Plot the data
fig, ax = plt.subplots(5, 1, figsize=(20, 15))
for i, key in enumerate(ploit_key_list):
    ax[i].plot(
        df.index, df[key], label=key, marker="o", linestyle=None, lw=0, markersize=5
    )
    ax[i].set_title(key)
    ax[i].legend()
    ax[i].grid()
# plt.show()
plt.savefig("../data/hk_testings/filtered_data_42_random_seed-no_hv.png")
