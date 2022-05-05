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
import lxi_gui_plot_routines as lgpr
#import plot_various_data as pvd
import lxi_read_files as lxrf

import global_variables


#importlib.reload(plot_routines)
importlib.reload(lgpr)
importlib.reload(lxrf)
importlib.reload(global_variables)

global_variables.init()


def load_ts_plots(df_slice_hk=None, plot_key=None, start_time=None, end_time=None, row=2):
    """
    Loads the time series plots for the selected time range and displays them in the GUI.

    Parameters
    ----------
    df_slice_hk : pandas.DataFrame
        The dataframe containing the HK data.
    plot_key : str
        The key of the HK data to be plotted.
    start_time : str
        The start time of the time range to be plotted.
    end_time : str
        The end time of the time range to be plotted.
    row : int
        The row in which the plots should be displayed.

    Returns
    -------
    None
    """
    fig_ts = lgpr.plot_data_class(df_slice_hk=df_slice_hk, plot_key=plot_key, start_time=start_time,
                                end_time=end_time).ts_plots()
    load_ts = Image.open(f"../figures/time_series_plots/{plot_key}_time_series_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load_ts = load_ts.resize((int(fig_ts.get_figwidth() * 100),
                              int(fig_ts.get_figheight() * 80)))
    render_ts = ImageTk.PhotoImage(load_ts)
    img_ts = tk.Label(image=render_ts)
    img_ts.image = render_ts
    img_ts.grid(row=row, column=0, rowspan=3, columnspan=2, sticky="w")


def load_hist_plots(df_slice_sci=None, start_time=None, end_time=None, bins=None, cmin=None,
                    cmax=None, x_min=None, x_max=None, y_min=None, y_max=None, density=None,
                    norm=None, row=3
                    ):

    fig_hist = lgpr.plot_data_class(df_slice_sci=df_slice_sci, start_time=start_time,
                                    end_time=end_time, bins=bins, cmin=cmin, cmax=cmax,
                                    x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,
                                    density=density, norm=norm).hist_plots()

    load_hist = Image.open("../figures/hist_plots/hist_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load_hist = load_hist.resize((int(fig_hist.get_figwidth() * 100),
                                  int(fig_hist.get_figheight() * 100)))
    render_hist = ImageTk.PhotoImage(load_hist)
    img_hist = tk.Label(image=render_hist)
    img_hist.image = render_hist
    img_hist.grid(row=row, column=2, rowspan=12, columnspan=2, sticky="nsew")


def load_hist_plots_volt(df_slice_sci=None, start_time=None, end_time=None, channel1=None,
                         channel2=None, row=None, column=None, sticky=None):

    fig_hist = lgpr.plot_data_class(
        df_slice_sci=df_slice_sci, start_time=start_time, end_time=end_time, channel1=channel1,
        channel2=channel2).hist_plots_volt()

    load_hist = Image.open(f"../figures/hist_plots/hist_plot_{channel1}_{channel2}.png")
    # Resize the image to fit the canvas (in pixels)
    load_hist = load_hist.resize((int(fig_hist.get_figwidth() * 80),
                                  int(fig_hist.get_figheight() * 80)))
    render_hist = ImageTk.PhotoImage(load_hist)
    img_hist = tk.Label(image=render_hist)
    img_hist.image = render_hist
    img_hist.grid(row=row, column=column, rowspan=3, columnspan=1, sticky=sticky)


def load_all_hist_plots(
        df_slice_sci=None, start_time=None, end_time=None, bins=None, cmin=None, cmax=None,
        x_min=None, x_max=None, y_min=None, y_max=None, density=None, norm=None, row_hist=3,
        channel1=None, channel3=None, row_channel13=None, column_channel13=None,
        sticky_channel13=None,
        channel2=None, channel4=None, row_channel24=None, column_channel24=None,
        sticky_channel24=None
):

    load_hist_plots(df_slice_sci=df_slice_sci, start_time=start_time, end_time=end_time, bins=bins,
                    cmin=cmin, cmax=cmax, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,
                    density=density, norm=norm, row=row_hist)

    load_hist_plots_volt(df_slice_sci=df_slice_sci, start_time=start_time, end_time=end_time,
                         channel1=channel1, channel2=channel3, row=row_channel13,
                         column=column_channel13, sticky=sticky_channel13)

    load_hist_plots_volt(df_slice_sci=df_slice_sci, start_time=start_time, end_time=end_time,
                         channel1=channel2, channel2=channel4, row=row_channel24,
                         column=column_channel24, sticky=sticky_channel24)


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

