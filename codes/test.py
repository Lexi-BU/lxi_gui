import numpy as np
import pandas as pd
import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


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
    return target_folder


def read_csv_file(csv_file):
    """Helper function to read a single CSV file."""
    return pd.read_csv(csv_file)


def read_sci_l1c_data():
    parent_folder = check_folder_structure()
    print(f"Reading data from: {parent_folder}\n")

    file_name_format = "lexi_payload_*_*_*_*_sci_output_L1c.csv"
    csv_files = np.sort(glob.glob(str(parent_folder / "**" / file_name_format), recursive=True))[:]

    print(f"Found \033[1;31m{len(csv_files)}\033[0m CSV files in the {parent_folder}\n")

    df_list = []
    with ThreadPoolExecutor() as executor:
        # Submit tasks to read CSV files in parallel
        future_to_file = {executor.submit(read_csv_file, csv_file): csv_file for csv_file in csv_files}

        for i, future in enumerate(as_completed(future_to_file)):
            csv_file = future_to_file[future]
            try:
                df = future.result()
                df_list.append(df)
                print(f"Reading file ==> \x1b[1;32;255m {np.round((i + 1) / len(csv_files) * 100, 3)}\x1b[0m % complete", end="\r")
            except Exception as e:
                print(f"Error reading file {csv_file}: {e}")

    df_all = pd.concat(df_list)

    # Set the Date column as the index
    df_all["Date"] = pd.to_datetime(df_all["Date"])
    df_all = df_all.set_index("Date", inplace=False)

    return df_all


def add_operation_numbers(df):
    """Add operation numbers and data points in parallel."""
    operation_number = 1
    number_of_data_points = 1
    start_time = time.time()  # Track start time

    def process_row(i):
        nonlocal operation_number, number_of_data_points
        if (df.index[i] - df.index[i - 1]).total_seconds() > 10800:
            operation_number += 1
            number_of_data_points = 1
        else:
            number_of_data_points += 1
        return i, operation_number, number_of_data_points

    with ThreadPoolExecutor() as executor:
        # Submit tasks to process rows in parallel
        future_to_index = {executor.submit(process_row, i): i for i in range(1, len(df))}

        for future in as_completed(future_to_index):
            i, op_num, data_points = future.result()
            df.loc[df.index[i], "number_of_data_points"] = data_points
            df.loc[df.index[i], "operation_number"] = op_num

            # Calculate elapsed time and estimated time remaining
            elapsed_time = time.time() - start_time
            avg_time_per_row = elapsed_time / i if i > 0 else 0
            estimated_total_time = avg_time_per_row * len(df)
            remaining_time = estimated_total_time - elapsed_time

            # Improved progress message with time estimates
            print(
                f"Progress: {np.round(i / len(df) * 100, 6)}% complete | "
                # f"Operation {op_num} of {len(df)} | "
                f"Elapsed: {np.round(elapsed_time, 6)}s | ",
                # f"Remaining: {np.round(remaining_time, 2)}s",
                end="\r"
            )

    return df


start_time = time.time()
read_data = True
if read_data:
    # Check the folder structure
    df = read_sci_l1c_data()
    # Add operation number to the data
    df["operation_number"] = 1
    df["number_of_data_points"] = 1

    # Parallelize the operation number assignment
    df = add_operation_numbers(df)

    end_time = time.time()

    print(f"\n\nTotal time taken: {np.round(end_time - start_time, 3)} seconds\n")