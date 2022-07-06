import importlib
from tkinter import filedialog

import numpy as np
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
    global_variables.all_file_details['file_name_sci'] = file_val

    df_all_sci, df_slice_sci = read_csv_sci(file_val=file_val, t_start=start_time, t_end=end_time)
    global_variables.all_file_details['df_slice_sci'] = df_slice_sci
    global_variables.all_file_details['df_all_sci'] = df_all_sci
    print(f"\n \x1b[1;32;255m Loaded {file_name_sci} in the data base \x1b[0m")

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
    global_variables.all_file_details['file_name_hk'] = file_val

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
    file_name_b = file_val
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
        f"\n Loaded \x1b[1;32;255m{file_name_b}\x1b[0m in the data base,\n  and the csv file for "
        f"\x1b[1;32;255m HK \x1b[0m and \x1b[1;32;255m SCI \x1b[0m data have been saved to \n "
        f"HK File : \x1b[1;32;255m{file_name_hk} \x1b[0m \n and \n Sci File: "
        f"\x1b[1;32;255m{file_name_sci}\x1b[0m")

    return file_val


def compute_position(v1=None, v2=None, n_bins=401, bin_min=0, bin_max=4):
    """
    The function computes the position of the particle in the xy-plane. The ratios to compute
    both the x and y position are taken from Dennis' code. The code computes the offset of the
    four voltages as measured by LEXI. We then subtract the offset from the four voltages to get
    the shifted voltages and then compute the position of the particle based on the shifted
    voltages.

    Parameters
    ----------
    v1 : float
        Voltage of the first channel. Default is None.
    v2 : float
        Voltage of the second channel. Default is None.
    n_bins : int
        Number of bins to compute the position. Default is 401.
    bin_min : float
        Minimum value of the bin. Default is 0.
    bin_max : float
        Maximum value of the bin. Default is 4.

    Returns
    -------
    particle_pos : float
        position of the particle along one of the axis. Whether it gives x or y position depends
        on which voltages were provided. For example, if v1 and v3 were provided, then the x
        position is returned. Else if v4 and v2 were provided, then the y position is returned.
        It is important to note that the order of the voltages is important.
    v1_shift: float
        Offset corrected voltage of the first channel.
    v2_shift: float
        Offset corrected voltage of the second channel.
    """
    bin_size = (bin_max - bin_min) / (n_bins - 1)

    # make 1-D histogram of all 4 channels
    hist_v1 = np.histogram(v1, bins=n_bins, range=(bin_min, bin_max))
    hist_v2 = np.histogram(v2, bins=n_bins, range=(bin_min, bin_max))

    xx = bin_min + bin_size * np.arange(n_bins)

    # Find the index where the histogram is the maximum
    # NOTE/TODO: I don't quite understand why the offset is computed this way. Need to talk to
    # Dennis about this and get an engineering/physics reason for it.
    max_index_v1 = np.argmax(hist_v1[0][0:int(n_bins / 2)])
    max_index_v2 = np.argmax(hist_v2[0][0:int(n_bins / 2)])

    z1_min = 1000 * xx[max_index_v1]
    z2_min = 1000 * xx[max_index_v2]

    n1_z = z1_min / 1000
    n2_z = z2_min / 1000

    v1_shift = v1 - n1_z
    v2_shift = v2 - n2_z

    particle_pos = v2_shift / (v2_shift + v1_shift)

    return particle_pos, v1_shift, v2_shift


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

    df = pd.read_csv(file_val, index_col=False)

    # Check all the keys and find out which one has the word "time" in it
    for key in df.keys():
        if "time" in key.lower():
            time_col = key
            break
    # Rename the time column to TimeStamp
    df.rename(columns={time_col: 'TimeStamp'}, inplace=True)
    # Set the index to the time column
    df.set_index('TimeStamp', inplace=True)
    # Sort the dataframe by timestamp
    df = df.sort_index()

    if t_start is None:
        t_start = df.index.min()
    if t_end is None:
        t_end = df.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_sci = df.loc[t_start:t_end]

    # For both the sliced and entire dataframes, compute the x and y-coordinates and the shift in
    # the voltages
    x_slice, v1_shift_slice, v3_shift_slice = compute_position(v1=df_slice_sci['Channel1'],
                                                               v2=df_slice_sci['Channel3'],
                                                               n_bins=401, bin_min=0, bin_max=4)

    x, v1_shift, v3_shift = compute_position(v1=df['Channel1'], v2=df['Channel3'], n_bins=401,
                                             bin_min=0, bin_max=4)

    # Add the x-coordinate to the dataframe
    df_slice_sci.loc[:, 'x_val'] = x_slice
    df_slice_sci.loc[:, 'v1_shift'] = v1_shift_slice
    df_slice_sci.loc[:, 'v3_shift'] = v3_shift_slice

    df.loc[:, 'x_val'] = x
    df.loc[:, 'v1_shift'] = v1_shift
    df.loc[:, 'v3_shift'] = v3_shift

    y_slice, v4_shift_slice, v2_shift_slice = compute_position(v1=df_slice_sci['Channel4'],
                                                               v2=df_slice_sci['Channel2'],
                                                               n_bins=401, bin_min=0, bin_max=4)

    y, v4_shift, v2_shift = compute_position(v1=df['Channel4'], v2=df['Channel2'], n_bins=401,
                                             bin_min=0, bin_max=4)

    # Add the y-coordinate to the dataframe
    df_slice_sci.loc[:, 'y_val'] = y_slice
    df_slice_sci.loc[:, 'v4_shift'] = v4_shift_slice
    df_slice_sci.loc[:, 'v2_shift'] = v2_shift_slice

    df.loc[:, 'y_val'] = y
    df.loc[:, 'v4_shift'] = v4_shift
    df.loc[:, 'v2_shift'] = v2_shift

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

    # Check all the keys and find out which one has the word "time" in it
    for key in df.keys():
        if "time" in key.lower():
            time_col = key
            break
    # Rename the time column to TimeStamp
    df.rename(columns={time_col: 'TimeStamp'}, inplace=True)
    # Set the index to the time column
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
    """
    Reads the binary file using functions saved in the file "lxi_read_binary_data.py" and returns
    a pandas dataframe for the selected time range along with x and y-coordinates.

    Parameters
    ----------
    file_val : str
        Path to the input file. Default is None.
    t_start : float
        Start time of the data. Default is None.
    t_end : float
        End time of the data. Default is None.

    Returns
    -------
    df_slice_hk : pandas.DataFrame
        The Housekeeping dataframe for the selected time range.
    df_slice_sci : pandas.DataFrame
        The Science dataframe for the selected time range.
    df_hk : pandas.DataFrame
        The Housekeeping dataframe for the entire time range in the file.
    df_sci : pandas.DataFrame
        The Science dataframe for the entire time range in the file.
    file_name_hk : str
        The name of the Housekeeping file.
    file_name_sci : str
        The name of the Science file.
    """

    # Read the housekeeping data
    df_hk, file_name_hk = lxrb.read_binary_data_hk(
        in_file_name=file_val,
        save_file_name=None,
        number_of_decimals=6
    )

    # Read the science data
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

    # For both the sliced and entire dataframes, compute the x and y-coordinates and the shift in
    # the voltages
    x_slice, v1_shift_slice, v3_shift_slice = compute_position(v1=df_slice_sci['Channel1'],
                                                               v2=df_slice_sci['Channel3'],
                                                               n_bins=401, bin_min=0, bin_max=4)

    x, v1_shift, v3_shift = compute_position(v1=df_sci['Channel1'], v2=df_sci['Channel3'],
                                             n_bins=401, bin_min=0, bin_max=4)

    # Add the x-coordinate to the dataframe
    df_slice_sci.loc[:, 'x_val'] = x_slice
    df_slice_sci.loc[:, 'v1_shift'] = v1_shift_slice
    df_slice_sci.loc[:, 'v3_shift'] = v3_shift_slice

    df_sci.loc[:, 'x_val'] = x
    df_sci.loc[:, 'v1_shift'] = v1_shift
    df_sci.loc[:, 'v3_shift'] = v3_shift

    y_slice, v4_shift_slice, v2_shift_slice = compute_position(v1=df_slice_sci['Channel4'],
                                                               v2=df_slice_sci['Channel2'],
                                                               n_bins=401, bin_min=0, bin_max=4)

    y, v4_shift, v2_shift = compute_position(v1=df_sci['Channel4'], v2=df_sci['Channel2'],
                                             n_bins=401, bin_min=0, bin_max=4)

    # Add the y-coordinate to the dataframe
    df_slice_sci.loc[:, 'y_val'] = y_slice
    df_slice_sci.loc[:, 'v4_shift'] = v4_shift_slice
    df_slice_sci.loc[:, 'v2_shift'] = v2_shift_slice

    df_sci.loc[:, 'y_val'] = y
    df_sci.loc[:, 'v4_shift'] = v4_shift
    df_sci.loc[:, 'v2_shift'] = v2_shift

    return df_slice_hk, file_name_hk, df_slice_sci, file_name_sci, df_hk, df_sci
