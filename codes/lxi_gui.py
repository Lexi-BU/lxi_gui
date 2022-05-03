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
import plot_various_data as pvd
import lxi_read_files as lxrf

import global_variables


importlib.reload(plot_routines)
importlib.reload(pvd)
importlib.reload(lxrf)
importlib.reload(global_variables)

global_variables.init()

"""
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
        print(f"Error: {e}")
        pass
    try:
        t_end = float(end_time.get())
    except Exception as e:
        print(f"Error: {e}")
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
        density = bool(int(density_entry.get()))
    except Exception:
        density = None

    if norm_entry.get() == "linear":
        norm = "linear"
    elif norm_entry.get() == "log":
        norm = "log"
    else:
        norm = None

    print(f"Density is {density}")

    df_slice_hk = read_csv_hk(file_val=file_name_hk, t_start=t_start, t_end=t_end)
    df_slice_sci = read_csv_sci(file_val=file_name_sci, t_start=t_start, t_end=t_end)
    df_slice_sci = df_slice_sci[df_slice_sci['IsCommanded']==False]

    # Display the time series plot
    fig1_ts = plot_routines.plot_indiv_time_series(df=df_slice_hk, key=plot_opt_entry_1.get(),
                                                   ms=2, alpha=1)

    load1_ts = Image.open(f"figures/{plot_opt_entry_1.get()}_time_series_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load1_ts = load1_ts.resize((int(fig1_ts.get_figwidth() * 100),
                                int(fig1_ts.get_figheight() * 60)))
    render1_ts = ImageTk.PhotoImage(load1_ts)
    img1_ts = tk.Label(image=render1_ts)
    img1_ts.image = render1_ts
    img1_ts.grid(row=2, column=0, rowspan=3, columnspan=2, sticky="w")

    fig2_ts = plot_routines.plot_indiv_time_series(df=df_slice_hk, key=plot_opt_entry_2.get(),
                                                   ms=2, alpha=1)
    load2_ts = Image.open(f"figures/{plot_opt_entry_2.get()}_time_series_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load2_ts = load2_ts.resize((int(fig2_ts.get_figwidth() * 100),
                                int(fig2_ts.get_figheight() * 60)))
    render2_ts = ImageTk.PhotoImage(load2_ts)
    img2_ts = tk.Label(image=render2_ts)
    img2_ts.image = render2_ts
    img2_ts.grid(row=6, column=0, rowspan=3, columnspan=2, sticky="w")

    fig3_ts = plot_routines.plot_indiv_time_series(df=df_slice_hk, key=plot_opt_entry_3.get(),
                                                    ms=2, alpha=1)
    load3_ts = Image.open(f"figures/{plot_opt_entry_3.get()}_time_series_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load3_ts = load3_ts.resize((int(fig3_ts.get_figwidth() * 100),
                                int(fig3_ts.get_figheight() * 60)))
    render3_ts = ImageTk.PhotoImage(load3_ts)
    img3_ts = tk.Label(image=render3_ts)
    img3_ts.image = render3_ts
    img3_ts.grid(row=10, column=0, rowspan=3, columnspan=2, sticky="w")

    fig2 = plot_routines.plot_histogram(df=df_slice_sci, x_min=x_min, x_max=x_max,
                                        y_min=y_min, y_max=y_max, bins=bins, cmin=cmin,
                                        density=density, norm=norm)
    load2 = Image.open("figures/xy_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load2 = load2.resize((int(fig2.get_figwidth() * 60),
                          int(fig2.get_figheight() * 60)))
    render2 = ImageTk.PhotoImage(load2)
    img2 = tk.Label(image=render2)
    img2.image = render2
    img2.grid(row=2, column=2, rowspan=10, columnspan=2, sticky="n")

    # Display the histogram plots
    # TODO: Find out the best way to display the histogram plots (aspect ratios and stuff)
    fig3 = plot_routines.plot_kde(df=df_slice_sci, key1="Channel1", key2="Channel2")
    load3 = Image.open("figures/kde_plot_Channel1_Channel2.png")
    # Resize the image to fit the canvas (in pixels)
    load3 = load3.resize((int(fig3.get_figwidth() * 70),
                          int(fig3.get_figheight() * 70)))
    render3 = ImageTk.PhotoImage(load3)
    img3 = tk.Label(image=render3)
    img3.image = render3
    img3.grid(row=14, column=2, rowspan=3, columnspan=1, sticky="n")

    fig4 = plot_routines.plot_kde(df=df_slice_sci, key1="Channel3", key2="Channel4")
    load4 = Image.open("figures/kde_plot_Channel3_Channel4.png")
    # Resize the image to fit the canvas (in pixels)
    load4 = load4.resize((int(fig4.get_figwidth() * 70),
                          int(fig4.get_figheight() * 70)))
    render4 = ImageTk.PhotoImage(load4)
    img4 = tk.Label(image=render4)
    img4.image = render4
    img4.grid(row=14, column=3, rowspan=3, columnspan=1, sticky="n")
"""

