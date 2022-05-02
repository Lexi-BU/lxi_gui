import tkinter as tk
from tkinter import Variable, filedialog, ttk
from tkinter import PhotoImage, font
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import importlib
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import lxi_gui_plot_routines as plot_routines

importlib.reload(plot_routines)

# Default file names
sci_file_name = "../data/processed_data/sci/2022_04_21_1431_LEXI_raw_LEXI_unit_1_mcp_unit_1_eBox-1987_qudsi.csv"
hk_file_name = "../data/processed_data/hk/2022_04_21_1431_LEXI_raw_LEXI_unit_1_mcp_unit_1_eBox-1987_qudsi.csv"

#sci_file_name = "../data/raw_data/2022_04_21_1431_LEXI_HK_unit_1_mcp_unit_1_eBox_1987_hk_/2022_04_21_1431_LEXI_unit_1_mcp_unit_1_eBox_1987.csv"
#hk_file_name = "../data/raw_data/2022_04_21_1431_LEXI_HK_unit_1_mcp_unit_1_eBox_1987_hk_/2022_04_21_1431_LEXI_HK_unit_1_mcp_unit_1_eBox_1987_hk_.csv"


def open_file_sci():
    # define a global variable for the file name
    global sci_file_name
    file_val = filedialog.askopenfilename(initialdir="../data/processed_data/sci/",
                                          title="Select file",
                                          filetypes=(("csv files", "*.csv"),
                                                     ("all files", "*.*"))
                                          )
    print(f"Loaded {file_val} in the data base")
    #df = pd.read_csv(file_val)

    sci_file_name = file_val
    return file_val


def open_file_hk():
    # define a global variable for the file name
    global hk_file_name
    file_val = filedialog.askopenfilename(initialdir="../data/processed_data/hk/",
                                          title="Select file",
                                          filetypes=(("csv files", "*.csv"),
                                                     ("all files", "*.*"))
                                          )
    print(f"Loaded {file_val} in the data base")
    #df = pd.read_csv(file_val)

    hk_file_name = file_val
    return file_val


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
    if file_val is None:
        file_val = sci_file_name

    global df_slice_sci
    df = pd.read_csv(file_val)

    # Replace index with timestamp
    try:
        df.set_index('TimeStamp', inplace=True)
    except Exception:
        df['Channel4'] = df['Channel3']
        df['Channel3'] = df['Channel2']
        df['Channel2'] = df['Channel1']
        df['Channel1'] = df['Timestamp']
        df['Timestamp'] = df.index
        df.set_index('Timestamp', inplace=True)
    # Sort the dataframe by timestamp
    df = df.sort_index()

    if t_start is None:
        t_start = df.index.min()
    if t_end is None:
        t_end = df.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_sci = df.loc[t_start:t_end]

    # Find the x and y coordinates from the voltage values.
    df_slice_sci['x_val'] = df_slice_sci.Channel1 / (df_slice_sci.Channel1 + df_slice_sci.Channel3)
    df_slice_sci['y_val'] = df_slice_sci.Channel2 / (df_slice_sci.Channel2 + df_slice_sci.Channel4)

    return df_slice_sci


def read_csv_hk(file_val=None, t_start=None, t_end=None):

    if file_val is None:
        file_val = hk_file_name

    global df_slice_hk
    df = pd.read_csv(file_val)

    # Replace index with timestamp
    try:
        df.set_index('TimeStamp', inplace=True)
    except Exception:
        df.set_index('Time', inplace=False)

    # Sort the dataframe by timestamp
    df = df.sort_index()

    if t_start is None:
        t_start = df.index.min()
    if t_end is None:
        t_end = df.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_hk = df.loc[t_start:t_end]

    return df_slice_hk


