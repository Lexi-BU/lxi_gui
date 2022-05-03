import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import global_variables
import importlib

importlib.reload(global_variables)


class plot_diff_data():

    def __init__(self, file_name_bnr, file_name_sci, file_name_hk, start_time, end_time,
                 x_min_entry, x_max_entry, y_min_entry, y_max_entry, hist_bin_entry, c_min_entry,
                 c_max_entry, density_entry, norm_entry, plot_entry_1, key):
        self.file_name_bnr = file_name_bnr
        self.file_name_sci = file_name_sci
        self.file_name_hk = file_name_hk
        self.start_time = start_time
        self.end_time = end_time
        self.x_min_entry = x_min_entry
        self.x_max_entry = x_max_entry
        self.y_min_entry = y_min_entry
        self.y_max_entry = y_max_entry
        self.hist_bin_entry = hist_bin_entry
        self.c_min_entry = c_min_entry
        self.c_max_entry = c_max_entry
        self.density_entry = density_entry
        self.norm_entry = norm_entry
        self.plot_entry_1 = plot_entry_1
        self.key = key
        print(key)

    #@staticmethod
    def ts_plots_1(self):
        """
    

        # Try to convert the start_time and end_time to float or int
        try:
            t_start = float(self.start_time.get())
        except Exception as e:
            print(f"Error: {e}")
            pass
        try:
            t_end = float(self.end_time.get())
        except Exception as e:
            print(f"Error: {e}")
            pass
        if not isinstance(t_start, (int, float)):
            t_start = None

        if not isinstance(t_end, (int, float)):
            t_end = None
        """
        self.plot_entry_1 = plot_opt_entry_1.get()
        print(f"Hey...this code worked and key is {self.plot_entry_1}!")
        """

        df_slice_hk = read_csv_hk(file_val=file_name_hk, t_start=t_start, t_end=t_end)
        df_slice_sci = read_csv_sci(file_val=file_name_sci, t_start=t_start, t_end=t_end)
        df_slice_sci = df_slice_sci[df_slice_sci['IsCommanded']==False]

        # Display the time series plot
        fig1_ts = plot_routines.plot_indiv_time_series(df=df_slice_hk,
                                                       key=plot_opt_entry_1.get(), ms=2,
                                                       alpha=1)

        load1_ts = Image.open(f"figures/{plot_opt_entry_1.get()}_time_series_plot.png")
        # Resize the image to fit the canvas (in pixels)
        load1_ts = load1_ts.resize((int(fig1_ts.get_figwidth() * 100),
                                    int(fig1_ts.get_figheight() * 60)))
        render1_ts = ImageTk.PhotoImage(load1_ts)
        img1_ts = tk.Label(image=render1_ts)
        img1_ts.image = render1_ts
        img1_ts.grid(row=2, column=0, rowspan=3, columnspan=2, sticky="w")
        """