root = tk.Tk()
#root.rowconfigure(, {'minsize': 3})
root.columnconfigure(0, {'minsize': 3}, weight=1)
root.columnconfigure(1, {'minsize': 3}, weight=2)
root.columnconfigure(2, {'minsize': 3}, weight=3)
root.columnconfigure(3, {'minsize': 3}, weight=3)
root.columnconfigure(4, {'minsize': 3}, weight=1)
root.columnconfigure(5, {'minsize': 3}, weight=1)
#root.columnconfigure(6, {'minsize': 3}, weight=6)
#root.columnconfigure(7, {'minsize': 3}, weight=2)
#root.columnconfigure(8, {'minsize': 3}, weight=2)
#root.columnconfigure(9, {'minsize': 3}, weight=2)
#root.columnconfigure(10, {'minsize': 3}, weight=1)

#root.rowconfigure(9, {'minsize': 3}, weight=1)

root.title("LEXI GUI")
# Add the lxi logo
#img = tk.PhotoImage(file="../../figures/lxi_gui_figures/lxi_icon.ico")
#root.tk.call('wm', 'iconphoto', root._w, img)
#root.iconbitmap("../../figures/lxi_gui_figures/lxi_icon.ico")
root.geometry("600x600")
root.resizable(True, True)

# Create a label widget and justify the text
#my_label = tk.Label(root, text="LEXI GUI", font=(
#    "Helvetica", 20), justify="center")
#my_label.pack()
#my_label.grid(row=0, column=1, columnspan=4, sticky="nsew")

# Choose a font style for GUI
font_style = font.Font(family="Helvetica", size=12)
font_style_box = font.Font(family="Helvetica", size=12, weight="bold")
font_style_big = font.Font(family="Helvetica", size=25)

# insert a file load button
# For science file
sci_file_load_button = tk.Button(root, text="Load Science File", command=lxrf.open_file_sci,
                                 font=font_style)
sci_file_load_button.grid(row=0, column=0, columnspan=1, pady=0, sticky="w")

sci_file_load_entry = tk.Entry(root, font=font_style, width=30, justify="left", bg="white",
                              fg="black", relief="flat", borderwidth=2)
sci_file_load_entry.grid(row=0, column=1, columnspan=4, pady=0, sticky="w")

# insert the file_load_entry value into the entry box only if the sci_file_load_button is clicked
sci_file_load_button.config(command=lambda: sci_file_load_entry.insert(0, lxrf.open_file_sci()))

# For housekeeping file
hk_file_load_button = tk.Button(root, text="Load HK File", command=lxrf.open_file_hk,
                                font=font_style)
hk_file_load_button.grid(row=1, column=0, columnspan=1, pady=0, sticky="w")
hk_file_load_entry = tk.Entry(root, font=font_style, width=30, justify="left", bg="white",
                              fg="black", relief="flat", borderwidth=2)
hk_file_load_entry.grid(row=1, column=1, columnspan=4, pady=0, sticky="w")

# insert the file_load_entry value into the entry box only if the hk_file_load_button is clicked
hk_file_load_button.config(command=lambda: hk_file_load_entry.insert(0, lxrf.open_file_hk()))