def plot_data(file_name_sci=None, file_name_hk=None, t_start=None, t_end=None):

    # TODO: Convert this to a class and decouple it into multiple plot routines for more flexibility
    # in plotting
    # Check if type of start_time is int or float
    if file_name_sci is None:
        file_name_sci = file_name_sci

    if file_name_hk is None:
        file_name_hk = file_name_hk

    # Try to convert the start_time and end_time to float or int
    try:
        t_start = float(start_time.get())
    except Exception as e:
        print(f"Warning: {e}, plotting the entire data set")
        pass
    try:
        t_end = float(end_time.get())
    except Exception as e:
        print(f"Warning: {e}, plotting the entire data set")
        pass
    if not isinstance(t_start, (int, float)):
        t_start = None

    if not isinstance(t_end, (int, float)):
        t_end = None

    # Read entries from the text boxes
    try:
        x_min = float(x_min_entry.get())
    except Exception:
        x_min = None
    try:
        x_max = float(x_max_entry.get())
    except Exception:
        x_max = None
    try:
        y_min = float(y_min_entry.get())
    except Exception:
        y_min = None
    try:
        y_max = float(y_max_entry.get())
    except Exception:
        y_max = None
    try:
        bins = int(hist_bins_entry.get())
    except Exception:
        bins = None
    try:
        cmin = int(c_min_entry.get())
    except Exception:
        cmin = None
    try:
        cmax = int(c_max_entry.get())
    except Exception:
        cmax = None
    try:
        density = bool(int(density_entry.get()))
    except Exception:
        density = None

    if norm_entry.get() == "linear":
        norm = "linear"
    elif norm_entry.get() == "log":
        norm = "log"
    else:
        norm = None

    df_slice_hk = read_csv_hk(file_val=file_name_hk, t_start=t_start, t_end=t_end)
    df_slice_sci = read_csv_sci(file_val=file_name_sci, t_start=t_start, t_end=t_end)
    try:
        df_slice_sci = df_slice_sci[df_slice_sci['IsCommanded']==False]
    except Exception:
        pass

    # Display the time series plot
    fig1_ts = plot_routines.plot_indiv_time_series(df=df_slice_hk, key=plot_opt_entry_1.get(),
                                                   ms=2, alpha=1)

    load1_ts = Image.open(f"../figures/gui_figures/{plot_opt_entry_1.get()}_time_series_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load1_ts = load1_ts.resize((int(fig1_ts.get_figwidth() * 100),
                                int(fig1_ts.get_figheight() * 60)))
    render1_ts = ImageTk.PhotoImage(load1_ts)
    img1_ts = tk.Label(image=render1_ts)
    img1_ts.image = render1_ts
    img1_ts.grid(row=2, column=0, rowspan=3, columnspan=3, sticky="new")

    fig2_ts = plot_routines.plot_indiv_time_series(df=df_slice_hk, key=plot_opt_entry_2.get(),
                                                   ms=2, alpha=1)
    load2_ts = Image.open(f"../figures/gui_figures/{plot_opt_entry_2.get()}_time_series_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load2_ts = load2_ts.resize((int(fig2_ts.get_figwidth() * 100),
                                int(fig2_ts.get_figheight() * 60)))
    render2_ts = ImageTk.PhotoImage(load2_ts)
    img2_ts = tk.Label(image=render2_ts)
    img2_ts.image = render2_ts
    img2_ts.grid(row=6, column=0, rowspan=3, columnspan=3, sticky="new")

    fig3_ts = plot_routines.plot_indiv_time_series(df=df_slice_hk, key=plot_opt_entry_3.get(),
                                                   ms=2, alpha=1)
    load3_ts = Image.open(f"../figures/gui_figures/{plot_opt_entry_3.get()}_time_series_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load3_ts = load3_ts.resize((int(fig3_ts.get_figwidth() * 100),
                                int(fig3_ts.get_figheight() * 60)))
    render3_ts = ImageTk.PhotoImage(load3_ts)
    img3_ts = tk.Label(image=render3_ts)
    img3_ts.image = render3_ts
    img3_ts.grid(row=10, column=0, rowspan=3, columnspan=3, sticky="new")

    fig2 = plot_routines.plot_histogram(df=df_slice_sci, x_min=x_min, x_max=x_max,
                                        y_min=y_min, y_max=y_max, bins=bins, cmin=cmin, cmax=cmax,
                                        density=density, norm=norm)
    load2 = Image.open("../figures/gui_figures/xy_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load2 = load2.resize((int(fig2.get_figwidth() * 120),
                          int(fig2.get_figheight() * 120)))
    render2 = ImageTk.PhotoImage(load2)
    img2 = tk.Label(image=render2)
    img2.image = render2
    img2.grid(row=2, column=3, rowspan=7, columnspan=2, sticky="new")

    # Display the histogram plots
    # TODO: Find out the best way to display the histogram plots (aspect ratios and stuff)
    fig3 = plot_routines.plot_kde(df=df_slice_sci, key1="Channel2", key2="Channel4")
    load3 = Image.open("../figures/gui_figures/kde_plot_Channel2_Channel4.png")
    # Resize the image to fit the canvas (in pixels)
    load3 = load3.resize((int(fig3.get_figwidth() * 80),
                          int(fig3.get_figheight() * 80)))
    render3 = ImageTk.PhotoImage(load3)
    img3 = tk.Label(image=render3)
    img3.image = render3
    img3.grid(row=9, column=3, rowspan=4, columnspan=1, sticky="ne")

    fig4 = plot_routines.plot_kde(df=df_slice_sci, key1="Channel1", key2="Channel3")
    load4 = Image.open("../figures/gui_figures/kde_plot_Channel1_Channel3.png")
    # Resize the image to fit the canvas (in pixels)
    load4 = load4.resize((int(fig4.get_figwidth() * 80),
                          int(fig4.get_figheight() * 80)))
    render4 = ImageTk.PhotoImage(load4)
    img4 = tk.Label(image=render4)
    img4.image = render4
    img4.grid(row=9, column=4, rowspan=4, columnspan=1, sticky="nw")


