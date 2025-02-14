import importlib
import datetime
import numpy as np
import pandas as pd
import glob

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


import lxi_misc_codes as lmsc
import temp_lxi_pipeline_file as lpf

importlib.reload(lmsc)
importlib.reload(lpf)


def get_data_dataframes(time_threshold=10, t_start="2025-02-14 00:00:00", t_end="2025-02-17 00:00:00"):

    # Download data
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
    print(f"Number of files: {len(file_val_list)}")

    # Selecct the files that are within the time range
    file_val_list = [
        file_val
        for file_val in file_val_list
        if (int(file_val.split("/")[-1].split("_")[2]) >= t_start_unix)
        and (int(file_val.split("/")[-1].split("_")[2]) <= t_end_unix)
    ]

    # Copy all the files in the list to the "quiescent_data" folder
    for file_val in file_val_list:
        # Check if the file exists in the "quiescent_data" folder
        if not Path(f"../data/from_LEXI/quiescent_data/{Path(file_val).name}").exists():
            # Copy the files to the "quiescent_data" folder
            Path(file_val).replace(f"../data/from_LEXI/quiescent_data/{Path(file_val).name}")
        else:
            print(f"File {Path(file_val).name} already exists in the quiescent_data folder")

    print(f"Number of files within the time range: {len(file_val_list)}")

    df_hk, df_sci, df_sci_l1b, file_name_hk, file_name_sci = lpf.read_binary_file(file_val="../data/from_LEXI/quiescent_data", t_start=t_start, t_end=t_end, multiple_files=True)

    return df_hk
