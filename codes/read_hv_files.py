import glob

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns
from spacepy.pycdf import CDF as cdf
from tabulate import tabulate
import getpass

user_name = getpass.getuser()


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

        # print(df.head())
        # If start and end time are given, filter the data
        if start_time is not None and end_time is not None:
            # If the start time and end time are given as strings, convert them to same type as
            # df.index
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            if isinstance(end_time, str):
                end_time = pd.to_datetime(end_time)
            df = df.loc[start_time:end_time]

        # df = df.drop(columns=["Date"])
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
            start_time=None, end_time=None, save_fig=False, fig_name=None, fig_folder=None,
            fig_size=(6, 6), fig_dpi=100, fig_format="png", unit_dict=None, font_dict=None,
            dark_mode=False):

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

        if dark_mode:
            # Use a colorblind friendly palette
            color = "lime"
            edge_color = "black"
        else:
            color = "steelblue"
            edge_color = "white"
        # Create a 2x2 plot
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=fig_size, dpi=fig_dpi)

        # Plot 1: Time series data
        axes[0, 0].plot(df.index, df[key], color=color, linewidth=0., marker=".", markersize=2.5,)
        # Format the x-axis to show the date and time so that they don"t overlap
        axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H"))
        axes[0, 0].tick_params(axis="x", rotation=45)

        axes[0, 0].set_xlabel("Date [YYYY-MM-DD HH]", fontdict=font_dict["axis"])
        axes[0, 0].set_ylabel(f"{key} [{unit_dict[key]}]", fontdict=font_dict["axis"])
        axes[0, 0].set_title("Time Series", fontdict=font_dict["title"])

        # Set the x-axis limits
        axes[0, 0].set_xlim(df.index[0], df.index[-1])

        # Plot 2: Histogram
        axes[0, 1].hist(df[key], bins=20, color=color, edgecolor=edge_color, linewidth=1.2)
        axes[0, 1].set_xlabel(f"{key} [{unit_dict[key]}]", fontdict=font_dict["axis"])
        axes[0, 1].set_ylabel("Frequency", fontdict=font_dict["axis"])
        axes[0, 1].set_title("Histogram", fontdict=font_dict["title"])
        axes[0, 1].set_xlim(df[key].min(), df[key].max())
        # Plot 3: Heatmap
        heatmap_data = df.pivot_table(index=df.index.hour, columns=df.index.date, values=key)
        sns.heatmap(heatmap_data, cmap="RdBu_r", ax=axes[1, 0])
        # Format the x-axis to show the date and time so that they don"t overlap
        # axes[1, 0].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        axes[1, 0].tick_params(axis="x", rotation=45)
        axes[1, 0].set_xlabel("Date", fontdict=font_dict["axis"])
        axes[1, 0].set_ylabel("Hour", fontdict=font_dict["axis"])
        axes[1, 0].set_title("Heatmap", fontdict=font_dict["title"])

        # Set heatmap colorbar label
        cbar = axes[1, 0].collections[0].colorbar
        cbar.set_label(f"{key} [{unit_dict[key]}]", fontdict=font_dict["axis"], color=color)

        # Set the x-axis limits
        # axes[1, 0].set_xlim(df.index[0], df.index[-1])

        time_min = df.index.min()

        # print(df.head())
        # print(df.tail())
        # print(df.keys())
        time_max = df.index.max()
        # Extract YYYY-MM-DD HH:MM:SS from the time_min and time_max
        time_min = time_min.strftime("%Y-%m-%d %H:%M:%S")
        time_max = time_max.strftime("%Y-%m-%d %H:%M:%S")
        # Plot 4: Statistical values
        table_data = [
            ["Key", key],
            ["Minimum Time", time_min],
            ["Maximum Time", time_max],
            ["Minimum Value", np.round(df[key].min(), 2)],
            ["Maximum Value", np.round(df[key].max(), 2)],
            ["10th Percentile", np.round(data.quantile(0.1), 2)],
            ["25th Percentile", np.round(data.quantile(0.25), 2)],
            ["50th Percentile", np.round(data.median(), 2)],
            ["75th Percentile", np.round(data.quantile(0.75), 2)],
            ["90th Percentile", np.round(data.quantile(0.9), 2)],
            # ["Mean", np.round(data.mean(), 2)],
            ["Standard Deviation", np.round(data.std(), 2)],
            # ["Skewness", np.round(data.skew(), 2)],
            # ["Kurtosis", np.round(data.kurtosis(), 2)],
        ]

        if dark_mode:
            bbox = {"facecolor": "k", "alpha": 0.5, "pad": 1}
        else:
            bbox = {"facecolor": "w", "alpha": 0.5, "pad": 1}
        # Add table title outside the table
        axes[1, 1].text(0.5, 1., f"Statistics for {key}", fontdict=font_dict["table_title"],
                        verticalalignment="center", horizontalalignment="center")
        table_text = tabulate(table_data, tablefmt="fancy_grid", floatfmt=".2f", )
        axes[1, 1].axis("off")
        axes[1, 1].text(0.5, .95, table_text, fontdict=font_dict["table"],
                        verticalalignment="top", horizontalalignment="center",
                        bbox=bbox, transform=axes[1, 1].transAxes)

        # Print the statistical values in the fourth subplot as a table
        # axes[1, 1].table(cellText=[[stats_text]], loc="center", colLabels=["Statistics"], cellLoc="center")

        # axes[1, 1].text(0.5, 0.5, stats_text, ha="center", va="center", fontsize=10)

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
            fig.savefig(f"{fig_folder}/{fig_name}_{key}_{dark_mode}.{fig_format}", dpi=300, bbox_inches="tight", pad_inches=0.1, format=fig_format)
    return df


