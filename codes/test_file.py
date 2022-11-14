import csv
import datetime
import importlib
import struct
from pathlib import Path
from tkinter import filedialog
from typing import NamedTuple

import numpy as np
import pandas as pd

import global_variables
import lxi_misc_codes as lmsc

importlib.reload(lmsc)

# Tha packet format of the science and housekeeping packets
packet_format_sci = ">II4H"
# signed lower case, unsigned upper case (b)
packet_format_hk = ">II4H"

sync_lxi = b'\xfe\x6b\x28\x40'
sync_pit = b'\x54\x53'

volts_per_count = 4.5126 / 65536  # volts per increment of digitization


class pit_packet(NamedTuple):
    """
    """
    pit_time : int

    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Unpacks the science packet from the bytes.
        :param data: bytes
        :return: sci_packet
        """
        struct_data = struct.unpack(">d", data)
        return cls(
            pit_time = struct_data[0],
        )

class hk_packet_cls(NamedTuple):
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
            timestamp = structure[1] & 0x3fffffff  # mask for getting all timestamp bits
            hk_id = (structure[2] & 0xf000) >> 12  # Down-shift 12 bits to get the hk_id
            if hk_id == 10 or hk_id == 11:
                hk_value = structure[2] & 0xfff
            else:
                hk_value = (structure[2] & 0xfff) << 4  # Up-shift 4 bits to get the hk_value
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
    number_of_decimals=6
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
        raise FileNotFoundError(
            "The input file name must be specified."
        )

    # Check if the file exists, if does not exist raise an error
    if not Path(in_file_name).is_file():
        raise FileNotFoundError(
            "The file " + in_file_name + " does not exist."
        )
    # Check if the file name and folder name are strings, if not then raise an error
    if not isinstance(in_file_name, str):
        raise TypeError(
            "The file name must be a string."
        )

    # Check the number of decimals to save
    if not isinstance(number_of_decimals, int):
        raise TypeError(
            "The number of decimals to save must be an integer."
        )

    input_file_name = in_file_name

    with open(input_file_name, 'rb') as file:
        raw = file.read()

    index = 0
    pit_time_list = []
    packets = []

    while index < len(raw) - 28:
        if raw[index:index + 2] == sync_pit and raw[index + 12:index + 16] == sync_lxi:
            pit_time_list.append(pit_packet.from_bytes(raw[index + 2:index + 10]))
            packets.append(hk_packet_cls.from_bytes(raw[index + 12:index + 28]))
            index += 28
            continue

        index += 1


    # For each element in pit_timer_list, convert it from uniox time to datetime
    pit_time_list = [datetime.datetime.utcfromtimestamp(x.pit_time) for x in pit_time_list]

    # Get only those packets that have the HK data
    hk_idx = []
    for idx, hk_packet in enumerate(packets):
        if hk_packet is not None:
            hk_idx.append(idx)

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

    all_data_dict = {"TimeStamp": TimeStamp, "HK_id": HK_id,
                     "0": PinPullerTemp, "1": OpticsTemp, "2": LEXIbaseTemp, "3": HVsupplyTemp,
                     "4": V_Imon_5_2, "5": V_Imon_10, "6": V_Imon_3_3, "7": AnodeVoltMon,
                     "8": V_Imon_28, "9": ADC_Ground, "10": Cmd_count, "11": Pinpuller_Armed,
                     "12": Unused1, "13": Unused2, "14": HVmcpAuto, "15": HVmcpMan,
                     "DeltaEvntCount": DeltaEvntCount, "DeltaDroppedCount": DeltaDroppedCount,
                     "DeltaLostEvntCount": DeltaLostEvntCount}

    selected_keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14",
                     "15"]

    # Check if "unit_1" or "unit1" is in the file name, if so then the data is from the unit 1
    if "unit_1" in input_file_name or "unit1" in input_file_name:
        lxi_unit = 1
    elif "unit_2" in input_file_name or "unit2" in input_file_name:
        lxi_unit = 2
    else:
        # Print warning that unit is defaulted to 1
        print(
            "\n FileName Warning: \033[91m \nThe unit is defaulted to 1 because the name of the "
            "file does not contain \"unit_1\" or \"unit1\" or \"unit_2\" or \"unit2\". \033[0m \n"
        )
        lxi_unit = 1

    for ii, idx in enumerate(hk_idx):
        hk_packet = packets[idx]
        # Convert to seconds from milliseconds for the timestamp
        all_data_dict["TimeStamp"][ii] = hk_packet.timestamp / 1e3
        all_data_dict["HK_id"][ii] = hk_packet.hk_id
        key = str(hk_packet.hk_id)
        if key in selected_keys:
            all_data_dict[key][ii] = lmsc.hk_value_comp(ii=ii,
                                                        vpc=volts_per_count,
                                                        hk_value=hk_packet.hk_value,
                                                        hk_id=hk_packet.hk_id,
                                                        lxi_unit=lxi_unit
                                                        )

        all_data_dict["DeltaEvntCount"][ii] = hk_packet.delta_event_count
        all_data_dict["DeltaDroppedCount"][ii] = hk_packet.delta_drop_event_count
        all_data_dict["DeltaLostEvntCount"][ii] = hk_packet.delta_lost_event_count

    # Create a dataframe with the data
    df_key_list = ["TimeStamp", "HK_id", "PinPullerTemp", "OpticsTemp", "LEXIbaseTemp",
                   "HVsupplyTemp", "+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon",
                   "+28V_Imon", "ADC_Ground", "Cmd_count", "Pinpuller_Armed", "Unused1", "Unused2",
                   "HVmcpAuto", "HVmcpMan", "DeltaEvntCount", "DeltaDroppedCount",
                   "DeltaLostEvntCount"]

    df = pd.DataFrame(columns=df_key_list)
    for ii, key in enumerate(df_key_list):
        df[key] = all_data_dict[list(all_data_dict.keys())[ii]]

    # For the dataframe, replace the nans with the value from the previous index.
    # This is to make sure that the file isn't inundated with nans.
    for key in df.keys():
        for ii in range(1, len(df[key])):
            if np.isnan(df[key][ii]):
                df[key][ii] = df[key][ii - 1]

    # Set the index to the TimeStamp
    df.set_index("TimeStamp", inplace=False)

    # Split the file name in a folder and a file name
    output_file_name = in_file_name.split("/")[-1].split(".")[0] + "_hk_output.csv"
    output_folder_name = "/".join(in_file_name.split("/")[:-2]) + "/processed_data/hk"

    save_file_name = output_folder_name + "/" + output_file_name

    # Check if the save folder exists, if not then create it
    if not Path(output_folder_name).exists():
        Path(output_folder_name).mkdir(parents=True, exist_ok=True)

    # Save the dataframe to a csv file
    df.to_csv(save_file_name, index=True)

    return df, save_file_name


fn = "../data/raw_data/20221114/payload_lexi_1706244043_19540.dat"
df, save_file_name = read_binary_data_hk(in_file_name=fn)

print(df.pit_time.describe())