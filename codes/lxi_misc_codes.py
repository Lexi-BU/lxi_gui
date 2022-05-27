from tabulate import tabulate
import global_variables
import numpy as np


def print_time_details(file_type=None, start_time=None, end_time=None):
    """
    Prints the details of the time values in different files in the data base for both SCI and
    HK files in a nice tabular format as well as the name of the loaded files.

    Parameters
    ----------
    file_type : str or list
        Type of file. Default is None.
    start_time : float
        Start time. Default is None.
    end_time : float
        End time. Default is None.

    Returns
    -------
        None
    """
    if file_type is None:
        file_type_list = ['sci', 'hk']
    else:
        if hasattr(file_type, '__len__'):
            file_type_list = file_type
            file_type = []
        else:
            file_type_list = [file_type]
            file_type = []

    for file_type in file_type_list:
        try:
            df_all = global_variables.all_file_details[f"df_all_{file_type}"]
            # df_slice = global_variables.all_file_details[f"df_all_{file_type}"]
            file_name = global_variables.all_file_details[f"file_name_{file_type}"]
            print(f"\n \x1b[1;32;255m Displaying values for {file_name} \x1b[0m")
            print(tabulate(
                [[f"Minimum time in the {file_type} file", df_all.index.min()],
                 [f"Maximum time in the  {file_type} file", df_all.index.max()],
                 # [f"Minimum time in the sliced  {file_type} file", df_slice.index.min()],
                 # [f"Maximum time in the sliced  {file_type} file", df_slice.index.max()],
                 ["Start time from widget", start_time],
                 ["End time from widget", end_time]],
                headers=["Parameter", "Value"], tablefmt="fancy_grid", floatfmt=".2f",
                numalign="center"))
        except Exception:
            pass


def insert_file_name(file_load_entry=None, tk=None, file_name=None):
    """
    If a new file is loaded, then insert the file name into the entry box

    Parameters
    ----------
    file_load_entry : tkinter.Entry
        The entry box where the file name is inserted
    tk : tkinter.Tk
        The main window
    file_name : str
        The file name to be inserted

    Returns
    -------
        None
    """
    file_name_short = file_name.split('/')[-1]
    file_load_entry.delete(0, tk.END)
    file_load_entry.insert(0, file_name_short)


def curve_fit_func(x, a, b, c):
    """
    Get the Gaussian curve function

    Parameters
    ----------
    x : numpy.ndarray
        The x values
    a : float
        The amplitude of the curve
    b : float
        The mean of the curve
    c : float
        The standard deviation of the curve
    """
    return a * np.exp(-(x - b) ** 2 / (2 * c ** 2))


def fwhm(x, y):
    """
    Calculate the full width at half maximum of a curve

    Parameters
    ----------
    x : numpy.ndarray
        The x values
    y : numpy.ndarray
        The y values
    """
    half_max = np.max(y) / 2.
    left_idx = np.where(y > half_max)[0][0]
    right_idx = np.where(y > half_max)[0][-1]
    return x[right_idx] - x[left_idx]


def ts_option_update():
    print(global_variables.all_file_details["df_slice_hk"].columns.tolist())
    return global_variables.all_file_details["df_slice_hk"].columns.tolist()