if __name__ == "__main__":
    plt.close("all")

    # Define whether to use dark_mode or not
    dark_mode = True
    unit_dict = {
        "HK_id": "#",
        "PinPullerTemp": r"$^\circ$C",
        "OpticsTemp": r"$^\circ$C",
        "LEXIbaseTemp": r"$^\circ$C",
        "HVsupplyTemp": r"$^\circ$C",
        "+5.2V_Imon": "mA",
        "+10V_Imon": "mA",
        "+3.3V_Imon": "mA",
        "AnodeVoltMon": "V",
        "+28V_Imon": "mA",
        "ADC_Ground": "V",
        "Cmd_count": "#",
        "DeltaEvntCount": "#",
        "DeltaDroppedCount": "#",
    }

    if dark_mode:
        color_list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                      "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        default_color = "white"
        plt.style.use("dark_background")
    else:
        color_list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                      "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        default_color = "k"
        plt.style.use("default")

    # Use tex for matplotlib
    plt.rc("text", usetex=False)
    plt.rc("font", family="serif")

    # Define a font_dict for labels, text, ticklabels, etc.
    # Define a font_dict for title
    font_dict_title = {
        "family": "serif",
        "color": default_color,
        "weight": "bold",
        "size": 16,
    }

    # Define a font_dict for axis labels
    font_dict_axis = {
        "family": "serif",
        "color": default_color,
        "weight": "normal",
        "size": 16,
    }

    # Define a font_dict for tick labels
    font_dict_tick = {
        "family": "serif",
        "color": default_color,
        "weight": "normal",
        "size": 12,
    }

    # Define a font_dict for tick labels
    font_dict_tick = {
        "family": "serif",
        "color": default_color,
        "weight": "normal",
        "size": 12,
    }

    # Define a font_dict for table
    font_dict_table = {
        "family": "serif",
        "color": default_color,
        "weight": "normal",
        "size": 10,
    }

    # Define a font_dict for table title
    font_dict_table_title = {
        "family": "serif",
        "color": default_color,
        "weight": "bold",
        "size": 16,
    }

    # Define a font_dict for all
    font_dict_all = {
        "title": font_dict_title,
        "axis": font_dict_axis,
        "tick": font_dict_tick,
        "table": font_dict_table,
        "table_title": font_dict_table_title,
    }

    input = {
        "hv_file": "payload_lexi_1716500403_21928_1717071517_5488_hk_output.csv",
        "hv_folder": f"/home/{user_name}/Desktop/git/Lexi-Bu/lxi_gui/data/PIT/20230608_not_sent/processed_data/alll_files/hk/",
        "file_type": "csv",
        # "key_list": ["PinPullerTemp"],
        "key_list": ["PinPullerTemp", "LEXIbaseTemp",
                     "HVsupplyTemp", "+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon",
                     "+28V_Imon", "ADC_Ground",
                     "DeltaEvntCount", "DeltaDroppedCount"],
        # "key_list": ["HK_id", "PinPullerTemp", "OpticsTemp", "LEXIbaseTemp",
        #              "HVsupplyTemp", "+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon",
        #              "+28V_Imon", "ADC_Ground", "Cmd_count",
        #              "DeltaEvntCount", "DeltaDroppedCount"],
        # , "LEXIbaseTemp", "+3.3V_Imon", "+5.2V_Imon", "+10V_Imon",  "+28V_Imon", "AnodeVoltMon",
        # "DeltaEvntCount", "DeltaDroppedCount",]
        "save_fig": True,
        "fig_name": None,
        "start_time": "2023-05-31 07:30:00",
        "end_time": "2023-06-06 22:00:00",
        "fig_folder": f"/home/{user_name}/Desktop/git/Lexi-Bu/lxi_gui/figures/hv_testing/",
        "fig_size": (12, 12),
        "fig_dpi": 300,
        "fig_format": "png",
        "unit_dict": unit_dict,
        "font_dict": font_dict_all,
        "dark_mode": dark_mode,
    }

    df = plot_hv(**input)

    # input = {
    #     "hv_file": "payload_lexi_1716500403_21928_1717075719_20852_hk_output.csv",
    #     "hv_folder": "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/PIT/20230608_not_sent/processed_data/hk/",
    #     "file_type": "csv",
    # }
    # df = read_hv_files(**input)
