import importlib
import tkinter as tk
from tkinter import font

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

# Create the main window.
root = tk.Tk()

# Set the number of columns for the main window.
root.columnconfigure(0, {'minsize': 3}, weight=1)
root.columnconfigure(1, {'minsize': 3}, weight=2)
root.columnconfigure(2, {'minsize': 3}, weight=3)
root.columnconfigure(3, {'minsize': 3}, weight=3)
root.columnconfigure(4, {'minsize': 3}, weight=1)
root.columnconfigure(5, {'minsize': 3}, weight=1)


# Set the title of the main window.
root.title("LEXI GUI")
# Add the lxi logo
# img = tk.PhotoImage(file="../../figures/lxi_gui_figures/lxi_icon.ico")
# root.tk.call('wm', 'iconphoto', root._w, img)
# root.iconbitmap("../../figures/lxi_gui_figures/lxi_icon.ico")
root.geometry("600x600")
root.resizable(True, True)

# Add a scrollbar
scrollbar = tk.Scrollbar(root)
scrollbar.grid(row=0, column=6, rowspan=12, sticky="nsew")

# Choose a font style for GUI
font_style = font.Font(family="Helvetica", size=12)
font_style_box = font.Font(family="Helvetica", size=12, weight="bold")
font_style_big = font.Font(family="Helvetica", size=25)

# Insert a file load button
# For science file
sci_file_load_button = tk.Button(root, text="Load Science File",
                                 command=lambda: lxrf.open_file_sci(start_time=start_time.get(),
                                                                    end_time=end_time.get()),
                                 font=font_style)
sci_file_load_button.grid(row=0, column=0, columnspan=1, pady=0, sticky="ew")

sci_file_load_entry = tk.Entry(root, font=font_style, width=30, justify="left", bg="white",
                               fg="black", relief="flat", borderwidth=2)
sci_file_load_entry.grid(row=0, column=1, columnspan=4, pady=0, sticky="w")

# insert the file_load_entry value into the entry box only if the sci_file_load_button is clicked
sci_file_load_button.config(command=lambda: sci_file_load_entry.insert(0, lxrf.open_file_sci()))

# For housekeeping file
hk_file_load_button = tk.Button(root, text="Load HK File", command=lxrf.open_file_hk,
                                font=font_style)
hk_file_load_button.grid(row=1, column=0, columnspan=1, pady=0, sticky="ew")
hk_file_load_entry = tk.Entry(root, font=font_style, width=30, justify="left", bg="white",
                              fg="black", relief="flat", borderwidth=2)
hk_file_load_entry.grid(row=1, column=1, columnspan=4, pady=0, sticky="w")
# insert the file_load_entry value into the entry box only if the hk_file_load_button is clicked
hk_file_load_button.config(command=lambda: hk_file_load_entry.insert(0, lxrf.open_file_hk()))

# For binary file
b_file_load_button = tk.Button(root, text="Load binary File", command=lxrf.open_file_b,
                               font=font_style)
b_file_load_button.grid(row=2, column=0, columnspan=1, pady=0, sticky="ew")
b_file_load_entry = tk.Entry(root, font=font_style, width=30, justify="left", bg="white",
                             fg="black", relief="flat", borderwidth=2)
b_file_load_entry.grid(row=2, column=1, columnspan=4, pady=0, sticky="w")
# insert the file_load_entry value into the entry box only if the b_file_load_button is clicked
b_file_load_button.config(command=lambda: b_file_load_entry.insert(0, lxrf.open_file_b()))

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
plot_opt_label_1 = tk.Label(root, text="Plot options:", font=font_style_box)
plot_opt_label_1.grid(row=3, column=0, columnspan=1, pady=0, sticky="w")
plot_opt_entry_1 = tk.StringVar(root)
plot_opt_entry_1.set("Select a column")
ts_menu_1 = tk.OptionMenu(root, plot_opt_entry_1, *ts_options)
ts_menu_1.grid(row=3, column=1, columnspan=1, sticky="w")

# Plot options for the second plot
plot_opt_entry_2 = tk.StringVar(root)
plot_opt_entry_2.set("Select a column")
ts_menu_2 = tk.OptionMenu(root, plot_opt_entry_2, *ts_options)
ts_menu_2.grid(row=7, column=1, columnspan=1, sticky="w")

