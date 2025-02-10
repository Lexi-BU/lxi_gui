import pandas as pd
import glob
import numpy as np
from pathlib import Path


def prepare_thruster_data():

    print("Preparing thruster data...\n")
    # Get the thruster data
    thruster_data_folder = "../data/from_LEXI/thruster_data/from_grafana/"
    # Expand the folder path
    thruster_data_folder = Path(thruster_data_folder).expanduser()
    # Get all the CSV files in the folder
    thruster_data_files = sorted(glob.glob(str(thruster_data_folder) + "/*.csv"))

    print(f"A total of {len(thruster_data_files)} files were found in the folder: {thruster_data_folder}\n")

    # Read the data from the CSV files
    df_thruster = pd.concat((pd.read_csv(file) for file in thruster_data_files), ignore_index=True)

    # Rename the "Time" column to "Date" and set it as the index of the DataFrame
    df_thruster.rename(columns={"Time": "Date"}, inplace=True)
    df_thruster["Date"] = pd.to_datetime(df_thruster["Date"])
    # Set the timezones to UTC
    df_thruster["Date"] = df_thruster["Date"].dt.tz_localize("UTC")
    df_thruster.set_index("Date", inplace=True)

    # Mapping ACS Thrusters to Telemetry:

    # THP9_CYCLECOUNT = ACS 1 (-X)
    # THP10_CYCLECOUNT = ACS 2 (+Y)
    # THP11_CYCLECOUNT = ACS 3 (+X) (LEXI facing)
    # THP12_CYCLECOUNT = ACS 4 (-X)
    # THP13_CYCLECOUNT = ACS 5 (-Z)
    # THP14_CYCLECOUNT = ACS 6 (+X)
    # THP15_CYCLECOUNT = ACS 7 (-X)
    # THP16_CYCLECOUNT = ACS 8 (-Y)
    # THP17_CYCLECOUNT = ACS 9 (+X)
    # THP18_CYCLECOUNT = ACS 10 (-X)
    # THP19_CYCLECOUNT = ACS 11 (+Z) (LEXI facing)
    # THP20_CYCLECOUNT = ACS 12 (+X)

    # For each column in the DataFrame, replace the column name with the ACS thruster name
    # and add the column to the DataFrame
    for column_name in df_thruster.columns:
        if "THP9" in column_name:
            df_thruster["acs_1"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP10" in column_name:
            df_thruster["acs_2"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP11" in column_name:
            df_thruster["acs_3"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP12" in column_name:
            df_thruster["acs_4"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP13" in column_name:
            df_thruster["acs_5"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP14" in column_name:
            df_thruster["acs_6"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP15" in column_name:
            df_thruster["acs_7"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP16" in column_name:
            df_thruster["acs_8"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP17" in column_name:
            df_thruster["acs_9"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP18" in column_name:
            df_thruster["acs_10"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP19" in column_name:
            df_thruster["acs_11"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)
        elif "THP20" in column_name:
            df_thruster["acs_12"] = df_thruster[column_name]
            # Drop the column
            df_thruster.drop(columns=column_name, inplace=True)

    # Add the values from THP11 and THP20 to get the "lexi_thrust" column
    df_thruster["lexi_thrust"] = df_thruster["acs_3"] + df_thruster["acs_12"]

    return df_thruster
