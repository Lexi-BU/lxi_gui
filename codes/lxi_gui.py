import importlib
import tkinter as tk
from tkinter import font, ttk

import global_variables
import lxi_gui_entry_box as lgeb
import lxi_gui_plot_routines as lgpr
import lxi_load_plot_routines as llpr
import lxi_read_files as lxrf
import lxi_misc_codes as lmsc

importlib.reload(lgpr)
importlib.reload(lxrf)
importlib.reload(global_variables)
importlib.reload(llpr)
importlib.reload(lgeb)
importlib.reload(lmsc)

# Initialize the global variables. This is necessary because the global variables is where all the
# data and name of the files are stored.
global_variables.init()


def hist_plot_inputs():
    """
    The function creates and updates the list of widget inputs as might be available from the GUI.
    """

    inputs = {
        "root": [frame_sci, frame_sci],
        "df_slice_sci": global_variables.all_file_details["df_slice_sci"],
        "start_time": start_time.get(),
        "end_time": end_time.get(),
        "bins": hist_bins_entry.get(),
        "cmin": c_min_entry.get(),
        "cmax": c_max_entry.get(),
        "x_min": x_min_entry.get(),
        "x_max": x_max_entry.get(),
        "y_min": y_min_entry.get(),
        "y_max": y_max_entry.get(),
        "density": density_status_var.get(),
        "norm": norm_type_var.get(),
        "row_hist": 0,
        "col_hist": 2,
        "channel1": "Channel1",
        "channel2": "Channel2",
        "row_channel13": 0,
        "column_channel13": 7,
        "sticky_channel13": "nesw",
        "row_span_channel13": 5,
        "column_span_channel13": 3,
        "channel3": "Channel3",
        "channel4": "Channel4",
        "row_channel24": 5,
        "column_channel24": 7,
        "sticky_channel24": "nesw",
        "row_span_channel24": 6,
        "column_span_channel24": 3,
        "hist_fig_height": screen_height / (1.1 * 96),
        "hist_fig_width": screen_width / (2 * 96),
        "hist_colspan": 2,
        "hist_rowspan": 12,
        "channel13_fig_height": screen_height / (3 * 96),
        "channel13_fig_width": screen_width / (3 * 96),
        "channel24_fig_height": screen_height / (3 * 96),
        "channel24_fig_width": screen_width / (3 * 96),
        "v_min": v_min_thresh_entry.get(),
        "v_max": v_max_thresh_entry.get(),
        "crv_fit": curve_fit_status_var.get()
    }

    llpr.load_all_hist_plots(**inputs)


def ts_plot_inputs(plot_opt_entry=None, row=None, column=None, columnspan=3, rowspan=2):

    inputs = {
        "root": hk_tab,
        "df_slice_hk": global_variables.all_file_details["df_slice_hk"],
        "plot_key": plot_opt_entry.get(),
        "start_time": start_time.get(),
        "end_time": end_time.get(),
        "row": row,
        "column": column,
        "columnspan": columnspan,
        "rowspan": rowspan,
        "fig_width": screen_width / (4 * 96),
        "fig_height": screen_height / (18 * 96)
    }

    llpr.load_ts_plots(**inputs)


# Create the main window.
root = tk.Tk()

# Get the screen width and height.
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()

#screen_width = 1200
#screen_height = 800

# Set the title of the main window.
root.title("LEXI GUI")
# Add the lxi logo
# root.iconbitmap("../figures/lxi_icon.ico")
# root.geometry("1100x700")
# set size of you window here is example for 1/2 screen height and width
root.geometry(f"{int(screen_width * 1.1)}x{int(screen_height * 1)}")

root.resizable(True, True)

tabControl = ttk.Notebook(root)
tabControl.pack(expand=1, fill="both")
# tabControl.grid(row=0, column=0, columnspan=16, rowspan=18, sticky="nsew")
tabControl.pack(expand=1, fill="both")
sci_tab = tk.Frame(tabControl)
sci_tab.pack(expand=1, fill="both")
hk_tab = tk.Frame(tabControl)
hk_tab.pack(expand=1, fill="both")

tabControl.add(sci_tab, text='Science Stuff')
tabControl.add(hk_tab, text='Housekeeping Stuff')

# Add a canvas to the science tab.
canvas_sci = tk.Canvas(sci_tab, width=screen_width, height=screen_height)
canvas_sci.pack(expand=1, fill="both")

# Add scroll bars to the science tab, and make sure it is always visible.
scroll_y_sci = ttk.Scrollbar(sci_tab, orient="vertical", command=canvas_sci.yview,
                             takefocus=True, cursor="hand2")

