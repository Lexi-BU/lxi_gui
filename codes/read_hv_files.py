from spacepy.pycdf import CDF as cdf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

def read_hv_files(hv_file=None, hv_folder=None, file_type=None, start_time=None, end_time=None):

    df_list = []
    if file_type == "csv":
        if hv_file is not None:
            hv_file_list = [hv_folder + "/" + hv_file]
        else:
            hv_file_list = np.sort(glob.glob(hv_folder + "*.csv"))
        for hv_file in hv_file_list:
            df = pd.read_csv(hv_file, index_col=0, parse_dates=True)
            df_list.append(df)
        # Set the Date column to index and drop the column
        df = pd.concat(df_list, axis=0)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        # Offset the index, so that 2024-05-23 21:40:00 becomes 2023-05-31 06:30:00
        df.index = df.index - pd.DateOffset(years=0, months=11, days=23, hours=15, minutes=10)

        print(df.head())
        # If start and end time are given, filter the data
        if start_time is not None and end_time is not None:
            # If the start time and end time are given as strings, convert them to same type as
            # df.index
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            if isinstance(end_time, str):
                end_time = pd.to_datetime(end_time)
            df = df.loc[start_time:end_time]
        #df = df.drop(columns=["Date"])
    elif file_type == "cdf":
        if hv_file is not None:
            hv_file_list = [hv_folder + "/" + hv_file]
        else:
            hv_file_list = np.sort(glob.glob(hv_folder + "*.cdf"))
        for hv_file in hv_file_list:
            cdf_file = cdf(hv_file)
            df = pd.DataFrame(cdf_file["Data"])
            df.index = pd.to_datetime(cdf_file["Epoch"])
            df = df.sort_index()
            df = df.drop(columns=["Epoch"])
            df_list.append(df)
        df = pd.concat(df_list, axis=0)
    return df


def plot_hv(df=None, hv_file=None, hv_folder=None, file_type=None, plot_type=None, key_list=None,
            start_time=None, end_time=None, save_fig=False, fig_name=None, fig_folder=None):
    # Read the HV file
    df = read_hv_files(hv_file=hv_file, hv_folder=hv_folder, file_type=file_type,
                       start_time=start_time, end_time=end_time)

    # For each key, make a 2x2 plot, where the first subplot is the time series data, the second
    # subplot is the histogram, the third subplot is the heatmap and the fourth subplot is following
    # statistical values: Minimum and maximum time, maximum and minimum values, 10, 25, 50, 75 and 90
    # percentiles, mean, median, standard deviation, skewness and kurtosis.
    for key in key_list:
        # Filter data for the current key
        data = df[key]

        # Print that data is being plotted in cyan color
        print("\n \033[96m" + "Plotting data for " + key + "\033[00m \n")
        # Create a 2x2 plot
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

        # Plot 1: Time series data
        axes[0, 0].plot(df.index, df[key])
        # Format the x-axis to show the date and time so that they don't overlap
        axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        axes[0, 0].tick_params(axis='x', rotation=45)

        axes[0, 0].set_xlabel('Datetime')
        axes[0, 0].set_ylabel('Value')
        axes[0, 0].set_title('Time Series')

        # Plot 2: Histogram
        axes[0, 1].hist(df[key], bins=20)
        axes[0, 1].set_xlabel('Value')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].set_title('Histogram')

        # Plot 3: Heatmap
        heatmap_data = df.pivot_table(index=df.index.hour, columns=df.index.date, values=key)
        sns.heatmap(heatmap_data, cmap='RdBu_r', ax=axes[1, 0])
        axes[1, 0].set_title('Heatmap')

        # Plot 4: Statistical values
        axes[1, 1].axis('off')
        stats_text = f"Key: {key}\n\n" \
                     f"Minimum Time: {df.index.min()}\n" \
                     f"Maximum Time: {df.index.max()}\n\n" \
                     f"Minimum Value: {np.round(df[key].min(), 2)}\n" \
                     f"Maximum Value: {np.round(df[key].max(), 2)}\n\n" \
                     f"10th Percentile: {np.round(data.quantile(0.1), 2)}\n" \
                     f"25th Percentile: {np.round(data.quantile(0.25), 2)}\n" \
                     f"50th Percentile: {np.round(data.median(), 2)}\n" \
                     f"75th Percentile: {np.round(data.quantile(0.75), 2)}\n" \
                     f"90th Percentile: {np.round(data.quantile(0.9), 2)}\n\n" \
                     f"Mean: {np.round(data.mean(), 2)}\n" \
                     f"Standard Deviation: {np.round(data.std(), 2)}\n" \
                     f"Skewness: {np.round(data.skew(), 2)}\n" \
                     f"Kurtosis: {np.round(data.kurtosis(), 2)}"

        axes[1, 1].text(0.5, 0.5, stats_text, ha='center', va='center', fontsize=10)

        # Print that the plotting is done in cyan color
        print("\033[96m" + "Plotting done for " + key + "\033[00m")
        # Adjust spacing between subplots
        plt.tight_layout()
        # Save the plot as a pdf file
        if save_fig:
            if fig_name is None:
                fig_name = hv_file.split("/")[-1].split(".")[0]
            if fig_folder is None:
                fig_folder = hv_folder
            fig.savefig(fig_folder + "/" + fig_name + "_" + key + ".png")


if __name__ == "__main__":
    plt.close("all")
    input = {
        "hv_file": "payload_lexi_1716500403_21928_1717075719_20852_hk_output.csv",
        "hv_folder": "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/PIT/20230608_not_sent/processed_data/hk/",
        "file_type": "csv",
        "key_list": ['HK_id', 'PinPullerTemp', 'OpticsTemp', 'LEXIbaseTemp',
                     'HVsupplyTemp', '+5.2V_Imon', '+10V_Imon', '+3.3V_Imon', 'AnodeVoltMon',
                     '+28V_Imon', 'ADC_Ground', 'Cmd_count',
                     'DeltaEvntCount', 'DeltaDroppedCount'],
        # , "LEXIbaseTemp", "+3.3V_Imon", "+5.2V_Imon", "+10V_Imon",  "+28V_Imon", "AnodeVoltMon",
        # "DeltaEvntCount", "DeltaDroppedCount",]
        "save_fig": True,
        "fig_name": None,
        "start_time": "2024-05-23 22:42:00",
        "end_time": "2024-05-30 12:25:00",
        "fig_folder": "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/figures"
    }

    plot_hv(**input)

    # input = {
    #     "hv_file": "payload_lexi_1716500403_21928_1717075719_20852_hk_output.csv",
    #     "hv_folder": "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/PIT/20230608_not_sent/processed_data/hk/",
    #     "file_type": "csv",
    # }
    # df = read_hv_files(**input)
