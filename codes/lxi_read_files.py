import importlib
from tkinter import filedialog

import pandas as pd

import global_variables
import lxi_read_binary_files as lxrb

importlib.reload(lxrb)


def open_file_sci(start_time=None, end_time=None):
    # define a global variable for the file name

    file_val = filedialog.askopenfilename(initialdir="../data/processed_data/sci/",
                                          title="Select file",
                                          filetypes=(("csv files", "*.csv"),
                                                     ("all files", "*.*"))
                                          )
    # Cut path to the file off
    file_name_sci = file_val.split('/')[-1]
    global_variables.all_file_details['file_name_sci'] = file_name_sci

    df_all_sci, df_slice_sci = read_csv_sci(file_val=file_val, t_start=start_time, t_end=end_time)
    global_variables.all_file_details['df_slice_sci'] = df_slice_sci
    global_variables.all_file_details['df_all_sci'] = df_all_sci
    print(f"\n \x1b[1;32;255m Loaded {file_name_sci} in the data base \x1b[0m")

    # print(tabulate(
    #     [["Minimum time in the SCI file", df_all_sci.index.min()],
    #      ["Maximum time in the SCI file", df_all_sci.index.max()],
    #      ["Minimum time in the sliced SCI file", df_slice_sci.index.min()],
    #      ["Maximum time in the sliced SCI file", df_slice_sci.index.max()]],
    #     headers=["Parameter", "Value"], tablefmt="fancy_grid", floatfmt=".2f",
    #     numalign="center"))

    return file_val


def open_file_hk():
    # define a global variable for the file name
    file_val = filedialog.askopenfilename(initialdir="../data/processed_data/hk/",
                                          title="Select file",
                                          filetypes=(("csv files", "*.csv"),
                                                     ("all files", "*.*"))
                                          )
    # Cut path to the file off
    file_name_hk = file_val.split('/')[-1]
    global_variables.all_file_details['file_name_hk'] = file_name_hk

    df_all_hk, df_slice_hk = read_csv_hk(file_val)
    global_variables.all_file_details['df_slice_hk'] = df_slice_hk
    global_variables.all_file_details['df_all_hk'] = df_all_hk
    print(f"\n \x1b[1;32;255m Loaded {file_name_hk} in the data base \x1b[0m")
    return file_val


def open_file_b():
    # define a global variable for the file name
    file_val = filedialog.askopenfilename(initialdir="../data/raw_data/",
                                          title="Select file",
                                          filetypes=(("text files", "*.txt"),
                                                     ("all files", "*.*"))
                                          )

    # Cut path to the file off
    file_name_b = file_val.split('/')[-1]
    (df_slice_hk, file_name_hk, df_slice_sci, file_name_sci, df_all_hk, df_all_sci
     ) = read_binary_file(file_val)
    global_variables.all_file_details["file_name_b"] = file_name_b
    global_variables.all_file_details["file_name_hk"] = file_name_hk
    global_variables.all_file_details["file_name_sci"] = file_name_sci

    global_variables.all_file_details["df_slice_hk"] = df_slice_hk
    global_variables.all_file_details["df_slice_sci"] = df_slice_sci
    global_variables.all_file_details["df_all_hk"] = df_all_hk
    global_variables.all_file_details["df_all_sci"] = df_all_sci

    print(
        f"\n \x1b[1;32;255m Loaded {file_name_b} in the data base, and the csv file for HK and "
        f"SCI data have been saved to ''{file_name_hk}'' and ''{file_name_sci}''\x1b[0m")

    return file_val


def read_csv_sci(file_val=None, t_start=None, t_end=None):
    """
    Reads a csv file and returns a pandas dataframe for the selected time range along with x and
    y-coordinates.

    Parameters
    ----------
    file_val : str
        Path to the input file. Default is None.
    t_start : float
        Start time of the data. Default is None.
    t_end : float
        End time of the data. Default is None.
    """
    df = pd.read_csv(file_val)

    # Replace index with timestamp
    df.set_index('TimeStamp', inplace=True)

    # Sort the dataframe by timestamp
    df = df.sort_index()

    if t_start is None:
        t_start = df.index.min()
    if t_end is None:
        t_end = df.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_sci = df.loc[t_start:t_end]

    # Find the x and y coordinates from the voltage values.
    df_slice_sci['x_val'] = df_slice_sci.Channel1 / (df_slice_sci.Channel1 + df_slice_sci.Channel2)
    df_slice_sci['y_val'] = df_slice_sci.Channel3 / (df_slice_sci.Channel3 + df_slice_sci.Channel4)

    return df, df_slice_sci


def read_csv_hk(file_val=None, t_start=None, t_end=None):
    """
    Reads a csv file and returns a pandas dataframe for the selected time range along with x and
    y-coordinates.

    Parameters
    ----------
    file_val : str
        Path to the input file. Default is None.
    t_start : float
        Start time of the data. Default is None.
    t_end : float
        End time of the data. Default is None.
    """

    global df_slice_hk
    df = pd.read_csv(file_val)

    # Replace index with timestamp
    df.set_index('TimeStamp', inplace=True)

    # Sort the dataframe by timestamp
    df = df.sort_index()

    if t_start is None:
        t_start = df.index.min()
    if t_end is None:
        t_end = df.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_hk = df.loc[t_start:t_end]

    return df, df_slice_hk


def read_binary_file(file_val=None, t_start=None, t_end=None):

    df_hk, file_name_hk = lxrb.read_binary_data_hk(
        in_file_name=file_val,
        save_file_name=None,
        number_of_decimals=6
    )

    df_sci, file_name_sci = lxrb.read_binary_data_sci(
        in_file_name=file_val,
        save_file_name=None,
        number_of_decimals=6
    )

    # Replace index with timestamp
    df_hk.set_index('TimeStamp', inplace=True)
    df_sci.set_index('TimeStamp', inplace=True)

    # Sort the dataframe by timestamp
    df_hk = df_hk.sort_index()
    df_sci = df_sci.sort_index()

    if t_start is None:
        t_start = df_sci.index.min()
    if t_end is None:
        t_end = df_sci.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_hk = df_hk.loc[t_start:t_end]
    df_slice_sci = df_sci.loc[t_start:t_end]

    return df_slice_hk, file_name_hk, df_slice_sci, file_name_sci, df_hk, df_sci