# Pack the scroll bars and make sure it is on the top of the canvas.
scroll_y_sci.pack(side="right", fill="y")
scroll_x_sci = ttk.Scrollbar(sci_tab, orient="horizontal", command=canvas_sci.xview,
                             takefocus=True, cursor="hand2")
scroll_x_sci.pack(side="bottom", fill="x")

# Configure the canvas to use the scroll bars.
canvas_sci.configure(yscrollcommand=scroll_y_sci.set, xscrollcommand=scroll_x_sci.set)
canvas_sci.bind("<Configure>",
                lambda event, canvas_sci=canvas_sci: canvas_sci.configure(
                    scrollregion=canvas_sci.bbox("all")))

# Create the frame for the science tab.
frame_sci = tk.Frame(canvas_sci)

canvas_sci.create_window((0, 0), window=frame_sci, anchor="nw")

# Configure the science tab rows and columns.
frame_sci.columnconfigure(0, {'minsize': 1}, weight=1)
frame_sci.columnconfigure(1, {'minsize': 1}, weight=2)
frame_sci.columnconfigure(2, {'minsize': 1}, weight=3)
frame_sci.columnconfigure(3, {'minsize': 1}, weight=3)
frame_sci.columnconfigure(4, {'minsize': 1}, weight=1)
frame_sci.columnconfigure(5, {'minsize': 1}, weight=1)