# Plot optiosn for third plot
plot_opt_entry_3 = tk.StringVar(root)
plot_opt_entry_3.set("Select a column")
ts_menu_3 = tk.OptionMenu(root, plot_opt_entry_3, *ts_options)
ts_menu_3.grid(row=11, column=1, columnspan=1, sticky="w")

# The minimum value of x-axis for histogram plot
x_min_entry = lgeb.entry_box(root=root, row=1, column=4, entry_label="X-min", entry_val=0,
                             font_style=font_style_box)

# The maximum value of x-axis for histogram plot
x_max_entry = lgeb.entry_box(root=root, row=2, column=4, entry_label="X-max", entry_val=1,
                             font_style=font_style_box)

# The minimum value of y-axis for histogram plot
y_min_entry = lgeb.entry_box(root=root, row=3, column=4, entry_label="Y-min", entry_val=0,
                             font_style=font_style_box)

# The maximum value of y-axis for histogram plot
y_max_entry = lgeb.entry_box(root=root, row=4, column=4, entry_label="Y-max", entry_val=1,
                             font_style=font_style_box)

# The number of bins for histogram plot
hist_bins_entry = lgeb.entry_box(root=root, row=5, column=4, entry_label="Bins", entry_val=50,
                                 font_style=font_style_box)

# Mimimum number of data points in each bin for the histogram plot
c_min_entry = lgeb.entry_box(root=root, row=6, column=4, entry_label="C Min", entry_val=1,
                             font_style=font_style_box)

# Maximum number of data points in each bin for the histogram plot
c_max_entry = lgeb.entry_box(root=root, row=7, column=4, entry_label="C Max", entry_val="None",
                             font_style=font_style_box)

# Choose whether to plot probability density or the number of data points in each bin (is Bool)
density_label = tk.Label(root, text="Density", font=font_style_box)
density_label.grid(row=8, column=5, columnspan=1, sticky="n")

# Add a checkbox to choose whether to plot probability density or the number of data points in each
# bin
density_status_var = tk.BooleanVar()
density_status_var.set(False)
density_checkbox = tk.Checkbutton(root, text="", font=font_style_box, variable=density_status_var)
density_checkbox.grid(row=8, column=4, columnspan=1, sticky="n")

# Redo the histogram plot if the status of the checkbox is changed
density_status_var.trace("w", lambda *_: llpr.load_all_hist_plots(
    df_slice_sci=global_variables.all_file_details["df_slice_sci"],
    start_time=start_time.get(), end_time=end_time.get(),
    bins=hist_bins_entry.get(), cmin=c_min_entry.get(),
    cmax=c_max_entry.get(), x_min=x_min_entry.get(),
    x_max=x_max_entry.get(), y_min=y_min_entry.get(),
    y_max=y_max_entry.get(), density=density_status_var.get(),
    norm=norm_type_var.get(), row_hist=1,
    channel1="Channel1", channel2="Channel2", row_channel13=12,
    column_channel13=2, sticky_channel13="ne",
    channel3="Channel3", channel4="Channel4", row_channel24=12,
    column_channel24=3, sticky_channel24="nw"
)
)

# Key for the norm of the colorbar
norm_label = tk.Label(root, text="Norm", font=font_style_box)
norm_label.grid(row=9, column=5, columnspan=1, sticky="n")

# Add radio button for the norm type (default is 'log', other option is 'linear')
norm_type_var = tk.StringVar()
norm_type_var.set("log")
norm_type_1 = tk.Radiobutton(root, text="Log", variable=norm_type_var, value="log")
norm_type_1.grid(row=9, column=4, columnspan=1, sticky="new")
norm_type_2 = tk.Radiobutton(root, text="Linear", variable=norm_type_var, value="linear")
norm_type_2.grid(row=10, column=4, columnspan=1, sticky="new")

# Redo the histogram plot when the norm type is changed
norm_type_var.trace("w", lambda *_: llpr.load_all_hist_plots(
    df_slice_sci=global_variables.all_file_details["df_slice_sci"],
    start_time=start_time.get(), end_time=end_time.get(),
    bins=hist_bins_entry.get(), cmin=c_min_entry.get(),
    cmax=c_max_entry.get(), x_min=x_min_entry.get(),
    x_max=x_max_entry.get(), y_min=y_min_entry.get(),
    y_max=y_max_entry.get(), density=density_status_var.get(),
    norm=norm_type_var.get(), row_hist=1,
    channel1="Channel1", channel2="Channel2", row_channel13=12,
    column_channel13=2, sticky_channel13="ne",
    channel3="Channel3", channel4="Channel4", row_channel24=12,
    column_channel24=3, sticky_channel24="nw"
)
)

