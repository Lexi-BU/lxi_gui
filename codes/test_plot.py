import importlib
import platform
import tkinter as tk
from tkinter import font, ttk

import global_variables
import lxi_gui_entry_box as lgeb
import lxi_gui_plot_routines as lgpr
import lxi_load_plot_routines as llpr
import lxi_misc_codes as lmsc
import lxi_file_read_funcs as lxrf
import lxi_csv_to_cdf as lctc

importlib.reload(lgpr)
importlib.reload(lxrf)
importlib.reload(global_variables)
importlib.reload(llpr)
importlib.reload(lgeb)
importlib.reload(lmsc)
importlib.reload(lctc)

df_sci = global_variables.all_file_details["df_slice_sci"]

fig_hist = lgpr.plot_data_class(
        df_slice_sci=df_sci, bins=200, cmin=1,
        cmax=None, density=False, norm="linear", channel1=0, channel2=5,
        volt_fig_width=10, volt_fig_height=10, v_min=5, v_max=7
    ).hist_plots_volt()
