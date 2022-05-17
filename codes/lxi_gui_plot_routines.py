import importlib
from pathlib import Path

import matplotlib as mpl
from matplotlib import legend_handler
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
# import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable

import global_variables

importlib.reload(global_variables)


class plot_data_class():
    """
    A class for plotting different kinds of data

    Attributes:
        df_slice_hk: pandas dataframe
            The dataframe containing the Housekeeping data. Once you upload an HK file to the GUI
            the dataframe is stored in a global variable called
            global_variables.all_file_details["df_slice_hk"] and corresponds to the value in the
            file which was loaded.
        df_slice_sci: pandas dataframe
            The dataframe containing the Science data. Once you upload an SCI file to the GUI
            the dataframe is stored in a global variable called
            global_variables.all_file_details["df_slice_sci"] and corresponds to the value in the
            file which was loaded.
        start_time: str
            The start time of the data to be plotted. By default this is the first time in the
            dataframe.
        end_time: str
            The end time of the data to be plotted. By default this is the last time in the
            dataframe.
        plot_key: str
            The key in the dataframe to be plotted for the time series of the housekeeping data.
        channel1: str
            The channel to be plotted along x-axis for the histogram of the voltage data from the
            science data. Though the default value is set to None here, when you start the GUI, the
            value of "channel1" is set to either "Channel1" or "Channel3" depending on which
            one is plotting in the GUI.
        channel2: str
            The channel to be plotted along y-axis for the histogram of the voltage data from the
            science data. Though the default value is set to None here, when you start the GUI, the
            value of "channel2" is set to either "Channel2" or "Channel4" depending on which
            one is plotting in the GUI.
        bins: int
            The number of bins to be used for the histogram of the main plot, the one that shows the
            distribution of photons on the (x,y) plane.
        cmin: int
            The minimum value of the colorbar for the main plot. Default is 1.
        cmax: int
            The maximum value of the colorbar for the main plot. Be careful while using it, since
            anything above this value will be clipped. Default is None.
        x_min: float
            The minimum value of the x-axis for the main plot. Default is minimum value of x in the
            science data.
        x_max: float
            The maximum value of the x-axis for the main plot. Default is maximum value of x in the
            science data.
        y_min: float
            The minimum value of the y-axis for the main plot. Default is minimum value of y in the
            science data.
        y_max: float
            The maximum value of the y-axis for the main plot. Default is maximum value of y in the
            science data.
        density: bool
            Whether to plot the histogram as a density or not. Default is False.
        norm: bool
            The scale of colorbar to be plotted. Options are "log" or "linear". Default is "log".

    Methods:
        ts_plots:
            Plots the time series of any given parameter from the housekeeping data. It is a
            initialized by the __init__ method. It takes the following arguments:
                - self: The object itself.
                - plot_key: The key in the dataframe to be plotted for the time series of the
                            housekeeping data.
                - start_time: The start time of the data to be plotted. By default this is the
                                first time in the dataframe.
                - end_time: The end time of the data to be plotted. By default this is the last
                                time in the dataframe.

        hist_plots:
            Plots the histogram of the x and y position of the observation. It is a initialized by
            the __init__ method. It needs the following arguments to be passed:
                - self: The object itself.
                - t_start: The start time of the data to be plotted. By default this is the first
                            time in the dataframe.
                - t_end: The end time of the data to be plotted. By default this is the last time
                            in the dataframe.
                - bins: The number of bins to be used for the histogram of the main plot, the one
                            that shows the distribution of photons on the (x,y) plane.
                - cmin: The minimum value of the colorbar for the main plot. Default is 1.
                - cmax: The maximum value of the colorbar for the main plot. Be careful while
                            using it, since anything above this value will be clipped. Default is
                            None.
                - x_min: The minimum value of the x-axis for the main plot. Default is minimum
                            value of x in the science data.
                - x_max: The maximum value of the x-axis for the main plot. Default is maximum
                            value of x in the science data.
                - y_min: The minimum value of the y-axis for the main plot. Default is minimum
                            value of y in the science data.
                - y_max: The maximum value of the y-axis for the main plot. Default is maximum
                            value of y in the science data.
                - density: Whether to plot the histogram as a density or not. Default is False.
                - norm: The scale of colorbar to be plotted. Options are "log" or "linear".
                            Default is "log".

        hist_plots_volt:
            Plots the histogram of the voltage of the observation. It is a initialized by the
            __init__ method. It needs the following arguments to be passed:
                - self: The object itself.
                - t_start: The start time of the data to be plotted. By default this is the first
                            time in the dataframe.
                - t_end: The end time of the data to be plotted. By default this is the last time
                            in the dataframe.
                - channel1: The channel to be plotted along x-axis for the histogram of the voltage
                            data from the science data. Though the default value is set to None
                            here, when you start the GUI, the value of "channel1" is set to either
                            "Channel1" or "Channel3" depending on which one is plotting in the
                            GUI.
                - channel2: The channel to be plotted along y-axis for the histogram of the voltage
                            data from the science data. Though the default value is set to None
                            here, when you start the GUI, the value of "channel2" is set to either
                            "Channel2" or "Channel4" depending on which one is plotting in the
                            GUI.
    """

    def __init__(self,
                 df_slice_hk=None,
                 df_slice_sci=None,
                 start_time=None,
                 end_time=None,
                 plot_key=None,
                 channel1=None,
                 channel2=None,
                 bins=None,
                 cmin=None,
                 cmax=None,
                 x_min=None,
                 x_max=None,
                 y_min=None,
                 y_max=None,
                 density=None,
                 norm=None,
                 ts_fig_height=None,
                 ts_fig_width=None,
                 hist_fig_height=None,
                 hist_fig_width=None
                 ):
        self.df_slice_hk = df_slice_hk
        self.df_slice_sci = df_slice_sci
        self.start_time = start_time
        self.end_time = end_time
        self.plot_key = plot_key
        self.channel1 = channel1
        self.channel2 = channel2
        self.bins = bins
        self.cmin = cmin
        self.cmax = cmax
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.density = density
        self.norm = norm
        self.ts_fig_height = ts_fig_height
        self.ts_fig_width = ts_fig_width
        self.hist_fig_height = hist_fig_height
        self.hist_fig_width = hist_fig_width

    def ts_plots(self):
        """
        Plot the time series of the data

        Return
        ------
            fig: figure object
        """
        # Try to convert the start_time and end_time to float or int
        try:
            t_start = int(self.start_time)
        except Exception:
            t_start = self.df_slice_hk.index.min()
            pass
        try:
            t_end = int(self.end_time)
        except Exception:
            t_end = self.df_slice_hk.index.max()
            pass

        # Make a dictionary of all the plot options and their units
        unit_dict = {"HK_id": "(#)",
                     "PinPullerTemp": "(K)",
                     "OpticsTemp": "(K)",
                     "LEXIbaseTemp": "(C)",
                     "HVsupplyTemp": "(K)",
                     "+5.2V_Imon": "(A)",
                     "+10V_Imon": "(A)",
                     "+3.3V_Imon": "(A)",
                     "AnodeVoltMon": "(V)",
                     "+28 V_Imon": "A",
                     "ADC_Ground": "V",
                     "Cmd_count": "#",
                     "Pinpuller_Armed": "",
                     "HVmcpAuto": "",
                     "HVmcpMan": "",
                     "DeltaEvntCount": "#",
                     "DeltaDroppedCount": "#",
                     "DeltaLostevntCount": "#"
                     }

        alpha = 0.8
        ms = 2
        # Plot the data
        fig = plt.figure(num=None, figsize=(self.ts_fig_width, self.ts_fig_height), facecolor='w',
                         edgecolor='k')
        fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0, hspace=0)
        gs = gridspec.GridSpec(1, 1, width_ratios=[1])

        axs1 = plt.subplot(gs[0])
        axs1.plot(self.df_slice_hk.index, self.df_slice_hk[self.plot_key], '.k', alpha=alpha, ms=ms,
                  label=self.plot_key)
        axs1.set_xlim(t_start, t_end)
        # Rotate the x-axis labels by 45 degrees and set their fontsize
        plt.setp(axs1.get_xticklabels(), rotation=45)
        axs1.set_xlabel('Time (s)')
        axs1.set_ylabel(f"{unit_dict[self.plot_key]}")
        axs1.tick_params(axis="both", which="major")
        axs1.legend(loc='best')
        legend_list = axs1.legend(handlelength=0, handletextpad=0, fancybox=False)
        for item in legend_list.legendHandles:
            item.set_visible(False)

        # Save the figure
        save_file_path = "../figures/time_series_plots/"
        # Check if the save folder exists, if not then create it
        if not Path(save_file_path).exists():
            Path(save_file_path).mkdir(parents=True, exist_ok=True)

        #plt.savefig(f"{save_file_path}/{self.plot_key}_time_series_plot.png", dpi=300,
        #            bbox_inches='tight', pad_inches=0.05, facecolor='w', edgecolor='w',
        #            transparent=False)
        plt.tight_layout()

        return fig

    def hist_plots(self):
        """
        Plot the histogram of the data

        Return
        ------
            fig: figure object
        """

        # Try to convert the start_time and end_time to float or int
        try:
            t_start = int(self.start_time)
        except Exception:
            t_start = self.df_slice_sci.index.min()
            pass
        try:
            t_end = int(self.end_time)
        except Exception:
            t_end = self.df_slice_sci.index.max()
            pass
        try:
            bins = int(self.bins)
        except Exception:
            bins = 50
        try:
            cmin = float(self.cmin)
        except Exception:
            cmin = 1
        try:
            cmax = float(self.cmax)
        except Exception:
            cmax = None
        try:
            x_min = float(self.x_min)
        except Exception:
            x_min = self.df_slice_sci["x_val"].min()
        try:
            x_max = float(self.x_max)
        except Exception:
            x_max = self.df_slice_sci["x_val"].max()
        try:
            y_min = float(self.y_min)
        except Exception:
            y_min = self.df_slice_sci["y_val"].min()
        try:
            y_max = float(self.y_max)
        except Exception:
            y_max = self.df_slice_sci["y_val"].max()
        try:
            density = self.density
        except Exception:
            density = None
        # Check if norm is an instance of mpl.colors.Normalize
        if (self.norm == 'log' or self.norm == 'linear'):
            norm = self.norm
        else:
            norm = None

        if norm == 'log':
            norm = mpl.colors.LogNorm(vmin=cmin, vmax=cmax)
        elif norm == 'linear':
            norm = mpl.colors.Normalize(vmin=cmin, vmax=cmax)

        x_range = [x_min, x_max]
        y_range = [y_min, y_max]

        # Remove rows with duplicate indices
        self.df_slice_sci = self.df_slice_sci[~self.df_slice_sci.index.duplicated(keep='first')]

        # Select data in the specified time range
        self.df_slice_sci = self.df_slice_sci[t_start:t_end]

        hst = plt.hist2d(self.df_slice_sci.x_val, self.df_slice_sci.y_val, bins=bins,
                         range=[x_range, y_range], cmin=cmin, density=density)
        z_counts = np.transpose(hst[0])
        plt.close("all")

        # Raise a warning if the maximum value of the z_counts is greater than the cmax, and print
        # it in red color
        if cmax is not None:
            if np.nanmax(z_counts) > cmax:
                print(f"\n\x1b[1;31;255m WARNING: The maximum value of the z_counts is \n"
                      f"{np.nanmax(z_counts)} This is greater than the cmax value of {cmax}.\n"
                      f"Though the z_counts are plotted, please keep in mind that the"
                      f" histogram may not be visualized properly.\x1b[0m")

        # Make a 2d histogram of the data
        fig = plt.figure(num=None, figsize=(self.hist_fig_width, self.hist_fig_height),
                         facecolor='w', edgecolor='k')
        fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0., hspace=0)

        gs = gridspec.GridSpec(1, 1, height_ratios=[1], width_ratios=[1])

        axs1 = plt.subplot(gs[0, 0])
        im1 = axs1.imshow(z_counts, cmap='Spectral', norm=norm,
                          extent=[x_range[0], x_range[1], y_range[0], y_range[1]], origin='lower',
                          aspect='equal')

        divider1 = make_axes_locatable(axs1)
        cax1 = divider1.append_axes("top", size="5%", pad=0.02)
        cbar1 = plt.colorbar(im1, cax=cax1, orientation='horizontal', ticks=None, fraction=0.05,
                             pad=0.0)

        cbar1.ax.tick_params(axis='x', which='both', direction='in', labeltop=True, top=True,
                             labelbottom=False, bottom=False, width=1, length=10,
                             labelsize=15, labelrotation=0, pad=0)

        cbar1.ax.xaxis.set_label_position('top')

        if density is True:
            cbar1.set_label('Density')
        else:
            cbar1.set_label('N', labelpad=0.0, rotation=0)

        axs1.set_xlabel('Strip = V1/(V1+V3)')
        axs1.set_ylabel('Wedge = V2/(V2+V4)')
        axs1.set_xlim(x_min, x_max)
        axs1.set_ylim(y_min, y_max)
        axs1.tick_params(axis="both", which="major")

        # Save the figure
        #save_file_path = "../figures/hist_plots/"
        # Check if the save folder exists, if not then create it
        #if not Path(save_file_path).exists():
        #    Path(save_file_path).mkdir(parents=True, exist_ok=True)
