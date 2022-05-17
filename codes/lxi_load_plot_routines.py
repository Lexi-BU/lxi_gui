import importlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec

from PIL import Image, ImageTk

import global_variables
import lxi_gui_plot_routines as lgpr
import lxi_read_files as lxrf
import matplotlib.pyplot as plt

importlib.reload(lgpr)
importlib.reload(lxrf)
importlib.reload(global_variables)

global_variables.init()


def load_ts_plots(root=None, df_slice_hk=None, plot_key=None, start_time=None, end_time=None, row=2,
                  column=1, columnspan=2, rowspan=2, fig_width=None, fig_height=None):
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
    # Set the fontstyle to Times New Roman
    font_mpl = {'family': 'serif', 'weight': 'normal'}
    plt.rc('font', **font_mpl)
    plt.rc('text', usetex=False)

    frame = tk.Frame(root)
    frame.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky='nsew')

    fig_ts = lgpr.plot_data_class(df_slice_hk=df_slice_hk, plot_key=plot_key, start_time=start_time,
                                  end_time=end_time, ts_fig_height=fig_height,
                                  ts_fig_width=fig_width).ts_plots()
    canvas = FigureCanvasTkAgg(fig_ts, master=frame)
    canvas.get_tk_widget().pack(side="left", fill='both', expand=False)
    canvas.draw()
    canvas.get_tk_widget().pack(side='left', fill='both', expand=False)


def load_hist_plots(root=None, df_slice_sci=None, start_time=None, end_time=None, bins=None, cmin=None,
                    cmax=None, x_min=None, x_max=None, y_min=None, y_max=None, density=None,
                    norm=None, row=3, column=1, fig_width=5, fig_height=5, columnspan=2, rowspan=2
                    ):
    """
    Loads the histogram plots for the selected time range and displays them in the GUI.

    Parameters
    ----------
    df_slice_sci : pandas.DataFrame
        The dataframe containing the science data.
    start_time : str
        The start time of the time range to be plotted.
    end_time : str
        The end time of the time range to be plotted.
    bins : int
        The number of bins to be used for the histogram.
    cmin : int
        The minimum value of the colorbar.
    cmax : int
        The maximum value of the colorbar.
    x_min : int
        The minimum value of the x-axis.
    x_max : int
        The maximum value of the x-axis.
    y_min : int
        The minimum value of the y-axis.
    y_max : int
        The maximum value of the y-axis.
    density : bool
        Whether or not the histogram should be normalized.
    norm : bool
        Whether or not the histogram should be normalized.
    row : int
        The row in which the plots should be displayed.
    column : int
        The column in which the plots should be displayed.

    Returns
    -------
    None
    """
    # Set the fontstyle to Times New Roman
    font_mpl = {'family': 'serif', 'weight': 'normal'}
    plt.rc('font', **font_mpl)
    plt.rc('text', usetex=False)

    fig_hist = lgpr.plot_data_class(df_slice_sci=df_slice_sci, start_time=start_time,
                                    end_time=end_time, bins=bins, cmin=cmin, cmax=cmax,
                                    x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,
                                    density=density, norm=norm, hist_fig_height=fig_height,
                                    hist_fig_width=fig_width).hist_plots()

    frame = tk.Frame(root)
    frame.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky='nsew')
    canvas = FigureCanvasTkAgg(fig_hist, master=frame)
    canvas.get_tk_widget().pack(side="left", fill='both', expand=True)
    canvas.draw()
    canvas.get_tk_widget().pack(side='left', fill='both', expand=True)
    #load_hist = Image.open("../figures/hist_plots/hist_plot.png")
    ## Resize the image to fit the canvas (in pixels)
    #load_hist = load_hist.resize((int(fig_hist.get_figwidth() * 100),
    #                              int(fig_hist.get_figheight() * 100)))
    #render_hist = ImageTk.PhotoImage(load_hist)
    #img_hist = tk.Label(master=root, image=render_hist)
    #img_hist.image = render_hist
    #img_hist.grid(row=row, column=column, rowspan=4, columnspan=2, sticky="nsew")
    #print(fig_hist.get_figwidth(), load_hist.size)


