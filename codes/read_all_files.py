import os
import numpy as np
import pandas as pd
import datetime
import struct
import lxi_misc_codes as lmsc
import importlib
import pytz

from pathlib import Path
from typing import NamedTuple

importlib.reload(lmsc)

# Tha packet format of the science and housekeeping packets
packet_format_sci = ">II4H"
# signed lower case, unsigned upper case (b)
packet_format_hk = ">II4H"

# double precision format for time stamp from pit
packet_format_pit = ">d"


sync_lxi = b"\xfe\x6b\x28\x40"

sync_pit = b"\x54\x53"

volts_per_count = 4.5126 / 65536  # volts per increment of digitization


class hk_packet_cls(NamedTuple):
    """
    Class for the housekeeping packet.
    The code unpacks the HK packet into a named tuple. Based on the document and data structure,
    each packet is unpacked into
    - Date: time of the packet as received from the PIT
    - "timestamp",
    - "hk_id" (this tells us what "hk_value" stores inside it),
    - "hk_value",
    - "delta_event_count",
    - "delta_drop_event_count", and
    - "delta_lost_event_count".

    Based on the value of "hk_id", "hk_value" might correspond to value of following parameters:
    NOTE: "hk_id" is a number, and varies from 0 to 15.
    0: PinPuller Temperature
    1: Optics Temperature
    2: LEXI Base Temperature
    3: HV Supply Temperature
    4: Current Correspoding to the HV Supply (5.2V)
    5: Current Correspoding to the HV Supply (10V)
    6: Current Correspoding to the HV Supply (3.3V)
    7: Anode Voltage Monitor
    8: Current Correspoding to the HV Supply (28V)
    9: ADC Ground
    10: Command Count
    11: Pin Puller Armmed
    12: Unused
    13: Unused
    14: MCP HV after auto change
    15: MCP HV after manual change
    """

    Date: int
    timestamp: int
    hk_id: int
    hk_value: float
    delta_event_count: int
    delta_drop_event_count: int
    delta_lost_event_count: int

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        structure_time = struct.unpack(">d", bytes_[2:10])
        structure = struct.unpack(packet_format_hk, bytes_[12:])
        # Check if the present packet is the house-keeping packet. Only the house-keeping packets
        # are processed.
        if structure[1] & 0x80000000:
            Date = structure_time[0]
            timestamp = structure[1] & 0x3FFFFFFF  # mask for getting all timestamp bits
            hk_id = (structure[2] & 0xF000) >> 12  # Down-shift 12 bits to get the hk_id
            if hk_id == 10 or hk_id == 11:
                hk_value = structure[2] & 0xFFF
            else:
                hk_value = (
                    structure[2] & 0xFFF
                ) << 4  # Up-shift 4 bits to get the hk_value
            delta_event_count = structure[3]
            delta_drop_event_count = structure[4]
            delta_lost_event_count = structure[5]

            return cls(
                Date=Date,
                timestamp=timestamp,
                hk_id=hk_id,
                hk_value=hk_value,
                delta_event_count=delta_event_count,
                delta_drop_event_count=delta_drop_event_count,
                delta_lost_event_count=delta_lost_event_count,
            )


class hk_packet_cls_gsfc(NamedTuple):
    """
    Class for the housekeeping packet.
    The code unpacks the HK packet into a named tuple. Based on the document and data structure,
    each packet is unpacked into
    - "timestamp",
    - "hk_id" (this tells us what "hk_value" stores inside it),
    - "hk_value",
    - "delta_event_count",
    - "delta_drop_event_count", and
    - "delta_lost_event_count".

    Based on the value of "hk_id", "hk_value" might correspond to value of following parameters:
    NOTE: "hk_id" is a number, and varies from 0 to 15.
    0: PinPuller Temperature
    1: Optics Temperature
    2: LEXI Base Temperature
    3: HV Supply Temperature
    4: Current Correspoding to the HV Supply (5.2V)
    5: Current Correspoding to the HV Supply (10V)
    6: Current Correspoding to the HV Supply (3.3V)
    7: Anode Voltage Monitor
    8: Current Correspoding to the HV Supply (28V)
    9: ADC Ground
    10: Command Count
    11: Pin Puller Armmed
    12: Unused
    13: Unused
    14: MCP HV after auto change
    15: MCP HV after manual change
    """

    timestamp: int
    hk_id: int
    hk_value: float
    delta_event_count: int
    delta_drop_event_count: int
    delta_lost_event_count: int

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        structure = struct.unpack(packet_format_hk, bytes_)
        # Check if the present packet is the house-keeping packet. Only the house-keeping packets
        # are processed.
        if structure[1] & 0x80000000:
            timestamp = structure[1] & 0x3FFFFFFF  # mask for getting all timestamp bits
            hk_id = (structure[2] & 0xF000) >> 12  # Down-shift 12 bits to get the hk_id
            if hk_id == 10 or hk_id == 11:
                hk_value = structure[2] & 0xFFF
            else:
                hk_value = (
                    structure[2] & 0xFFF
                ) << 4  # Up-shift 4 bits to get the hk_value
            delta_event_count = structure[3]
            delta_drop_event_count = structure[4]
            delta_lost_event_count = structure[5]

            return cls(
                timestamp=timestamp,
                hk_id=hk_id,
                hk_value=hk_value,
                delta_event_count=delta_event_count,
                delta_drop_event_count=delta_drop_event_count,
                delta_lost_event_count=delta_lost_event_count,
            )