# For binary file
b_file_load_button = tk.Button(root, text="Load binary File", command=lxrf.open_file_b,
                               font=font_style)
b_file_load_button.grid(row=2, column=0, columnspan=1, pady=0, sticky="w")
b_file_load_entry = tk.Entry(root, font=font_style, width=30, justify="left", bg="white",
                             fg="black", relief="flat", borderwidth=2)
b_file_load_entry.grid(row=2, column=1, columnspan=4, pady=0, sticky="w")
# insert the file_load_entry value into the entry box only if the b_file_load_button is clicked
b_file_load_button.config(command=lambda: b_file_load_entry.insert(0, lxrf.open_file_b()))

# If the global_variables.all_file_details["df_slice_hk"] is not empty, then set the comlumn names
# to the columns in the dataframe
if bool("df_slice_hk" in global_variables.all_file_details.keys()):
    ts_options = global_variables.all_file_details["df_slice_hk"].columns.tolist()
else:
    ts_options = ['HK_id', 'PinPullerTemp', 'OpticsTemp', 'LEXIbaseTemp', 'HVsupplyTemp',
                  '+5.2V_Imon', '+10V_Imon', '+3.3V_Imon', 'AnodeVoltMon', '+28V_Imon',
                  'ADC_Ground', 'Cmd_count', 'Pinpuller_Armed', 'Unused', 'Unused.1',
                  'HVmcpAuto', 'HVmcpMan', 'DeltaEvntCount', 'DeltaDroppedCount',
                  'DeltaLostevntCount']

# check if global_variables.all_file_details["df_slice_hk"] exists
plot_opt_label_1 = tk.Label(root, text="Plot options:", font=font_style_box)
plot_opt_label_1.grid(row=3, column=0, columnspan=1, pady=0, sticky="w")
plot_opt_entry_1 = tk.StringVar(root)
plot_opt_entry_1.set("Select a column")
ts_menu_1 = tk.OptionMenu(root, plot_opt_entry_1, *ts_options)
ts_menu_1.grid(row=3, column=1, columnspan=1, sticky="w")

plot_opt_entry_2 = tk.StringVar(root)
plot_opt_entry_2.set("Select a column")
ts_menu_2 = tk.OptionMenu(root, plot_opt_entry_2, *ts_options)
ts_menu_2.grid(row=8, column=1, columnspan=1, sticky="w")

#plot_opt_label_3 = tk.Label(root, text="Plot options:", font=font_style_box)
#plot_opt_label_3.grid(row=9, column=0, columnspan=1, pady=0, sticky="w")
plot_opt_entry_3 = tk.StringVar(root)
plot_opt_entry_3.set("Select a column")
ts_menu_3 = tk.OptionMenu(root, plot_opt_entry_3, *ts_options)
ts_menu_3.grid(row=13, column=1, columnspan=1, sticky="w")

# if any of the ts_options are changed, update the plot
#pvd.plot_diff_data.__init__()
plot_opt_entry_1.trace("w", lambda *args: pvd.plot_diff_data.ts_plots_1())
#plot_opt_entry_2.trace("w", lambda *args: pvd.plot_diff_data.ts_plots_1(key=plot_opt_entry_2.get()))
#plot_opt_entry_3.trace("w", lambda *args: pvd.plot_diff_data.ts_plots_1(key=plot_opt_entry_3.get()))
#
# The minimum value of x-axis for histogram plot
x_min_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
x_min_entry.insert(0, 0)
x_min_entry.grid(row=1, column=4, columnspan=1, sticky="n")
x_min_label = tk.Label(root, text="X Min", font=font_style_box)
x_min_label.grid(row=1, column=5, columnspan=1, sticky="n")

# The maximum value of x-axis for histogram plot
x_max_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
x_max_entry.insert(0, "X Maximum")
x_max_entry.grid(row=2, column=4, columnspan=1, sticky="n")
x_max_label = tk.Label(root, text="X Max", font=font_style_box)
x_max_label.grid(row=2, column=5, columnspan=1, sticky="n")

