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


if __name__ == "__main__":
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
