import importlib
import logging
import time
import threading
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt

import global_variables
import lxi_csv_to_cdf as lctc
import lxi_csv_to_csv as lctcsv
import lxi_file_read_funcs as lxrf
import lxi_gui_entry_box as lgeb
import numpy as np
import paramiko
from tabulate import tabulate

importlib.reload(lctc)
importlib.reload(lgeb)
importlib.reload(lctcsv)
importlib.reload(lxrf)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

# Check if the log folder exists. If not, create it
Path("../log").mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler("../log/lxi_misc_codes.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Global flag to control the blinking thread
thread_running = True


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
        file_type_list = ["sci", "hk"]
    else:
        if hasattr(file_type, "__len__"):
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
            print(
                f"\n Displaying values for \x1b[1;32;255m {file_name.split('/')[-1]} \x1b[0m"
            )
            print(
                tabulate(
                    [
                        [f"Minimum time in the {file_type} file", df_all.index.min()],
                        [f"Maximum time in the  {file_type} file", df_all.index.max()],
                        # [f"Minimum time in the sliced  {file_type} file", df_slice.index.min()],
                        # [f"Maximum time in the sliced  {file_type} file", df_slice.index.max()],
                        ["Start time from widget", start_time],
                        ["End time from widget", end_time],
                    ],
                    headers=["Parameter", "Value"],
                    tablefmt="fancy_grid",
                    floatfmt=".2f",
                    numalign="center",
                )
            )
            logger.info(f"Time details for {file_type} file printed")
        except Exception:
            logger.exception(f"Error in printing time details for {file_type} file")
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
    if file_name is not None:
        file_name_short = file_name.split("/")[-1]
        if file_load_entry is not None and tk is not None:
            file_load_entry.delete(0, tk.END)
            file_load_entry.insert(0, file_name_short)


# Write a function to change the state of a button to disabled if it was enabled and vice versa
def change_state(button=None):
    """
    Change the state of a button

    Parameters
    ----------
    button : tkinter.Button
        The button whose state is to be changed

    Returns
    -------
        None
    """
    if button is not None:
        state = button.cget("state")
        if state == "disabled":
            button.config(state="normal")
        elif state == "normal":
            button.config(state="disabled")


def load_folder(file_val=None, t_start=None, t_end=None, multiple_files=True):
    """
    Load a folder of files

    Parameters
    ----------
    file_val : str
        The folder name

    t_start : float
        The start time

    t_end : float
        The end time

    multiple_files : bool
        If True, then load multiple files. Default is True.

    Returns
    -------
        None
    """
    lxrf.open_file_b_multiple(
        file_val=file_val, t_start=t_start, t_end=t_end, multiple_files=multiple_files
    )

    return None


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
    return a * np.exp(-((x - b) ** 2) / (2 * c**2))


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
    half_max = np.max(y) / 2.0
    left_idx = np.where(y > half_max)[0][0]
    right_idx = np.where(y > half_max)[0][-1]
    return x[right_idx] - x[left_idx]


def ts_option_update():
    print(global_variables.all_file_details["df_slice_hk"].columns.tolist())
    return global_variables.all_file_details["df_slice_hk"].columns.tolist()


def diff_file_warnings():
    """
    Warn the user if the hk and sci files do not have the same time values (within 1 second)
    """
    try:
        hk_t_min = global_variables.all_file_details["df_all_hk"].index.min()
        hk_t_max = global_variables.all_file_details["df_all_hk"].index.max()
        sci_t_min = global_variables.all_file_details["df_all_sci"].index.min()
        sci_t_max = global_variables.all_file_details["df_all_sci"].index.max()
        if abs((hk_t_min - sci_t_min).total_seconds()) > 1:
            print(
                "\n \x1b[1;31;255m WARNING: The hk file does not have the same minimum time "
                "values as the sci file \x1b[0m"
            )
            print(
                f"The hk file has the minimum time value of \x1b[1;32;255m{hk_t_min} \x1b[0m"
                f"and the sci file has the minimum time value of \x1b[1;32;255m{sci_t_min}"
                f"\x1b[0m"
            )
        if abs((hk_t_max - sci_t_max).total_seconds()) > 1:
            print(
                "\n \x1b[1;31;255m WARNING: The hk file does not have the same maximum time "
                "values as the sci file \x1b[0m"
            )
            print(
                f"The hk file has the maximum time value of \x1b[1;32;255m{hk_t_max} \x1b[0m"
                f"and the sci file has the maximum time value of \x1b[1;32;255m{sci_t_max}"
                f"\x1b[0m"
            )
    except Exception:
        pass


def file_name_update(file_name=None, file_type=None):
    """
    Update the file name in the global variables

    Parameters
    ----------
    file_name : str
        The file name to be updated
    """
    if file_type == "sci":
        file_name = global_variables.all_file_details["file_name_sci"].split("/")[-1]
    elif file_type == "hk":
        file_name = global_variables.all_file_details["file_name_hk"].split("/")[-1]
    elif file_type == "b":
        file_name = global_variables.all_file_details["file_name_b"].split("/")[-1]
    diff_file_warnings()

    return file_name


def PinPullerTemp_func(vpc, hk_value, lxi_unit):
    PinPullerTemp = (hk_value * vpc - 2.73) * 100
    return PinPullerTemp


def OpticsTemp_func(vpc, hk_value, lxi_unit):
    OpticsTemp = (hk_value * vpc - 2.73) * 100
    return OpticsTemp


def LEXIbaseTemp_func(vpc, hk_value, lxi_unit):
    LEXIbaseTemp = (hk_value * vpc - 2.73) * 100
    return LEXIbaseTemp


def HVsupplyTemp_func(vpc, hk_value, lxi_unit):
    HVsupplyTemp = (hk_value * vpc - 2.73) * 100
    return HVsupplyTemp


def V_Imon_5_2_func(vpc, hk_value, lxi_unit):
    if lxi_unit == 1:
        V_Imon_5_2 = (hk_value * vpc) * 1e3 / 18
    elif lxi_unit == 2:
        V_Imon_5_2 = (hk_value * vpc - 1.129) * 1e3 / 21.456
    else:
        V_Imon_5_2 = (hk_value * vpc) * 1e3 / 18
    return V_Imon_5_2


def V_Imon_10_func(vpc, hk_value, lxi_unit):

    # NOTE: The 10 V current monitor value unit is not quite true. The value is in volts but the conversion factor is missing.
    V_Imon_10 = hk_value * vpc
    return V_Imon_10


def V_Imon_3_3_func(vpc, hk_value, lxi_unit):
    if lxi_unit == 1:
        V_Imon_3_3 = (hk_value * vpc + 0.0178) * 1e3 / 9.131
    elif lxi_unit == 2:
        V_Imon_3_3 = (hk_value * vpc - 0.029) * 1e3 / 18
    else:
        V_Imon_3_3 = (hk_value * vpc + 0.0178) * 1e3 / 9.131
    return V_Imon_3_3


def AnodeVoltMon_func(vpc, hk_value, lxi_unit):
    # NOTE: The anode voltage monitor value unit is not quite true. The value is in volts but the
    # conversion factor is missing.
    AnodeVoltMon = hk_value * vpc
    return AnodeVoltMon


def V_Imon_28_func(vpc, hk_value, lxi_unit):
    if lxi_unit == 1:
        V_Imon_28 = (hk_value * vpc + 0.00747) * 1e3 / 17.94
    elif lxi_unit == 2:
        V_Imon_28 = (hk_value * vpc + 0.00747) * 1e3 / 17.94
    else:
        V_Imon_28 = (hk_value * vpc + 0.00747) * 1e3 / 17.94
    return V_Imon_28


def ADC_Ground_func(vpc, hk_value, ADC_Ground):
    ADC_Ground = hk_value * vpc
    return ADC_Ground


def Cmd_count_func(vpc, hk_value, lxi_unit):
    Cmd_count = hk_value
    return Cmd_count


def Pinpuller_Armed_func(vpc, hk_value, lxi_unit):
    Pinpuller_Armed = hk_value
    return Pinpuller_Armed


def Unused1_func(vpc, hk_value, lxi_unit):
    Unused1 = hk_value
    return Unused1


def Unused2_func(vpc, hk_value, lxi_unit):
    Unused2 = hk_value
    return Unused2


def HVmcpAuto_func(vpc, hk_value, lxi_unit):
    HVmcpAuto = hk_value * vpc
    return HVmcpAuto


def HVmcpMan_func(vpc, hk_value, lxi_unit):
    HVmcpMan = hk_value * vpc
    return HVmcpMan


def hk_value_comp(ii=None, vpc=None, hk_value=None, hk_id=None, lxi_unit=None):
    ops = {
        "0": PinPullerTemp_func,
        "1": OpticsTemp_func,
        "2": LEXIbaseTemp_func,
        "3": HVsupplyTemp_func,
        "4": V_Imon_5_2_func,
        "5": V_Imon_10_func,
        "6": V_Imon_3_3_func,
        "7": AnodeVoltMon_func,
        "8": V_Imon_28_func,
        "9": ADC_Ground_func,
        "10": Cmd_count_func,
        "11": Pinpuller_Armed_func,
        "12": Unused1_func,
        "13": Unused2_func,
        "14": HVmcpAuto_func,
        "15": HVmcpMan_func,
    }
    chosen_func = ops.get(str(hk_id))
    if chosen_func is None:
        raise ValueError(f"No function found for hk_id {hk_id}")
    return chosen_func(vpc, hk_value, lxi_unit)


def save_csv():
    """
    The function, upon clicking the "Save CSV" button, saves the data in the csv file format in a
    folder names "csv". The name of the csv file is the same as the name of the input file, with
    "_updated" appended to it.
    """

    # NOTE: As of now this part of the code doesn't serve any purpose. However, it is kept here in
    # case we implement a thresholding feature in the future for the csv file.
    # (x_min_entry, x_max_entry, y_min_entry, y_max_entry, hist_bins_entry, c_min_entry,
    #  c_max_entry,
    #  density_status_var, norm_type_var, unit_type_var, v_min_thresh_entry, v_max_thresh_entry,
    #  v_sum_min_thresh_entry, v_sum_max_thresh_entry, cut_status_var, curve_fit_status_var,
    #  lin_corr_status_var, cmap_option) = lgeb.populate_entries(root=root)

    # x_min_entry_value = float(x_min_entry.get())
    # x_max_entry_value = float(x_max_entry.get())
    # y_min_entry_value = float(y_min_entry.get())
    # y_max_entry_value = float(y_max_entry.get())
    # hist_bins_entry_value = int(hist_bins_entry.get())
    # c_min_entry_value = float(c_min_entry.get())
    # c_max_entry_value = float(c_max_entry.get())
    # density_status_var_value = density_status_var.get()
    # norm_type_var_value = norm_type_var.get()
    # unit_type_var_value = unit_type_var.get()
    # v_min_thresh_entry_value = float(v_min_thresh_entry.get())
    # v_max_thresh_entry_value = float(v_max_thresh_entry.get())
    # v_sum_min_thresh_entry_value = float(v_sum_min_thresh_entry.get())
    # v_sum_max_thresh_entry_value = float(v_sum_max_thresh_entry.get())
    # cut_status_var_value = cut_status_var.get()
    # curve_fit_status_var_value = curve_fit_status_var.get()
    # lin_corr_status_var_value = lin_corr_status_var.get()
    # cmap_option_value = cmap_option.get()

    if global_variables.all_file_details:
        try:
            inputs = {
                "df": global_variables.all_file_details["df_all_sci"],
                "csv_file": global_variables.all_file_details["file_name_sci"],
            }
            lctcsv.lxi_csv_to_csv(**inputs)
        except Exception as e:
            print(
                f"\n \x1b[1;31;255m Error: \x1b[0m Could not save the csv file. Following exception"
                f" was raised: \n \x1b[1;31;255m {e} \x1b[0m is not defined. \n Check if a valid "
                f"Science csv file is loaded. \n"
            )
    else:
        logger.error("No file loaded/ no Data in the file")


def save_cdf():
    """
    The function, upon clicking the "Save CDF" button, saves the data in the csv file to a cdf file
    in a folder named "cdf". The name of the cdf file is the same as the name of the input file,
    with "cdf" appended to it.
    """
    if global_variables.all_file_details:
        try:
            inputs = {
                "df": global_variables.all_file_details["df_all_sci"],
                "csv_file": global_variables.all_file_details["file_name_sci"],
            }
            lctc.lxi_csv_to_cdf(**inputs)
        except Exception as e:
            print(
                f"\n \x1b[1;31;255m Error: \x1b[0m Could not save the cdf file. Following exception"
                f" was raised: \n \x1b[1;31;255m {e} \x1b[0m is not defined. \n Check if a valid "
                f"Science csv file is loaded. \n"
            )
            pass
    else:
        logger.error("No file loaded/ no Data in the file")


def get_lexi_files_from_ff(sftp, remote_dir, local_dir, time_threshold):
    """
    Recursively download files from the Firefly server that were modified after the given time
    threshold.

    Parameters
    ----------
    sftp : paramiko.SFTPClient
        The SFTP client object
    remote_dir : str
        The remote directory to download files from
    local_dir : str
        The local directory to save the files
    time_threshold : datetime
        The time threshold to check if the files were modified after this time

    Returns
    -------
        None
    """
    # Change to the remote directory
    sftp.chdir(remote_dir)
    # Get list of files and directories in the remote directory
    for file_attr in sftp.listdir_attr():
        file_name = file_attr.filename
        remote_file_path = Path(remote_dir) / file_name
        remote_file_path = remote_file_path.as_posix()
        local_file_path = Path(local_dir) / file_name

        # Get the modified time of the file in UTC
        file_modified_time = datetime.fromtimestamp(file_attr.st_mtime, timezone.utc)
        # if file_modified_time < time_threshold:
        # Check if the file was modified before the threshold time and that it is not a directory
        if file_modified_time < time_threshold and not file_attr.st_mode & 0o040000:
            print(
                f"Skipping {file_name} as it was modified before the threshold time\n"
            )
            # print(f"File modified time: {file_modified_time}, Threshold time: {time_threshold}")
            continue
        elif file_modified_time < time_threshold and file_attr.st_mode & 0o040000:
            # If it is a directory, recurse into it
            if file_attr.st_mode & 0o040000:  # This checks if the path is a directory
                local_file_path.mkdir(parents=True, exist_ok=True)
                get_lexi_files_from_ff(
                    sftp, str(remote_file_path), str(local_file_path), time_threshold
                )
        elif file_modified_time > time_threshold and file_attr.st_mode & 0o040000:
            # If it is a directory, recurse into it
            if file_attr.st_mode & 0o040000:  # This checks if the path is a directory
                local_file_path.mkdir(parents=True, exist_ok=True)
                get_lexi_files_from_ff(
                    sftp, str(remote_file_path), str(local_file_path), time_threshold
                )
        # If it is a file, check if it was modified in the last 'time_delta_minutes'
        elif file_modified_time > time_threshold:
            # Ensure the local directory exists
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            # Check if the file already exists locally
            if local_file_path.exists():
                local_file_size = local_file_path.stat().st_size
                remote_file_size = file_attr.st_size
                # If the file exists and sizes match, skip downloading
                if local_file_size == remote_file_size:
                    print(f"Skipping {file_name} as it already exists locally\n")
                    continue

            # Download the file
            try:
                sftp.get(str(remote_file_path), str(local_file_path))
                print(f"Downloaded {file_name} from {remote_dir} to {local_dir}\n")
            except Exception:
                logger.exception(
                    f"Error downloading {file_name} from {remote_dir} to {local_dir}"
                )
                continue


def show_blinking_message():
    """
    Display a blinking message "Downloading data, please wait" while the data is being downloaded
    """

    global thread_running

    while thread_running:
        sys.stdout.write(
            "\rDownloading data, please wait" + "." * (int(time.time()) % 4)
        )
        sys.stdout.flush()
        time.sleep(0.25)

    # Clear the blinking message after download is complete
    sys.stdout.write("\r" + " " * 30 + "\r")  # Clear the line


def download_latest_files(time_threshold=1.0):
    """
    Download the latest files from the Firefly server that were modified in the last given time. By
    default, all files from last 1 hour are downloaded. You can change the time range by changing
    the "time_delta_minutes" parameter in the function.

    The default configuration parameters are:
    hostname = "sftp.fireflyspace.com"
    port = 22  # or the port number your server uses
    username = "LEXI"
    private_key_path = "/home/cephadrius/.ssh/firefly_ssh_key"
    remote_directory = "/BGM1/1_Payload_Science/2_LEXI/"
    local_directory = "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/test/"
    time_delta_minutes = None  # Time range in minutes. If None, download all files

    Returns
    -------
        None
    """

    global thread_running

    # Configuration parameters
    hostname = "sftp.fireflyspace.com"
    port = 22  # or the port number your server uses
    username = "LEXI"
    private_key_path = "~/firefly_ssh_key_ssh"
    private_key_path = Path(private_key_path).expanduser()
    # password = "your_password"  # Only needed if not using an SSH key
    remote_directory = "/BGM1/1_Payload_Science/2_LEXI/"
    local_directory = (
        "C:\\Users\\Lexi-Admin\\Documents\\GitHub\\Lexi-BU\\lxi_gui\\data\\from_ff"
    )
    local_directory = Path(local_directory).expanduser()
    try:
        time_delta_minutes = float(time_threshold)  # Time range in minutes
        print(f"Downloading files modified in the last {time_delta_minutes} minutes\n")

    except Exception:
        time_delta_minutes = None
        print("Downloading all files\n")

    # Time calculation: files modified in the last "time_delta_minutes" minutes
    # If time_delta_minutes is None, then download all files
    if time_delta_minutes is not None:
        # Get the time in UTC
        time_threshold = datetime.now(timezone.utc) - timedelta(
            minutes=time_delta_minutes
        )
    else:
        time_threshold = datetime.min
        # Set the timezone to UTC
        time_threshold = time_threshold.replace(tzinfo=timezone.utc)

    # Start the blinking message in a separate thread
    blinking_thread = threading.Thread(target=show_blinking_message)
    blinking_thread.daemon = (
        True  # This ensures the thread will exit when the main program does
    )
    blinking_thread.start()

    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Authenticate using either password or SSH key
        if private_key_path:
            private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
            ssh.connect(hostname, port, username=username, pkey=private_key)
        else:
            ssh.connect(hostname, port, username=username)

        # Open the SFTP session
        sftp = ssh.open_sftp()

        # Download files modified in the last 37 minutes
        get_lexi_files_from_ff(sftp, remote_directory, local_directory, time_threshold)

        # Close the SFTP session
        sftp.close()
        ssh.close()

        print("\nDownload complete.")

    finally:
        thread_running = False


def add_circle(
    axs=None,
    radius=4,
    units="mcp",
    color=["r", "c"],
    fill=False,
    linewidth=2,
    zorder=10,
    fontsize=12,
):
    """
    The function adds a circle to the histogram plot.

    Parameters
    ----------
    axs : matplotlib.axes._subplots.AxesSubplot
        The axes object to which the circle is to be added.
    radius : float
        The radius of the circle in appropriate units.
    units : str
        The units of the radius. Default is "mcp".
    color : list
        The color of the circle boundary and the text. Default is ["r", "c"].
    fill : bool
        If True, the circle is filled with the color. Default is False.
    linewidth : float
        The width of the circle boundary. Default is 2.
    zorder : int
        The zorder of the circle. Default is 1.
    fontsize : int
        The fontsize of the text. Default is 12.

    Returns
    -------
    axs : matplotlib.axes._subplots.AxesSubplot
        The axes object to which the circle is added.
    """
    if axs is None:
        raise ValueError("The axes object is not defined.")
    else:
        if units == "mcp":
            radius1 = radius
            radius2 = 0.9375 * radius
        elif units == "deg":
            radius1 = radius * 9.1 / 8
            radius2 = radius * 0.9375 * 9.1 / 8
        elif units == "volt":
            # Exit the function without adding the circle
            return axs

        # Add a circle centered at (0,0) with radius 4 cm
        circle1 = plt.Circle(
            (0, 0),
            radius1,
            color=color[0],
            fill=False,
            linewidth=linewidth,
            zorder=zorder,
        )
        circle2 = plt.Circle(
            (0, 0),
            radius2,
            color=color[1],
            fill=False,
            linewidth=linewidth,
            zorder=zorder,
        )
        # Make an arrow pointing to the edge of the circle from outside the circle at 45
        # degrees from the horizontal axis and with text "4.5 cm"
        angle_1 = np.pi / 2.7
        angle_2 = np.pi / 1.5
        axs.annotate(
            "Detector Size",
            xy=(radius1 * np.cos(angle_1), radius1 * np.sin(angle_1)),
            xytext=((radius1 + 1) * np.cos(angle_1), (radius1 + 1) * np.sin(angle_1)),
            arrowprops=dict(arrowstyle="->", color=color[0], linewidth=linewidth),
            color=color[0],
            fontsize=fontsize,
        )
        # Make an arrow pointing to the edge of the circle from outside the circle at -45
        # degrees from the horizontal axis and with text "3.75 cm"
        axs.annotate(
            "Effective Area",
            xy=(radius2 * np.cos(angle_2), radius2 * np.sin(angle_2)),
            xytext=((radius2 + 4) * np.cos(angle_2), (radius2 + 1) * np.sin(angle_2)),
            arrowprops=dict(arrowstyle="->", color=color[1], linewidth=linewidth),
            color=color[1],
            fontsize=fontsize,
        )
        # Add the circles to the plot and make sure they are in the foreground
        axs.add_artist(circle1)
        axs.add_artist(circle2)
        circle1.set_zorder(zorder)
        circle2.set_zorder(zorder)

    return axs