def read_binary_data_hk(
    in_file_name=None,
    save_file_name="../data/processed/hk/output_hk.csv",
    number_of_decimals=6,
):
    """
    Reads housekeeping packet of the binary data from a file and saves it to a csv file.

    Parameters
    ----------
    in_file_name : str
        Name of the input file. Default is None.
    save_file_name : str
        Name of the output file. Default is "output_hk.csv".
    number_of_decimals : int
        Number of decimals to save. Default is 6.

    Raises
    ------
    FileNotFoundError :
        If the input file does not exist.
    TypeError :
        If the name of the input file or input directory is not a string. Or if the number of
        decimals is not an integer.
    Returns
    -------
        df : pandas.DataFrame
            DataFrame of the housekeeping packet.
        save_file_name : str
            Name of the output file.

    Raises
    ------
    FileNotFoundError :
        If the input file does not exist or isn't a specified
    """
    if in_file_name is None:
        raise FileNotFoundError("The input file name must be specified.")

    # Check if the file exists, if does not exist raise an error
    if not Path(in_file_name).is_file():
        raise FileNotFoundError("The file " + in_file_name + " does not exist.")
    # Check if the file name and folder name are strings, if not then raise an error
    if not isinstance(in_file_name, str):
        raise TypeError("The file name must be a string.")

    # Check the number of decimals to save
    if not isinstance(number_of_decimals, int):
        raise TypeError("The number of decimals to save must be an integer.")

    input_file_name = in_file_name

    print(f"Reading the file \033[96m {in_file_name}\033[0m")

    # Get the creation date of the file in UTC and local time
    creation_date_utc = datetime.datetime.fromtimestamp(
        os.path.getctime(input_file_name), tz=datetime.timezone.utc
    )
    creation_date_local = datetime.datetime.fromtimestamp(
        os.path.getctime(input_file_name)
    )

    with open(input_file_name, "rb") as file:
        raw = file.read()

    index = 0
    packets = []

    if "payload" in in_file_name:
        while index < len(raw) - 28:
            if (
                raw[index : index + 2] == sync_pit
                and raw[index + 12 : index + 16] == sync_lxi
            ):
                # print(f"{index} d ==> {raw[index:index + 28].hex()}\n")
                packets.append(hk_packet_cls.from_bytes(raw[index : index + 28]))
                index += 28
                continue
            elif (
                raw[index : index + 2] == sync_pit
                and raw[index + 12 : index + 16] != sync_lxi
            ):
                # Ignore the last packet
                if index >= len(raw) - 28 - 16:
                    # NOTE: This is a temporary fix. The last packet is ignored because the last
                    # packet often isn't complete. Need to find a better solution. Check the function
                    # read_binary_data_sci for the same.
                    index += 28
                    continue
                # Check if sync_lxi is present in the next 16 bytes
                if sync_lxi in raw[index + 12 : index + 28] and index + 28 < len(raw):
                    # Find the index of sync_lxi
                    index_sync = (
                        index + 12 + raw[index + 12 : index + 28].index(sync_lxi)
                    )
                    # Reorder the packet
                    new_packet = (
                        raw[index : index + 12]
                        + raw[index_sync : index + 28]
                        + raw[index + 12 + 28 : index_sync + 28]
                    )
                    # Check if the packet length is 28
                    if len(new_packet) != 28:
                        # Print the packet length
                        print(
                            f"The packet length is {len(new_packet)}, index = {index} and length of raw is {len(raw)}"
                        )
                        print(f"{index} 1 ==> {new_packet.hex()}\n")
                        # If the index + 28 is greater than the length of the raw data, then break
                        if index + 28 > len(raw):
                            break
                    # print(f"{index} 1 ==> {new_packet.hex()}\n")
                    packets.append(hk_packet_cls.from_bytes(new_packet))
                    index += 28
                    continue
                # Check if raw[index - 3:index] + raw[index+12:index+13] == sync_lxi
                elif raw[index - 3 : index] + raw[index + 12 : index + 13] == sync_lxi:
                    # Reorder the packet
                    new_packet = (
                        raw[index : index + 12]
                        + raw[index - 3 : index]
                        + raw[index + 12 : index + 25]
                    )
                    # print(f"{index} 2 ==> {new_packet.hex()}\n")
                    packets.append(hk_packet_cls.from_bytes(new_packet))
                    index += 28
                    continue
                # Check if raw[index - 2:index] + raw[index+12:index+14] == sync_lxi
                elif raw[index - 2 : index] + raw[index + 12 : index + 14] == sync_lxi:
                    # Reorder the packet
                    new_packet = (
                        raw[index : index + 12]
                        + raw[index - 2 : index]
                        + raw[index + 13 : index + 26]
                    )
                    # print(f"{index} 3 ==> {new_packet.hex()}\n")
                    packets.append(hk_packet_cls.from_bytes(new_packet))
                    index += 28
                    continue
                # Check if raw[index - 1:index] + raw[index+12:index+15] == sync_lxi
                elif raw[index - 1 : index] + raw[index + 12 : index + 15] == sync_lxi:
                    # Reorder the packet
                    new_packet = (
                        raw[index : index + 12]
                        + raw[index - 1 : index]
                        + raw[index + 14 : index + 27]
                    )
                    # print(f"{index} 4 ==> {new_packet.hex()}\n")
                    packets.append(hk_packet_cls.from_bytes(new_packet))
                    index += 28
                    continue
                index += 28
                continue
            index += 28
    else:
        # Print in green color that the gsfc code is running
        print("\033[92mRunning the GSFC code for Housekeeping.\033[0m")
        while index < len(raw) - 16:
            if raw[index : index + 4] == sync_lxi:
                packets.append(hk_packet_cls_gsfc.from_bytes(raw[index : index + 16]))
                index += 16
                continue
            index += 1
    # Get only those packets that have the HK data
    hk_idx = []
    for idx, hk_packet in enumerate(packets):
        if hk_packet is not None:
            hk_idx.append(idx)

    Date = np.full(len(hk_idx), np.nan)
    TimeStamp = np.full(len(hk_idx), np.nan)
    HK_id = np.full(len(hk_idx), np.nan)
    PinPullerTemp = np.full(len(hk_idx), np.nan)
    OpticsTemp = np.full(len(hk_idx), np.nan)
    LEXIbaseTemp = np.full(len(hk_idx), np.nan)
    HVsupplyTemp = np.full(len(hk_idx), np.nan)
    V_Imon_5_2 = np.full(len(hk_idx), np.nan)
    V_Imon_10 = np.full(len(hk_idx), np.nan)
    V_Imon_3_3 = np.full(len(hk_idx), np.nan)
    AnodeVoltMon = np.full(len(hk_idx), np.nan)
    V_Imon_28 = np.full(len(hk_idx), np.nan)
    ADC_Ground = np.full(len(hk_idx), np.nan)
    Cmd_count = np.full(len(hk_idx), np.nan)
    Pinpuller_Armed = np.full(len(hk_idx), np.nan)
    Unused1 = np.full(len(hk_idx), np.nan)
    Unused2 = np.full(len(hk_idx), np.nan)
    HVmcpAuto = np.full(len(hk_idx), np.nan)
    HVmcpMan = np.full(len(hk_idx), np.nan)
    DeltaEvntCount = np.full(len(hk_idx), np.nan)
    DeltaDroppedCount = np.full(len(hk_idx), np.nan)
    DeltaLostEvntCount = np.full(len(hk_idx), np.nan)

    all_data_dict = {
        "Date": Date,
        "TimeStamp": TimeStamp,
        "HK_id": HK_id,
        "0": PinPullerTemp,
        "1": OpticsTemp,
        "2": LEXIbaseTemp,
        "3": HVsupplyTemp,
        "4": V_Imon_5_2,
        "5": V_Imon_10,
        "6": V_Imon_3_3,
        "7": AnodeVoltMon,
        "8": V_Imon_28,
        "9": ADC_Ground,
        "10": Cmd_count,
        "11": Pinpuller_Armed,
        "12": Unused1,
        "13": Unused2,
        "14": HVmcpAuto,
        "15": HVmcpMan,
        "DeltaEvntCount": DeltaEvntCount,
        "DeltaDroppedCount": DeltaDroppedCount,
        "DeltaLostEvntCount": DeltaLostEvntCount,
    }

    selected_keys = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
    ]

    # Check if "unit_1" or "unit1" is in the file name, if so then the data is from the unit 1
    if "unit_1" in input_file_name or "unit1" in input_file_name:
        lxi_unit = 1
    elif "unit_2" in input_file_name or "unit2" in input_file_name:
        lxi_unit = 2
    else:
        lxi_unit = 1

    for ii, idx in enumerate(hk_idx):
        hk_packet = packets[idx]
        # Convert to seconds from milliseconds for the timestamp
        if "payload" in in_file_name:
            all_data_dict["Date"][ii] = hk_packet.Date
        else:
            default_time = datetime.datetime(
                2024, 1, 1, 0, 0, 0, tzinfo=pytz.timezone("UTC")
            )
            new_time = default_time + datetime.timedelta(
                milliseconds=hk_packet.timestamp
            )
            all_data_dict["Date"][ii] = new_time.timestamp()
        all_data_dict["TimeStamp"][ii] = hk_packet.timestamp / 1e3
        all_data_dict["HK_id"][ii] = hk_packet.hk_id
        key = str(hk_packet.hk_id)
        if key in selected_keys:
            all_data_dict[key][ii] = lmsc.hk_value_comp(
                ii=ii,
                vpc=volts_per_count,
                hk_value=hk_packet.hk_value,
                hk_id=hk_packet.hk_id,
                lxi_unit=lxi_unit,
            )

        all_data_dict["DeltaEvntCount"][ii] = hk_packet.delta_event_count
        all_data_dict["DeltaDroppedCount"][ii] = hk_packet.delta_drop_event_count
        all_data_dict["DeltaLostEvntCount"][ii] = hk_packet.delta_lost_event_count

    # Create a dataframe with the data
    df_key_list = [
        "Date",
        "TimeStamp",
        "HK_id",
        "PinPullerTemp",
        "OpticsTemp",
        "LEXIbaseTemp",
        "HVsupplyTemp",
        "+5.2V_Imon",
        "+10V_Imon",
        "+3.3V_Imon",
        "AnodeVoltMon",
        "+28V_Imon",
        "ADC_Ground",
        "Cmd_count",
        "Pinpuller_Armed",
        "Unused1",
        "Unused2",
        "HVmcpAuto",
        "HVmcpMan",
        "DeltaEvntCount",
        "DeltaDroppedCount",
        "DeltaLostEvntCount",
    ]

    Date_datetime = [
        datetime.datetime.utcfromtimestamp(x) for x in all_data_dict["Date"]
    ]

    df = pd.DataFrame(columns=df_key_list)
    for ii, key in enumerate(df_key_list):
        df[key] = all_data_dict[list(all_data_dict.keys())[ii]]

    # For the dataframe, replace the nans with the value from the previous index.
    # This is to make sure that the file isn't inundated with nans.
    for key in df.keys():
        for ii in range(1, len(df[key])):
            if np.isnan(df[key][ii]):
                df[key][ii] = df[key][ii - 1]

    # Set the date column to the Date_datetime
    df["Date"] = Date_datetime

    # Get the time difference between the first and last timestamp
    try:
        time_diff = df["Date"].iloc[:] - df["Date"].iloc[-1]
    except Exception:
        # Set time difference to 0 seconds
        time_diff = datetime.timedelta(seconds=0)

    try:
        # For each time difference, get the total number of seconds as an array
        time_diff_seconds = time_diff.dt.total_seconds().values
    except Exception:
        # Set time difference to 0 seconds
        time_diff_seconds = 0
    # Add utc_time and local_time column to the dataframe as NaNs
    df["utc_time"] = np.nan
    df["local_time"] = np.nan
    # For each row, set the utc_time and local_time as sum of created_date_utc and time_diff_seconds
    df["utc_time"] = creation_date_utc + pd.to_timedelta(time_diff_seconds, unit="s")
    df["local_time"] = creation_date_local + pd.to_timedelta(
        time_diff_seconds, unit="s"
    )

    # Set Date as the index without replacing the column
    df.set_index("Date", inplace=True, drop=False)
    # Split the file name in a folder and a file name
    # Format filenames and folder names for the different operating systems
    if os.name == "posix":
        output_folder_name = (
            os.path.dirname(os.path.normpath(in_file_name)) + "/processed_data/hk"
        )
        output_file_name = (
            os.path.basename(os.path.normpath(in_file_name)).split(".")[0]
            + "_hk_output.csv"
        )
        save_file_name = output_folder_name + "/" + output_file_name
    elif os.name == "nt":
        output_folder_name = (
            os.path.dirname(os.path.normpath(in_file_name)) + "\\processed_data\\hk"
        )
        output_file_name = (
            os.path.basename(os.path.normpath(in_file_name)).split(".")[0]
            + "_hk_output.csv"
        )
        save_file_name = output_folder_name + "\\" + output_file_name
    elif os.name == "darwin":
        output_folder_name = (
            os.path.dirname(os.path.normpath(in_file_name)) + "/processed_data/hk"
        )
        output_file_name = (
            os.path.basename(os.path.normpath(in_file_name)).split(".")[0]
            + "_hk_output.csv"
        )
        save_file_name = output_folder_name + "/" + output_file_name
    else:
        raise OSError("Operating system not supported.")

    # Check if the save folder exists, if not then create it
    if not Path(output_folder_name).exists():
        Path(output_folder_name).mkdir(parents=True, exist_ok=True)

    # Save the dataframe to a csv file
    df.to_csv(save_file_name, index=False)

    return df, save_file_name


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
    df = pd.read_csv(file_val, index_col=False)

    # Check all the keys and find out which one has the word "time" in it
    for key in df.keys():
        if "time" in key.lower():
            time_col = key
            break
    # Rename the time column to TimeStamp
    df.rename(columns={time_col: "TimeStamp"}, inplace=True)

    # Convert the Date column from string to datetime in utc
    try:
        df["Date"] = pd.to_datetime(df["Date"], utc=True)
    except Exception:
        # Convert timestamp to datetime and set it to Date
        df["Date"] = pd.to_datetime(df["TimeStamp"], unit="s", utc=True)

    # Set the index to the time column
    df.set_index("Date", inplace=True)
    # Sort the dataframe by timestamp
    df = df.sort_index()

    if t_start is None:
        t_start = df.index.min()
    if t_end is None:
        t_end = df.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_hk = df.loc[t_start:t_end].copy()

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

    # If only one of t_start and t_end is None, raise an error
    if (t_start is None and t_end is not None) or (
        t_start is not None and t_end is None
    ):
        raise ValueError(
            "when multiple_files is True, both t_start and t_end must either be"
            f"None or a valid time value. The vlaues provided are t_start ="
            f"{t_start} and t_end = {t_end}."
        )
    # If both t_start and t_end are None, raise a warning stating that the times are set to none
    if t_start is None and t_end is None:
        print(
            "\n \x1b[1;31;255m WARNING: Both the start and end time values provided were None"
            "setting both of them to None \x1b[0m"
        )
        t_start = None
        t_end = None

    if t_start is not None and t_end is not None:
        # Convert t_start and t_end from string to datetime in UTC timezone
        t_start = pd.to_datetime(t_start, utc=True)
        t_end = pd.to_datetime(t_end, utc=True)

        try:
            # Convert t_start and t_end from string to unix time in seconds in UTC timezone
            t_start_unix = t_start.timestamp()
            t_end_unix = t_end.timestamp()
        except Exception:
            t_start_unix = None
            t_end_unix = None

    # Define a list in which the dataframes will be stored
    df_hk_list = []
    file_name_hk_list = []

    # Make sure that file_val is a directory
    if not os.path.isdir(file_val):
        raise ValueError("file_val should be a directory.")

    # Get the names of all the files in the directory with*.dat or *.txt extension
    file_list = sorted(
        [
            os.path.join(file_val, f)
            for f in os.listdir(file_val)
            if f.endswith((".dat", ".txt"))
        ]
    )

    # If file list is empty, raise an error and exit
    if len(file_list) == 0:
        raise ValueError("No files found in the directory.")
    else:
        print(
            f"Found total \x1b[1;32;255m {len(file_list)} \x1b[0m files in the directory."
        )

    """
    if t_start_unix is not None and t_end_unix is not None:
        # In file_list, select only those files which are within the time range
        file_list = [
            file_name
            for file_name in file_list
            if t_start_unix
            <= float(os.path.basename(file_name).split("_")[2])
            <= t_end_unix
        ]
        print(
            f"Found \x1b[1;32;255m {len(file_list)} \x1b[0m files in the time range "
            f"\x1b[1;32;255m {t_start.strftime('%Y-%m-%d %H:%M:%S')} \x1b[0m to "
            f"\x1b[1;32;255m {t_end.strftime('%Y-%m-%d %H:%M:%S')}\x1b[0m"
        )
    """
    # Loop through all the files
    for file_name in file_list:
        # Print in cyan color that file number is being read from the directory conatining total
        # number of files
        print(
            f"\n Reading file \x1b[1;36;255m {file_list.index(file_name) + 1} \x1b[0m of "
            f"total \x1b[1;36;255m {len(file_list)} \x1b[0m files."
        )
        # Read the housekeeping data
        df_hk, file_name_hk = read_binary_data_hk(
            in_file_name=file_name, save_file_name=None, number_of_decimals=6
        )

        # Append the dataframes to the list
        df_hk_list.append(df_hk)
        file_name_hk_list.append(file_name_hk)

    # Concatenate all the dataframes
    df_hk = pd.concat(df_hk_list)

    # Set file_names_hk and file_names_sci to dates of first and last files
    save_dir = os.path.dirname(file_val)
    # If save_dir does not exist, create it
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Get the file name based on the os path
    file_name_hk = (
        save_dir
        + "/processed_data/hk/"
        + file_name_hk_list[0].split("/")[-1].split(".")[0].split("_")[0]
        + "_"
        + file_name_hk_list[0].split("/")[-1].split(".")[0].split("_")[1]
        + "_"
        + file_name_hk_list[0].split("/")[-1].split(".")[0].split("_")[2]
        + "_"
        + file_name_hk_list[0].split("/")[-1].split(".")[0].split("_")[3]
        + "_"
        + file_name_hk_list[-1].split("/")[-1].split(".")[0].split("_")[-4]
        + "_"
        + file_name_hk_list[-1].split("/")[-1].split(".")[0].split("_")[-3]
        + "_hk_output.csv"
    )

    print(f"The Housekeeping File name =\x1b[1;32;255m {file_name_hk} \x1b[0m, \n")
    # Save the dataframe to a csv file
    df_hk.to_csv(file_name_hk, index=False)

    print(
        f"Saved the dataframes to csv files. \n"
        f"The Housekeeping File name =\x1b[1;32;255m {file_name_hk} \x1b[0m,\n"
    )
    # Replace index with timestamp
    df_hk.set_index("Date", inplace=True)

    # Sort the dataframe by timestamp
    df_hk = df_hk.sort_index()

    df_hk, df_slice_hk = read_csv_hk(
        file_val=file_name_hk, t_start=t_start, t_end=t_end
    )

    # Select dataframe from timestamp t_start to t_end
    df_slice_hk = df_hk.loc[t_start:t_end].copy()

    # For both the sliced and entire dataframes, compute the x and y-coordinates and the
    # shift in the voltages

    return df_slice_hk, file_name_hk, df_hk


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


if __name__ == "__main__":
    directory_path = "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/hk_testings/"
    folder_list = list_folders_in_directory(directory_path)

    for folder in folder_list[4:]:
        print(
            f"\n \x1b[1;31;255m Reading the binary file from the folder {folder} \x1b[0m \n"
        )
        # If the folder anme has "processed_data" in it, then skip it
        if "processed" in folder:
            print(f"Skipping the folder {folder}")
            continue
        try:
            input_dict = {
                "file_val": folder + "/",
                "t_start": "2020-04-14 00:00:00",
                "t_end": "2026-04-14 23:59:59",
            }
            # Read the binary file
            df_slice_hk, file_name_hk, df_hk = read_binary_file(**input_dict)
            # Write that the files from the folders were read in bold red color
            print(
                f"\n \x1b[1;31;255m The files from the folder {folder} were read. \x1b[0m"
            )
        except Exception:
            print(f"Failed to read the binary file from {folder}")
            continue
