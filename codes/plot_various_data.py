import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class plot_diff_data():

    def __init__(self, file_name_sci, file_name_hk, start_time, end_time) -> None:
        self.file_name_sci = file_name_sci
        self.file_name_hk = file_name_hk
        self.start_time = start_time
        self.end_time = end_time


    def ts_plots(self):
        """
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