# Add a scrollbar")


def populate(frame):
    '''Put in some fake data'''
    for row in range(100):
        tk.Label(frame, text="%s" % row, width=3, borderwidth="1",
                 relief="solid").grid(row=row, column=0)
        t = "this is the second column for row %s" % row
        tk.Label(frame, text=t).grid(row=row, column=1)


def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))


canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
frame = tk.Frame(canvas, background="#ffffff")
vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)
vsb.grid(row=0, column=6, sticky="ns")
canvas.grid(row=0, column=0, columnspan=6, rowspan=19, sticky="nsew")
#vsb.pack(side="right", fill="y")
#canvas.pack(side="left", fill="both", expand=True)
#canvas.create_window((4, 4), window=frame, anchor="nw")

frame.bind("<Configure>", lambda event,
           canvas=canvas: onFrameConfigure(canvas))

#populate(frame)

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
ts_menu_2.grid(row=7, column=1, columnspan=1, sticky="w")

#plot_opt_label_3 = tk.Label(root, text="Plot options:", font=font_style_box)
#plot_opt_label_3.grid(row=9, column=0, columnspan=1, pady=0, sticky="w")
plot_opt_entry_3 = tk.StringVar(root)
plot_opt_entry_3.set("Select a column")
ts_menu_3 = tk.OptionMenu(root, plot_opt_entry_3, *ts_options)
ts_menu_3.grid(row=11, column=1, columnspan=1, sticky="w")

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

#print(global_variables.all_file_details)
# if any of the ts_options are changed, update the plot
#lgpr.plot_data_class.__init__()
plot_opt_entry_1.trace(
    "w", lambda *_: load_ts_plots(
        df_slice_hk=global_variables.all_file_details["df_slice_hk"],
        plot_key=plot_opt_entry_1.get(), start_time=start_time.get(),
        end_time=end_time.get(), row=4)
)

plot_opt_entry_2.trace(
    "w", lambda *_: load_ts_plots(
        df_slice_hk=global_variables.all_file_details["df_slice_hk"],
        plot_key=plot_opt_entry_2.get(), start_time=start_time.get(),
        end_time=end_time.get(), row=8)
)

plot_opt_entry_3.trace(
    "w", lambda *_: load_ts_plots(
        df_slice_hk=global_variables.all_file_details["df_slice_hk"],
        plot_key=plot_opt_entry_3.get(), start_time=start_time.get(),
        end_time=end_time.get(), row=12)
)

plot_button = tk.Button(root, text="Plot Histogram", font=font_style_box, justify="center",
                        command=lambda: load_all_hist_plots(
                            df_slice_sci=global_variables.all_file_details["df_slice_sci"],
                            start_time=start_time.get(), end_time=end_time.get(),
                            bins=hist_bins_entry.get(), cmin=c_min_entry.get(),
                            cmax=c_max_entry.get(), x_min=x_min_entry.get(),
                            x_max=x_max_entry.get(), y_min=y_min_entry.get(),
                            y_max=y_max_entry.get(), density=density_entry.get(),
                            norm=norm_entry.get(), row_hist=1,
                            channel1="Channel1", channel2="Channel2", row_channel13=12,
                            column_channel13=2, sticky_channel13="ne",
                            channel3="Channel3", channel4="Channel4", row_channel24=12,
                            column_channel24=3, sticky_channel24="nw"
                        )
                        )

plot_button.grid(row=0, column=2, columnspan=2, rowspan=1)
# Add a button to the window to get start time
#start_button = tk.Button(root, text="Start", command=lambda: print("Start"))
#start_button.grid(row=13, column=3, columnspan=1)

# Add a quit button
quit_button = tk.Button(
    root, text="Quit", command=root.destroy, font=font_style_box, justify="center")
quit_button.grid(row=10, column=4, columnspan=2, rowspan=2)
# Print the value in the entry box

root.mainloop()