#
        #plt.savefig(f"{save_file_path}/hist_plot.png", dpi=100, bbox_inches='tight',
        #            pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)

        #plt.close("all")
        plt.tight_layout()
        return fig

    def hist_plots_volt(self):
        """
        This function creates a histogram of the voltage data.

        Return
        ------
            fig: figure object
        """
        # Try to convert the start_time and end_time to float or int
        try:
            t_start = int(self.start_time)
        except Exception:
            t_start = self.df_slice_sci.index.min()
            pass
        try:
            t_end = int(self.end_time)
        except Exception:
            t_end = self.df_slice_sci.index.max()
            pass

        self.df_slice_sci = self.df_slice_sci[~self.df_slice_sci.index.duplicated(keep='first')]
        v1 = self.df_slice_sci[self.channel1][t_start:t_end]
        v2 = self.df_slice_sci[self.channel2][t_start:t_end]

        labelsize = 28
        ticklabelsize = 20
        ticklength = 10

        fig = plt.figure(num=None, figsize=(3, 3), dpi=200, facecolor='w', edgecolor='k')
        fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0., hspace=3)

        '''
        axs1 = sns.jointplot(x=v1, y=v2, cmap='Reds', kind="hist", bins=30,
                             hue_norm=mpl.colors.Normalize(vmin=1, vmax=10),
                             xlim=[0.1, 4], ylim=[0.1, 4], height=8, ratio=6, space=0.)

        #axs1 = sns.jointplot(x=v1, y=v2, cmap='Reds', kind="scatter", alpha=0.5,
        #                     hue_norm=mpl.colors.LogNorm(vmin=1, vmax=10000),
        #                     xlim=[0.1, 4], ylim=[0.1, 4], height=8, ratio=6, space=0.)
        axs1.fig.axes[0].tick_params(axis='both', which='major', direction='in', labelbottom=True,
                                     bottom=True, labeltop=False, top=True, labelleft=True,
                                     left=True, labelright=False, right=True, width=1.5,
                                     length=ticklength, labelsize=ticklabelsize, labelrotation=0)

        axs1.fig.axes[0].tick_params(axis='both', which='minor', direction='in', labelbottom=False,
                                     bottom=False, left=False, width=1.5, length=ticklength,
                                     labelsize=ticklabelsize, labelrotation=0)

        axs1.fig.axes[1].tick_params(axis='both', which='both', direction='in', labelbottom=False,
                                     bottom=False, labelleft=False, left=False, width=1.5,
                                     length=ticklength, labelsize=ticklabelsize, labelrotation=0)

        axs1.fig.axes[2].tick_params(axis='both', which='both', direction='in', labelbottom=False,
                                     bottom=False, labelleft=False, left=False, width=1.5,
                                     length=ticklength, labelsize=ticklabelsize, labelrotation=0)

        axs1.ax_joint.set_xlabel(self.channel1, fontsize=labelsize)
        axs1.ax_joint.set_ylabel(self.channel2, fontsize=labelsize)
        '''
        x_range = [0.9 * v1.min(), 1.1 * v1.max()]
        y_range = [0.9 * v2.min(), 1.1 * v2.max()]
        hst = np.histogram2d(v1, v2, bins=50,
                             range=[[x_range[0], x_range[1]], [y_range[0], y_range[1]]],
                             density=True)

        gs = gridspec.GridSpec(1, 1, height_ratios=[1], width_ratios=[1])

        axs1 = plt.subplot(gs[0, 0])
        im1 = axs1.imshow(hst[0], cmap="Spectral_r", norm=mpl.colors.LogNorm(),
                          extent=[x_range[0], x_range[1], y_range[0], y_range[1]], aspect='auto',
                          interpolation='nearest', origin='lower')
        divider1 = make_axes_locatable(axs1)
        cax1 = divider1.append_axes("top", size="5%", pad=0.02)
        cbar1 = plt.colorbar(im1, cax=cax1, orientation='horizontal', ticks=None, fraction=0.05,
                             pad=0.0)
        axs1.tick_params(axis='both', which='major', direction='in', labelbottom=True,
                         bottom=True, labeltop=False, top=True, labelleft=True,
                         left=True, labelright=False, right=True, width=1.5,
                         length=ticklength, labelsize=ticklabelsize, labelrotation=0)

        cbar1.ax.tick_params(axis='x', which='both', direction='in', labeltop=True, top=True,
                             labelbottom=False, bottom=False, width=0.7, length=5,
                             labelsize=10, labelrotation=0, pad=0)
        axs1.set_xlabel(self.channel1, fontsize=labelsize)
        axs1.set_ylabel(self.channel2, fontsize=labelsize)
        # Save the figure
        save_file_path = "../figures/hist_plots/"
        # Check if the save folder exists, if not then create it
        if not Path(save_file_path).exists():
            Path(save_file_path).mkdir(parents=True, exist_ok=True)

        plt.savefig(f"{save_file_path}/hist_plot_{self.channel1}_{self.channel2}.png", dpi=100,
                    bbox_inches='tight', pad_inches=0.05, facecolor='w', edgecolor='w',
                    transparent=False)

        plt.close('all')

        return fig
