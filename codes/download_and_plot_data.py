import datetime
import glob
import importlib
import shutil
from pathlib import Path

import lxi_misc_codes as lmsc
import numpy as np
import pandas as pd
import temp_lxi_pipeline_file as lpf
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

importlib.reload(lmsc)
importlib.reload(lpf)


def get_data_dataframes(
    time_threshold=10,
    t_start="2025-02-14 00:00:00",
    t_end="2025-02-19 00:00:00",
    download_data=True,
    all_files=False,
):

    # Download data
    if download_data:
        lmsc.download_latest_files(time_threshold=time_threshold)

    folder_val = "../data/from_LEXI/orbit/"
    folder_val = Path(folder_val).expanduser().resolve()

    # Compute t_start and t_end in unix time
    dt_start = datetime.datetime.strptime(t_start, "%Y-%m-%d %H:%M:%S")
    dt_end = datetime.datetime.strptime(t_end, "%Y-%m-%d %H:%M:%S")

    t_start_unix = dt_start.replace(tzinfo=datetime.timezone.utc).timestamp()
    t_end_unix = dt_end.replace(tzinfo=datetime.timezone.utc).timestamp()

    # Get the file name
    folder_val_str = str(folder_val)
    # Recursively, within two levels, get all the "dat" files
    file_val_list = glob.glob(folder_val_str + "/**/*.dat", recursive=True)
    print(f"Total number of files in the folder: \033[1;90m{len(file_val_list)}\033[0m\n")

    # Select the files that are within the time range
    file_val_list = [
        file_val
        for file_val in file_val_list
        if (int(file_val.split("/")[-1].split("_")[2]) >= t_start_unix)
        and (int(file_val.split("/")[-1].split("_")[2]) <= t_end_unix)
    ]
    # If file_val_list is more than 24, then select the last 24 files
    if not all_files:
        if len(file_val_list) > 25:
            file_val_list = file_val_list[-25:]
            # Get the maximum time from the file names
            max_time = max(
                [int(file_val.split("/")[-1].split("_")[2]) for file_val in file_val_list]
            )
            # Convert the maximum time to datetime
            t_end = datetime.datetime.fromtimestamp(max_time, tz=datetime.timezone.utc)
            # Define t_end as 2 hours before t_start
            t_start = (t_end - datetime.timedelta(hours=2, minutes=10)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            t_end = t_end.strftime("%Y-%m-%d %H:%M:%S")

    # Copy all the files in the list to the "quiescent_data" folder
    for file_val in file_val_list:
        # Check if the file exists in the "quiescent_data" folder
        if not Path(f"../data/from_LEXI/quiescent_data/{Path(file_val).name}").exists():
            # Copy the files to the "quiescent_data" folder
            shutil.copy(file_val, "../data/from_LEXI/quiescent_data")
        else:
            # print(f"File {Path(file_val).name} already exists in the quiescent_data folder")
            pass

    print(f"Number of files within the time range: {len(file_val_list)}")

    df_hk, df_sci, df_sci_l1b, file_name_hk, file_name_sci = lpf.read_binary_file(
        file_val="../data/from_LEXI/quiescent_data",
        t_start=t_start,
        t_end=t_end,
        multiple_files=True,
    )

    if all_files:
        df_hk = df_hk.loc[df_hk.index > (df_hk.index[0] + pd.Timedelta(seconds=600))]
    else:
        # Ignore first 600 seconds of data
        #  df_hk = df_hk.loc[df_hk.index > (df_hk.index[0] + pd.Timedelta(seconds=600))]
        pass
    return df_hk, t_start, t_end