root = tk.Tk()
#root.rowconfigure(, {'minsize': 3})
root.columnconfigure(0, {'minsize': 3}, weight=1)
root.columnconfigure(1, {'minsize': 3}, weight=1)
root.columnconfigure(2, {'minsize': 3}, weight=1)
root.columnconfigure(3, {'minsize': 3}, weight=2)
root.columnconfigure(4, {'minsize': 3}, weight=2)
root.columnconfigure(5, {'minsize': 3}, weight=1)
root.columnconfigure(6, {'minsize': 3}, weight=1)

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=1)
root.rowconfigure(6, weight=1)
root.rowconfigure(7, weight=1)
root.rowconfigure(8, weight=1)
root.rowconfigure(9, weight=1)
root.rowconfigure(10, weight=1)
root.rowconfigure(11, weight=1)
root.rowconfigure(12, weight=1)
root.rowconfigure(13, weight=1)
#root.rowconfigure(14, weight=1)
#root.rowconfigure(15, weight=1)

root.title("LEXI GUI")
# Add the lxi logo
#img = tk.PhotoImage(file="../../figures/lxi_gui_figures/lxi_icon.ico")
#root.tk.call('wm', 'iconphoto', root._w, img)
#root.iconbitmap("../../figures/lxi_gui_figures/lxi_icon.ico")
root.geometry("600x550")
root.resizable(True, True)

# Create a label widget and justify the text
#my_label = tk.Label(root, text="LEXI GUI", font=(
#    "Helvetica", 20), justify="center")
#my_label.pack()
#my_label.grid(row=0, column=1, columnspan=4, sticky="nsew")

# Choose a font style for GUI
font_style = font.Font(family="Helvetica")
font_style_box = font.Font(family="Helvetica", weight="bold")
font_style_big = font.Font(family="Helvetica")

# insert a file load button
sci_file_load_button = tk.Button(root, text="Load Science File", command=open_file_sci,
                                 font=font_style)
sci_file_load_button.grid(row=0, column=0, columnspan=1, pady=0, sticky="nsew")

hk_file_load_button = tk.Button(root, text="Load HK File", command=open_file_hk,
                                font=font_style)
hk_file_load_button.grid(row=0, column=1, columnspan=1, pady=0, sticky="nsew")

b_file_load_button = tk.Button(root, text="Load binary File", command=open_file_sci,
                               font=font_style)
b_file_load_button.grid(row=0, column=2, columnspan=1, pady=0, sticky="nsew")

# List out all the columns in the housekeeping file as options for time series plots
ts_options = ['PinPullerTemp', 'OpticsTemp', 'LEXIbaseTemp', 'HVsupplyTemp', '+5.2V_Imon',
              '+10V_Imon', '+3.3V_Imon', 'AnodeVoltMon', '+28V_Imon', 'ADC_Ground', 'Cmd_count',
              'Pinpuller_Armed', 'Unused', 'Unused.1', 'HVmcpAuto', 'HVmcpMan', 'DeltaEvntCount',
              'DeltaDroppedCount', 'DeltaLostevntCount']

plot_opt_label_1 = tk.Label(root, text="Plot options:", font=font_style_box)
plot_opt_label_1.grid(row=1, column=0, columnspan=1, pady=0, sticky="nsew")
plot_opt_entry_1 = tk.StringVar(root)
plot_opt_entry_1.set(ts_options[4])
ts_menu_1 = tk.OptionMenu(root, plot_opt_entry_1, *ts_options)
ts_menu_1.grid(row=1, column=1, columnspan=2, sticky="ne")

#plot_opt_label_2 = tk.Label(root, text="Plot options:", font=font_style_box)
#plot_opt_label_2.grid(row=5, column=0, columnspan=1, pady=0, sticky="nsew")
plot_opt_entry_2 = tk.StringVar(root)
plot_opt_entry_2.set(ts_options[5])
ts_menu_2 = tk.OptionMenu(root, plot_opt_entry_2, *ts_options)
ts_menu_2.grid(row=5, column=1, columnspan=2, sticky="ne")

#plot_opt_label_3 = tk.Label(root, text="Plot options:", font=font_style_box)
#plot_opt_label_3.grid(row=9, column=0, columnspan=1, pady=0, sticky="nsew")
plot_opt_entry_3 = tk.StringVar(root)
plot_opt_entry_3.set(ts_options[7])
ts_menu_3 = tk.OptionMenu(root, plot_opt_entry_3, *ts_options)
ts_menu_3.grid(row=9, column=1, columnspan=2, sticky="ne")

