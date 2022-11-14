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

class sci_packet(NamedTuple):
    """
    Class for the science packet.
    The code unpacks the science packet into a named tuple. Based on the packet format, each packet
    is unpacked into following parameters:
    - pit_time: time of the packet as received from the PIT
    - timestamp: int (32 bit)
    - IsCommanded: bool (1 bit)
    - voltage channel1: float (16 bit)
    - voltage channel2: float (16 bit)
    - voltage channel3: float (16 bit)
    - voltage channel4: float (16 bit)

    TimeStamp is the time stamp of the packet in seconds.
    IsCommand tells you if the packet was commanded.
    Voltages 1 to 4 are the voltages of corresponding different channels.
    """
    pit_time: float
    is_commanded: bool
    timestamp: int
    channel1: float
    channel2: float
    channel3: float
    channel4: float

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        structure_time = struct.unpack(">d", bytes_[2:10])
        structure = struct.unpack(packet_format_sci, bytes_[12:])
        return cls(
            pit_time=structure_time[0],
            is_commanded=bool(structure[1] & 0x40000000),  # mask to test for commanded event type
            timestamp=structure[1] & 0x3fffffff,           # mask for getting all timestamp bits
            channel1=structure[2] * volts_per_count,
            channel2=structure[3] * volts_per_count,
            channel3=structure[4] * volts_per_count,
            channel4=structure[5] * volts_per_count,
        )


def read_binary_data_sci(
    in_file_name=None,
    save_file_name="../data/processed/sci/output_sci.csv",
    number_of_decimals=6
):
    """
    Reads science packet of the binary data from a file and saves it to a csv file.

    Parameters
    ----------
    in_file_name : str
        Name of the input file. Default is None.
    save_file_name : str
        Name of the output file. Default is "output_sci.csv".
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
            DataFrame of the science packet.
        save_file_name : str
            Name of the output file.
    """
    if in_file_name is None:
        in_file_name = "../data/raw_data/2022_03_03_1030_LEXI_raw_2100_newMCP_copper.txt"

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
    packets = []

    while index < len(raw) - 28:
        if raw[index:index + 2] == sync_pit and raw[index + 12:index + 16] == sync_lxi:
            packets.append(sci_packet.from_bytes(raw[index:index + 28]))
            index += 28
            continue

        index += 1

    # For each element in pit_timer_list, convert it from uniox time to datetime
    # pit_time_list = [datetime.datetime.utcfromtimestamp(x.pit_time) for x in pit_time_list]


    # Split the file name in a folder and a file name
    output_file_name = in_file_name.split("/")[-1].split(".")[0] + "_sci_output.csv"
    output_folder_name = "/".join(in_file_name.split("/")[:-2]) + "/processed_data/sci"

    save_file_name = output_folder_name + "/" + output_file_name

    # Check if the save folder exists, if not then create it
    if not Path(output_folder_name).exists():
        Path(output_folder_name).mkdir(parents=True, exist_ok=True)

    with open(save_file_name, 'w', newline='') as file:
        dict_writer = csv.DictWriter(
            file,
            fieldnames=(
                'pit_time',
                'TimeStamp',
                'IsCommanded',
                'Channel1',
                'Channel2',
                'Channel3',
                'Channel4'
            ),
        )
        dict_writer.writeheader()
        dict_writer.writerows(
            {
                'pit_time': datetime.datetime.utcfromtimestamp(sci_packet.pit_time),
                'TimeStamp': sci_packet.timestamp / 1e3,
                'IsCommanded': sci_packet.is_commanded,
                'Channel1': np.round(sci_packet.channel1, decimals=number_of_decimals),
                'Channel2': np.round(sci_packet.channel2, decimals=number_of_decimals),
                'Channel3': np.round(sci_packet.channel3, decimals=number_of_decimals),
                'Channel4': np.round(sci_packet.channel4, decimals=number_of_decimals)
            }
            for sci_packet in packets
        )

    # Read the saved file data in a dataframe
    df = pd.read_csv(save_file_name)

    # Save the dataframe to a csv file and set index to time stamp
    df.to_csv(save_file_name, index=False)

    return df, save_file_name


fn = "../data/raw_data/20221114/payload_lexi_1706244043_19540.dat"
df, save_file_name = read_binary_data_sci(in_file_name=fn)

print(df.pit_time.describe())