# The minimum value of y-axis for histogram plot
y_min_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
y_min_entry.insert(0, "Y Minimum")
y_min_entry.grid(row=3, column=4, columnspan=1, sticky="n")
y_min_label = tk.Label(root, text="Y Min", font=font_style_box)
y_min_label.grid(row=3, column=5, columnspan=1, sticky="n")

# The maximum value of y-axis for histogram plot
y_max_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
y_max_entry.insert(0, "Y Maximum")
y_max_entry.grid(row=4, column=4, columnspan=1, sticky="n")
y_max_label = tk.Label(root, text="Y Max", font=font_style_box)
y_max_label.grid(row=4, column=5, columnspan=1, sticky="n")

# The number of bins for histogram plot
hist_bins_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
hist_bins_entry.insert(0, "Bins")
hist_bins_entry.grid(row=5, column=4, columnspan=1, sticky="n")
hist_bins_label = tk.Label(root, text="Bins", font=font_style_box)
hist_bins_label.grid(row=5, column=5, columnspan=1, sticky="n")

# Mimimum number of data points in each bin for the histogram plot
c_min_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
c_min_entry.insert(0, "Colorbar Mininimum")
c_min_entry.grid(row=6, column=4, columnspan=1, sticky="n")
c_min_label = tk.Label(root, text="C Min", font=font_style_box)
c_min_label.grid(row=6, column=5, columnspan=1, sticky="n")

# Maximum number of data points in each bin for the histogram plot
c_max_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
c_max_entry.insert(0, "Colorbar Maximum")
c_max_entry.grid(row=7, column=4, columnspan=1, sticky="n")
c_max_label = tk.Label(root, text="C Max", font=font_style_box)
c_max_label.grid(row=7, column=5, columnspan=1, sticky="n")

# Choose whether to plot probability density or the number of data points in each bin (is Bool)
density_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
density_entry.insert(0, "Density")
density_entry.grid(row=8, column=4, columnspan=1, sticky="n")
density_label = tk.Label(root, text="Density", font=font_style_box)
density_label.grid(row=8, column=5, columnspan=1, sticky="n")

# Choose whther the colorbar is in 'linear' or 'log' scale (default is 'log', other option is 
# 'linear')
norm_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
norm_entry.insert(0, "Norm style")
norm_entry.grid(row=9, column=4, columnspan=1, sticky="n")
norm_label = tk.Label(root, text="Norm", font=font_style_box)
norm_label.grid(row=9, column=5, columnspan=1, sticky="n")


# Add an input box with a label for start time
start_time = tk.Entry(root, width=30, justify="center", bg="white", fg="black", borderwidth=2)
start_time.insert(0, "YYYY-MM-DD HH:MM:SS")
start_time.grid(row=17, column=2, columnspan=1, pady=5, ipadx=10, ipady=10)
start_time_label = tk.Label(root, text="Start Time", font=font_style)
start_time_label.grid(row=18, column=2, columnspan=1)

# Add an input box with a label for end time
end_time = tk.Entry(root, width=30, justify="center", bg="white", fg="black", borderwidth=2)
end_time.insert(0, "YYYY-MM-DD HH:MM:SS")
end_time.grid(row=17, column=3, columnspan=1, pady=5, ipadx=10, ipady=10)
end_time_label = tk.Label(root, text="End Time", font=font_style)
end_time_label.grid(row=18, column=3, columnspan=1)

# Add a button to plot the data
plot_button = tk.Button(root, text="Plot Time Series", font=font_style_box, justify="center",
                        command=pvd.plot_diff_data.ts_plots_1)
plot_button.grid(row=18, column=0, columnspan=2, rowspan=1)
# Add a button to the window to get start time
#start_button = tk.Button(root, text="Start", command=lambda: print("Start"))
#start_button.grid(row=13, column=3, columnspan=1)

# Add a quit button
quit_button = tk.Button(
    root, text="Quit", command=root.destroy, font=font_style_big)
quit_button.grid(row=18, column=5, columnspan=1, rowspan=1)
# Print the value in the entry box


root.mainloop()
