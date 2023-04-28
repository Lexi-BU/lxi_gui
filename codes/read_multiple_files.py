import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt

# Activate the latex text rendering
plt.rc('text', usetex=True)
# Set the font for the latex text
plt.rc('font', family='serif')

# If any figures are open, close them
plt.close("all")


def read_multiple_csv(csv_folder=None, csv_file=None):
    """
    Read multiple CSV files from a folder and return a single dataframe.

    Parameters
    ----------
    csv_folder : str
        Path to the folder containing the CSV files.
    csv_file : str
        Path to the CSV file.

    Returns
    -------
    df : pandas.DataFrame
        Dataframe containing data from all the CSV files.
    """
    if csv_folder is not None:
        if csv_file is not None:
            csv_file_list = [csv_folder + "/" + csv_file]
        else:
            # Find all the CSV files in the folder
            csv_file_list = np.sort(glob.glob(csv_folder + "*.csv"))
    elif csv_folder is None and csv_file is not None:
        csv_file_list = [csv_file]

    # Read the CSV files
    df_list = []
    for csv_file in csv_file_list:
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        df_list.append(df)

    # Concatenate the dataframes
    df = pd.concat(df_list, axis=0)

    return df


# Define the path to the folder containing the CSV files
#csv_folder = "/home/vetinari/Desktop/git/Lexi-Bu/lxi_gui/data/PIT/processed_data/hk/"
csv_folder = "/home/vetinari/Desktop/git/Lexi-Bu/lxi_gui/data/PIT/20230414/processed_data/hk/"
# Read the CSV files
df = read_multiple_csv(csv_folder=csv_folder)

time_in_seconds = df.index.astype(np.int64) // 10 ** 9
time_elapsed = (time_in_seconds - time_in_seconds[0]) / 60

# Add a column for the time elapsed
df["TimeElapsed"] = time_elapsed

# Save the dataframe to a CSV file
df.to_csv("../data/hk_data_20230414.csv")

# Define the keys to plot
plot_key_list = ["PinPullerTemp", "OpticsTemp", "LEXIbaseTemp", "HVsupplyTemp", "+5.2V_Imon",
                 "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon", "ADC_Ground", "Cmd_count",
                 "Pinpuller_Armed", "HVmcpAuto", "HVmcpMan", "DeltaEvntCount", "DeltaDroppedCount",
                 "DeltaLostEvntCount", "TimeStamp"]

# Make a 6 x 3 plot of the data in the dataframe for the keys in plot_key_list
fig, ax = plt.subplots(6, 3, figsize=(15, 15))

# Adjust the spacing between the subplots
plt.subplots_adjust(wspace=0.2, hspace=0.2)


for xx, key in enumerate(plot_key_list):

    ax[xx // 3, xx % 3].scatter(time_elapsed, df[key], s=1, marker=".", color="k", alpha=0.8)
    # ax[xx // 3, xx % 3].set_title(key)

    # Show x-label at 5 minute intervals
    ax[xx // 3, xx % 3].set_xticks(np.arange(0, time_elapsed[-1], 5))
    ax[xx // 3, xx % 3].set_xlabel("Time elapsed (minutes)")
    ax[xx // 3, xx % 3].set_ylabel(key)
    ax[xx // 3, xx % 3].grid(True)

plt.tight_layout()
plt.savefig("../figures/hk_data_20230414.pdf", bbox_inches="tight", pad_inches=0.1, format="pdf",
            dpi=300)