# Configure the housekeeping tab rows and columns.
hk_tab.columnconfigure(0, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(1, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(2, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(3, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(4, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(5, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(6, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(7, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(8, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(9, {'minsize': 1}, weight=1)
hk_tab.columnconfigure(10, {'minsize': 1}, weight=1)

hk_tab.rowconfigure(0, {'minsize': 1}, weight=1)
hk_tab.rowconfigure(1, {'minsize': 1}, weight=1)
hk_tab.rowconfigure(2, {'minsize': 1}, weight=1)
hk_tab.rowconfigure(3, {'minsize': 1}, weight=1)
hk_tab.rowconfigure(4, {'minsize': 1}, weight=1)
hk_tab.rowconfigure(5, {'minsize': 1}, weight=1)


# Choose a font style for GUI
font_style = font.Font(family="serif", size=12)
font_style_box = font.Font(family="serif", size=12, weight="bold")
font_style_big = font.Font(family="serif", size=25)


# Insert a file load button
# For science file
sci_file_load_button = tk.Button(frame_sci, text="Load Science File", command=lxrf.open_file_sci,
                                 font=font_style)
sci_file_load_button.grid(row=0, column=0, columnspan=1, pady=0, sticky="ew")

sci_file_load_entry = tk.Entry(frame_sci, font=font_style, justify="left", bg="white",
                               fg="black", relief="flat", borderwidth=2)
sci_file_load_entry.grid(row=1, column=0, columnspan=2, pady=0, sticky="ew")

# insert the file_load_entry value into the entry box only if the sci_file_load_button is clicked
sci_file_load_button.config(
    command=lambda: sci_file_load_entry.insert(0, lxrf.open_file_sci()))

# For housekeeping file
hk_file_load_button = tk.Button(frame_sci, text="Load HK File", command=lxrf.open_file_hk,
                                font=font_style)
hk_file_load_button.grid(row=2, column=0, columnspan=1, pady=0, sticky="ew")
hk_file_load_entry = tk.Entry(frame_sci, font=font_style, justify="left", bg="white",
                              fg="black", relief="flat", borderwidth=2)
hk_file_load_entry.grid(row=3, column=0, columnspan=2, pady=0, sticky="ew")
# insert the file_load_entry value into the entry box only if the hk_file_load_button is clicked
hk_file_load_button.config(
    command=lambda: hk_file_load_entry.insert(0, lxrf.open_file_hk()))

# For binary file
b_file_load_button = tk.Button(frame_sci, text="Load binary File", command=lxrf.open_file_b,
                               font=font_style)
b_file_load_button.grid(row=4, column=0, columnspan=1, pady=0, sticky="ew")
b_file_load_entry = tk.Entry(frame_sci, font=font_style, justify="left", bg="white",
                             fg="black", relief="flat", borderwidth=2)
b_file_load_entry.grid(row=5, column=0, columnspan=1, pady=0, sticky="ew")
# insert the file_load_entry value into the entry box only if the b_file_load_button is clicked
b_file_load_button.config(
    command=lambda: b_file_load_entry.insert(0, lxrf.open_file_b()))

# If a new file is loaded, then print its name in the entry box.
sci_file_load_button.bind("<Button-1>", lambda event: lmsc.insert_file_name(
    file_load_entry=sci_file_load_entry, tk=tk, file_name=lxrf.open_file_sci()))
hk_file_load_button.bind("<Button-1>", lambda event: lmsc.insert_file_name(
    file_load_entry=hk_file_load_entry, tk=tk, file_name=lxrf.open_file_hk()))
b_file_load_button.bind("<Button-1>", lambda event: lmsc.insert_file_name(
    file_load_entry=b_file_load_entry, tk=tk, file_name=lxrf.open_file_b()))

# If the global_variables.all_file_details["df_slice_hk"] is not empty, then set the comlumn names
# to the columns in the dataframe
if bool("df_slice_hk" in global_variables.all_file_details.keys()):
    ts_options = global_variables.all_file_details["df_slice_hk"].columns.tolist()
else:
    ts_options = ['HK_id', 'PinPullerTemp', 'OpticsTemp', 'LEXIbaseTemp', 'HVsupplyTemp',
                  '+5.2V_Imon', '+10V_Imon', '+3.3V_Imon', 'AnodeVoltMon', '+28V_Imon',
                  'ADC_Ground', 'Cmd_count', 'Pinpuller_Armed', 'HVmcpAuto', 'HVmcpMan',
                  'DeltaEvntCount', 'DeltaDroppedCount', 'DeltaLostevntCount']

# Plot options for the first plot
plot_opt_label_1 = tk.Label(hk_tab, text="Plot options:", font=font_style_box)
plot_opt_label_1.grid(row=0, column=0, columnspan=1, pady=0, sticky="w")
plot_opt_entry_1 = tk.StringVar(hk_tab)
plot_opt_entry_1.set("Select a column")
ts_menu_1 = tk.OptionMenu(hk_tab, plot_opt_entry_1, *ts_options)
ts_menu_1.grid(row=0, column=2, columnspan=1, sticky="w")

# Plot options for the second plot
plot_opt_entry_2 = tk.StringVar(hk_tab)
plot_opt_entry_2.set("Select a column")
ts_menu_2 = tk.OptionMenu(hk_tab, plot_opt_entry_2, *ts_options)
ts_menu_2.grid(row=0, column=5, columnspan=1, sticky="w")

# Plot optiosn for third plot
plot_opt_entry_3 = tk.StringVar(hk_tab)
plot_opt_entry_3.set("Select a column")
ts_menu_3 = tk.OptionMenu(hk_tab, plot_opt_entry_3, *ts_options)
ts_menu_3.grid(row=0, column=8, columnspan=1, sticky="w")

# The minimum value of x-axis for histogram plot
x_min_entry = lgeb.entry_box(root=frame_sci, row=0, column=4, entry_label="X-min", entry_val=0.40,
                             font_style=font_style_box)

# The maximum value of x-axis for histogram plot
x_max_entry = lgeb.entry_box(root=frame_sci, row=1, column=4, entry_label="X-max", entry_val=0.54,
                             font_style=font_style_box)

# The minimum value of y-axis for histogram plot
y_min_entry = lgeb.entry_box(root=frame_sci, row=2, column=4, entry_label="Y-min", entry_val=0.45,
                             font_style=font_style_box)

# The maximum value of y-axis for histogram plot
y_max_entry = lgeb.entry_box(root=frame_sci, row=3, column=4, entry_label="Y-max", entry_val=0.58,
                             font_style=font_style_box)

# The number of bins for histogram plot
hist_bins_entry = lgeb.entry_box(root=frame_sci, row=4, column=4, entry_label="Bins", entry_val=400,
                                 font_style=font_style_box)

# Mimimum number of data points in each bin for the histogram plot
c_min_entry = lgeb.entry_box(root=frame_sci, row=5, column=4, entry_label="C Min", entry_val=10,
                             font_style=font_style_box)

# Maximum number of data points in each bin for the histogram plot
c_max_entry = lgeb.entry_box(root=frame_sci, row=6, column=4, entry_label="C Max", entry_val="None",
                             font_style=font_style_box)

# Choose whether to plot probability density or the number of data points in each bin (is Bool)
density_label = tk.Label(frame_sci, text="Density", font=font_style_box)
density_label.grid(row=7, column=5, columnspan=1, sticky="n")

# Add a checkbox to choose whether to plot probability density or the number of data points in each
# bin
density_status_var = tk.BooleanVar()
density_status_var.set(False)
density_checkbox = tk.Checkbutton(frame_sci, text="", font=font_style_box,
                                  variable=density_status_var)
density_checkbox.grid(row=7, column=4, columnspan=1, sticky="n")

# Redo the histogram plot if the status of the checkbox is changed
density_status_var.trace("w", lambda *_: hist_plot_inputs())

# Key for the norm of the colorbar
norm_label = tk.Label(frame_sci, text="Norm", font=font_style_box)
norm_label.grid(row=8, column=5, columnspan=1, sticky="n")

# Add radio button for the norm type (default is 'log', other option is 'linear')
norm_type_var = tk.StringVar()
norm_type_var.set("log")
norm_type_1 = tk.Radiobutton(frame_sci, text="Log", variable=norm_type_var, value="log")
norm_type_1.grid(row=8, column=4, columnspan=1, sticky="new")
norm_type_2 = tk.Radiobutton(frame_sci, text="Linear", variable=norm_type_var, value="linear")
norm_type_2.grid(row=9, column=4, columnspan=1, sticky="new")

# Redo the histogram plot when the norm type is changed
norm_type_var.trace("w", lambda *_: hist_plot_inputs())

# Minimum threshold for the voltage to be considered
v_min_thresh_entry = lgeb.entry_box(root=frame_sci, row=10, column=4, entry_label="V Min",
                                    entry_val=1.6, font_style=font_style_box)

# Maximum threshold for the voltage to be considered
v_max_thresh_entry = lgeb.entry_box(root=frame_sci, row=11, column=4, entry_label="V Max",
                                    entry_val=3.6, font_style=font_style_box)


# Choose whether to plot probability density or the number of data points in each bin (is Bool)
curve_fit_label = tk.Label(frame_sci, text="Curve Fit", font=font_style_box)
curve_fit_label.grid(row=12, column=5, columnspan=1, sticky="n")

# Add a checkbox to choose whether to plot probability density or the number of data points in each
# bin
curve_fit_status_var = tk.BooleanVar()
curve_fit_status_var.set(False)
curve_fit_checkbox = tk.Checkbutton(frame_sci, text="", font=font_style_box,
                                    variable=curve_fit_status_var)
curve_fit_checkbox.grid(row=12, column=4, columnspan=1, sticky="n")

curve_fit_status_var.trace("w", lambda *_: hist_plot_inputs())

# Add an input box with a label for start time
start_time = tk.Entry(frame_sci, justify="center", bg="white", fg="black", borderwidth=2)
start_time.insert(0, "YYYY-MM-DD HH:MM:SS")
start_time.grid(row=6, column=0, columnspan=2)
start_time_label = tk.Label(frame_sci, text="Start Time", font=font_style)
start_time_label.grid(row=7, column=0, columnspan=2)

# Add an input box with a label for end time
# end_time_entry, end_time_label = lgeb.entry_box(root=frame_sci, row=17, column=3,
#                                                 entry_label="End Time", width=30,
#                                                 entry_val="YYYY-MM-DD HH:MM:SS",
#                                                 font_style=font_style)
end_time = tk.Entry(frame_sci, justify="center", bg="white", fg="black", borderwidth=2)
end_time.insert(0, "YYYY-MM-DD HH:MM:SS")
end_time.grid(row=8, column=0, columnspan=2)
end_time_label = tk.Label(frame_sci, text="End Time", font=font_style)
end_time_label.grid(row=9, column=0, columnspan=2)

# If the start time or end time is changed, print the value of the start time or end time
# start_time.bind("<KeyRelease>", lambda event: print(start_time.get()))
# end_time.bind("<KeyRelease>", lambda event: sleep(1))
# end_time.bind("<KeyRelease>", lambda event: lmsc.print_time_details(start_time=start_time.get(),
# end_time=end_time.get()))

# if any of the ts_options are changed, update the plot
plot_opt_entry_1.trace(
    "w", lambda *_: ts_plot_inputs(plot_opt_entry=plot_opt_entry_1, row=1, column=0, rowspan=1,
                                   columnspan=3))

plot_opt_entry_2.trace(
    "w", lambda *_: ts_plot_inputs(plot_opt_entry=plot_opt_entry_2, row=1, column=3, rowspan=1,
                                   columnspan=3))

plot_opt_entry_3.trace(
    "w", lambda *_: ts_plot_inputs(plot_opt_entry=plot_opt_entry_3, row=1, column=6, rowspan=1,
                                   columnspan=3))

# If the plot button is pressed then all the histogram plots are redrawn
plot_button = tk.Button(frame_sci, text="Plot Histogram", font=font_style_box, justify="center",
                        command=lambda: hist_plot_inputs())

plot_button.grid(row=10, column=0, columnspan=2, rowspan=1, sticky="nsew", pady=5, padx=5)

# If the plot button is pressed, then print the current time
plot_button.bind("<Button-1>", lambda event: lmsc.print_time_details(start_time=start_time.get(),
                                                                     end_time=end_time.get()))

# Add a quit button
quit_button_sci = tk.Button(
    frame_sci, text="Quit", command=root.destroy, font=font_style_box, justify="center")
quit_button_sci.grid(row=11, column=0, columnspan=2, rowspan=2)

quit_button_hk = tk.Button(
    hk_tab, text="Quit", command=root.destroy, font=font_style_box, justify="center")
quit_button_hk.grid(row=11, column=3, columnspan=2, rowspan=2)

root.mainloop()