def load_hist_plots_volt(root=None, df_slice_sci=None, start_time=None, end_time=None, channel1=None,
                         channel2=None, row=None, column=None, sticky=None):
    """
    Loads the histogram plots for the selected time range and displays them in the GUI. This is for
    the voltage

    Parameters
    ----------
    df_slice_sci : pandas.DataFrame
        The dataframe containing the science data.
    start_time : str
        The start time of the time range to be plotted.
    end_time : str
        The end time of the time range to be plotted.
    channel1 : str
        The channel to be plotted.
    channel2 : str
        The channel to be plotted.
    row : int
        The row in which the plots should be displayed.
    column : int
        The column in which the plots should be displayed.
    sticky : str
        The sticky parameter for the grid.

    Returns
    -------
    None
    """
    # Set the fontstyle to Times New Roman
    font_mpl = {'family': 'serif', 'weight': 'normal', 'size': 10}
    plt.rc('font', **font_mpl)
    plt.rc('text', usetex=False)

    fig_hist = lgpr.plot_data_class(
        df_slice_sci=df_slice_sci, start_time=start_time, end_time=end_time, channel1=channel1,
        channel2=channel2).hist_plots_volt()

    load_hist = Image.open(
        f"../figures/hist_plots/hist_plot_{channel1}_{channel2}.png")
    # Resize the image to fit the canvas (in pixels)
    load_hist = load_hist.resize((int(fig_hist.get_figwidth() * 80),
                                  int(fig_hist.get_figheight() * 80)))
    render_hist = ImageTk.PhotoImage(load_hist)
    img_hist = tk.Label(master=root, image=render_hist)
    img_hist.image = render_hist
    img_hist.grid(row=row, column=column, rowspan=3,
                  columnspan=1, sticky=sticky)


def load_all_hist_plots(
        root=None, df_slice_sci=None, start_time=None, end_time=None, bins=None, cmin=None,
        cmax=None, x_min=None, x_max=None, y_min=None, y_max=None, density=None, norm=None,
        row_hist=3, col_hist=1, channel1=None, channel3=None, row_channel13=None, column_channel13=None,
        sticky_channel13=None, channel2=None, channel4=None, row_channel24=None,
        column_channel24=None, sticky_channel24=None, hist_fig_height=None, hist_fig_width=None,
        hist_colspan=None, hist_rowspan=None
):
    """
    Loads the histogram plots for the selected time range and displays them in the GUI. This is for
    the voltage as well as the x,y locations of the photons

    Parameters
    ----------
    df_slice_sci : pandas.DataFrame
        The dataframe containing the science data.
    start_time : str
        The start time of the time range to be plotted.
    end_time : str
        The end time of the time range to be plotted.
    bins : int
        The number of bins to be used for the histogram.
    cmin : int
        The minimum value of the colorbar.
    cmax : int
        The maximum value of the colorbar.
    x_min : int
        The minimum value of the x-axis.
    x_max : int
        The maximum value of the x-axis.
    y_min : int
        The minimum value of the y-axis.
    y_max : int
        The maximum value of the y-axis.
    density : bool
        Whether or not the histogram should be normalized.
    norm : bool
        Whether or not the histogram should be normalized.
    row_hist : int
        The row in which the histogram plots should be displayed.
    channel1 : str
        The channel to be plotted.
    channel3 : str
        The channel to be plotted.
    row_channel13 : int
        The row in which the histogram plots should be displayed.
    column_channel13 : int
        The column in which the histogram plots should be displayed.
    sticky_channel13 : str
        The sticky parameter for the grid.
    channel2 : str
        The channel to be plotted.
    channel4 : str
        The channel to be plotted.
    row_channel24 : int
        The row in which the histogram plots should be displayed.
    column_channel24 : int
        The column in which the histogram plots should be displayed.
    sticky_channel24 : str
        The sticky parameter for the grid.

    Returns
    -------
        None
    """
    load_hist_plots(root=root[0], df_slice_sci=df_slice_sci, start_time=start_time,
                    end_time=end_time, bins=bins, cmin=cmin, cmax=cmax, x_min=x_min, x_max=x_max,
                    y_min=y_min, y_max=y_max, density=density, norm=norm, row=row_hist,
                    column=col_hist, fig_height=hist_fig_height, fig_width=hist_fig_width,
                    columnspan=hist_colspan, rowspan=hist_rowspan)

    load_hist_plots_volt(root=root[1], df_slice_sci=df_slice_sci, start_time=start_time,
                         end_time=end_time, channel1=channel1, channel2=channel3,
                         row=row_channel13, column=column_channel13, sticky=sticky_channel13)

    load_hist_plots_volt(root=root[1], df_slice_sci=df_slice_sci, start_time=start_time,
                         end_time=end_time, channel1=channel2, channel2=channel4, row=row_channel24,
                         column=column_channel24, sticky=sticky_channel24)