# Add buttons for plotting values

# The minimum value of x-axis for histogram plot
x_min_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
x_min_entry.insert(0, 0)
x_min_entry.grid(row=1, column=5, columnspan=1, sticky="n")
x_min_label = tk.Label(root, text="X Min", font=font_style_box)
x_min_label.grid(row=1, column=6, columnspan=1, sticky="n")

# The maximum value of x-axis for histogram plot
x_max_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
x_max_entry.insert(0, "X Maximum")
x_max_entry.grid(row=2, column=5, columnspan=1, sticky="n")
x_max_label = tk.Label(root, text="X Max", font=font_style_box)
x_max_label.grid(row=2, column=6, columnspan=1, sticky="n")

# The minimum value of y-axis for histogram plot
y_min_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
y_min_entry.insert(0, "Y Minimum")
y_min_entry.grid(row=3, column=5, columnspan=1, sticky="n")
y_min_label = tk.Label(root, text="Y Min", font=font_style_box)
y_min_label.grid(row=3, column=6, columnspan=1, sticky="n")

# The maximum value of y-axis for histogram plot
y_max_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
y_max_entry.insert(0, "Y Maximum")
y_max_entry.grid(row=4, column=5, columnspan=1, sticky="n")
y_max_label = tk.Label(root, text="Y Max", font=font_style_box)
y_max_label.grid(row=4, column=6, columnspan=1, sticky="n")

# The number of bins for histogram plot
hist_bins_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
hist_bins_entry.insert(0, "Bins")
hist_bins_entry.grid(row=5, column=5, columnspan=1, sticky="n")
hist_bins_label = tk.Label(root, text="Bins", font=font_style_box)
hist_bins_label.grid(row=5, column=6, columnspan=1, sticky="n")

# Mimimum number of data points in each bin for the histogram plot
c_min_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
c_min_entry.insert(0, "Colorbar Mininimum")
c_min_entry.grid(row=6, column=5, columnspan=1, sticky="n")
c_min_label = tk.Label(root, text="C Min", font=font_style_box)
c_min_label.grid(row=6, column=6, columnspan=1, sticky="n")

# Maximum number of data points in each bin for the histogram plot
c_max_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
c_max_entry.insert(0, "Colorbar Maximum")
c_max_entry.grid(row=7, column=5, columnspan=1, sticky="n")
c_max_label = tk.Label(root, text="C Max", font=font_style_box)
c_max_label.grid(row=7, column=6, columnspan=1, sticky="n")

# Choose whether to plot probability density or the number of data points in each bin (is Bool)
density_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
density_entry.insert(0, "0 or 1")
density_entry.grid(row=8, column=5, columnspan=1, sticky="n")
density_label = tk.Label(root, text="Density", font=font_style_box)
density_label.grid(row=8, column=6, columnspan=1, sticky="n")

# Choose whther the colorbar is in 'linear' or 'log' scale (default is 'log', other option is 
# 'linear')
norm_entry = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
norm_entry.insert(0, "Norm style")
norm_entry.grid(row=9, column=5, columnspan=1, sticky="n")
norm_label = tk.Label(root, text="Norm", font=font_style_box)
norm_label.grid(row=9, column=6, columnspan=1, sticky="n")


# Add an input box with a label for start time
start_time = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
start_time.insert(0, "YYYY-MM-DD HH:MM:SS")
start_time.grid(row=13, column=0, columnspan=1, sticky="")
start_time_label = tk.Label(root, text="Start Time", font=font_style)
start_time_label.grid(row=14, column=0, columnspan=1, sticky="")

# Add an input box with a label for end time
end_time = tk.Entry(root, justify="center", bg="white", fg="black", borderwidth=2)
end_time.insert(0, "YYYY-MM-DD HH:MM:SS")
end_time.grid(row=13, column=1, columnspan=1, sticky="")
end_time_label = tk.Label(root, text="End Time", font=font_style)
end_time_label.grid(row=14, column=1, columnspan=1, sticky="")

# Add a button to plot the data
plot_button = tk.Button(root, text="Plot", width=10, font=font_style_box, command=plot_data)
plot_button.grid(row=13, column=2, columnspan=1, rowspan=1, sticky="ne")
# Add a button to the window to get start time
#start_button = tk.Button(root, text="Start", command=lambda: print("Start"))
#start_button.grid(row=13, column=3, columnspan=1)

# Add a quit button
quit_button = tk.Button(
    root, text="Quit", command=root.destroy, font=font_style_big)
quit_button.grid(row=13, column=5, columnspan=1, rowspan=1, sticky="n")
# Print the value in the entry box

root.mainloop()