# Add an input box with a label for start time
# start_time_entry, start_time_label = lgeb.entry_box(root=root, row=17, column=2,
#                                                    entry_label="Start Time", width=30,
#                                                    entry_val="YYYY-MM-DD HH:MM:SS",
#                                                    font_style=font_style)
start_time = tk.Entry(root, width=30, justify="center", bg="white", fg="black", borderwidth=2)
start_time.insert(0, "YYYY-MM-DD HH:MM:SS")
start_time.grid(row=17, column=2, columnspan=1, pady=5, ipadx=10, ipady=10)
start_time_label = tk.Label(root, text="Start Time", font=font_style)
start_time_label.grid(row=18, column=2, columnspan=1)

# Add an input box with a label for end time
# end_time_entry, end_time_label = lgeb.entry_box(root=root, row=17, column=3,
#                                                 entry_label="End Time", width=30,
#                                                 entry_val="YYYY-MM-DD HH:MM:SS",
#                                                 font_style=font_style)
end_time = tk.Entry(root, width=30, justify="center", bg="white", fg="black", borderwidth=2)
end_time.insert(0, "YYYY-MM-DD HH:MM:SS")
end_time.grid(row=17, column=3, columnspan=1, pady=5, ipadx=10, ipady=10)
end_time_label = tk.Label(root, text="End Time", font=font_style)
end_time_label.grid(row=18, column=3, columnspan=1)

# If the start time or end time is changed, print the value of the start time or end time
# start_time.bind("<KeyRelease>", lambda event: print(start_time.get()))
# end_time.bind("<KeyRelease>", lambda event: sleep(1))
# end_time.bind("<KeyRelease>", lambda event: lmsc.print_time_details(start_time=start_time.get(),
# end_time=end_time.get()))

# if any of the ts_options are changed, update the plot
plot_opt_entry_1.trace(
    "w", lambda *_: llpr.load_ts_plots(
        df_slice_hk=global_variables.all_file_details["df_slice_hk"],
        plot_key=plot_opt_entry_1.get(), start_time=start_time.get(),
        end_time=end_time.get(), row=4)
)

plot_opt_entry_2.trace(
    "w", lambda *_: llpr.load_ts_plots(
        df_slice_hk=global_variables.all_file_details["df_slice_hk"],
        plot_key=plot_opt_entry_2.get(), start_time=start_time.get(),
        end_time=end_time.get(), row=8)
)

plot_opt_entry_3.trace(
    "w", lambda *_: llpr.load_ts_plots(
        df_slice_hk=global_variables.all_file_details["df_slice_hk"],
        plot_key=plot_opt_entry_3.get(), start_time=start_time.get(),
        end_time=end_time.get(), row=12)
)

# If the plot button is pressed then all the histogram plots are redrawn
plot_button = tk.Button(root, text="Plot Histogram", font=font_style_box, justify="center",
                        command=lambda: llpr.load_all_hist_plots(
                            df_slice_sci=global_variables.all_file_details["df_slice_sci"],
                            start_time=start_time.get(), end_time=end_time.get(),
                            bins=hist_bins_entry.get(), cmin=c_min_entry.get(),
                            cmax=c_max_entry.get(), x_min=x_min_entry.get(),
                            x_max=x_max_entry.get(), y_min=y_min_entry.get(),
                            y_max=y_max_entry.get(), density=density_status_var.get(),
                            norm=norm_type_var.get(), row_hist=1,
                            channel1="Channel1", channel2="Channel2", row_channel13=12,
                            column_channel13=2, sticky_channel13="ne",
                            channel3="Channel3", channel4="Channel4", row_channel24=12,
                            column_channel24=3, sticky_channel24="nw"
                        )
                        )
plot_button.grid(row=0, column=2, columnspan=2, rowspan=1)

# If the plot button is pressed, then print the current time
plot_button.bind("<Button-1>", lambda event: lmsc.print_time_details(start_time=start_time.get(),
                                                                     end_time=end_time.get()))
# Add a quit button
quit_button = tk.Button(
    root, text="Quit", command=root.destroy, font=font_style_box, justify="center")
quit_button.grid(row=11, column=4, columnspan=2, rowspan=2)

root.mainloop()
