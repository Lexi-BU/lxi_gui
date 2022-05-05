from cProfile import label
import importlib
from pathlib import Path
import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable

import global_variables

importlib.reload(global_variables)


class plot_data_class():

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
                 norm=None
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

    def ts_plots(self):

        # Try to convert the start_time and end_time to float or int
        try:
            t_start = float(self.start_time)
        except Exception:
            #print(f"Error: {e} failed start")
            t_start = self.df_slice_hk.index.min()
            pass
        try:
            t_end = float(self.end_time)
        except Exception:
            #print(f"Error: {e}, failed end")
            t_end = self.df_slice_hk.index.max()
            pass
        #if not isinstance(t_start, (int, float)):
        #    t_start = None
#
        #if not isinstance(t_end, (int, float)):
        #    t_end = None
        """
        #self.plot_entry_1 = plot_opt_entry_1.get()
        print(f"Hey...this code worked and key is {self.key}!")
        """
        tick_label_size = 18
        axis_label_size = 25
        alpha = 0.8
        ms = 2
        # Plot the data
        fig = plt.figure(num=None, figsize=(4, 2), dpi=200, facecolor='w', edgecolor='k')
        fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0, hspace=0)
        gs = gridspec.GridSpec(1, 1, width_ratios=[1])

        axs1 = plt.subplot(gs[0])
        axs1.plot(self.df_slice_hk.index, self.df_slice_hk[self.plot_key], '.k', alpha=alpha, ms=ms,
                  label=self.plot_key)
        axs1.set_xlim(t_start, t_end)
        # Rotate the x-axis labels by 45 degrees and set their fontsize
        plt.setp(axs1.get_xticklabels(), rotation=45, fontsize=tick_label_size)
        #axs1.set_xticklabels(labels=axs1.get_xticks(), fontsize=tick_label_size, rotattion=45)
        axs1.set_xlabel('Time (s)', fontsize=axis_label_size)
        #axs1.set_ylabel(f'{self.plot_key}', fontsize=axis_label_size)
        axs1.tick_params(axis="both", which="major", labelsize=tick_label_size)
        axs1.legend(loc='best', fontsize=tick_label_size)
        #axs1.text(1, 0.95, self.plot_key, horizontalalignment='right', fontsize=tick_label_size,
        #          verticalalignment='top', transform=axs1.transAxes)

        # Save the figure
        save_file_path = "../figures/time_series_plots/"
        # Check if the save folder exists, if not then create it
        if not Path(save_file_path).exists():
            Path(save_file_path).mkdir(parents=True, exist_ok=True)

        plt.savefig(f"{save_file_path}/{self.plot_key}_time_series_plot.png", dpi=300,
                    bbox_inches='tight', pad_inches=0.05, facecolor='w', edgecolor='w',
                    transparent=False)

        plt.close("all")
        return fig

    def hist_plots(self):

        # Try to convert the start_time and end_time to float or int
        try:
            t_start = float(self.start_time)
        except Exception:
            #print(f"Error: {e} failed start")
            t_start = self.df_slice_sci.index.min()
            pass
        try:
            t_end = float(self.end_time)
        except Exception:
            #print(f"Error: {e}, failed end")
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
            density =None
        # Check if norm is an instance of mpl.colors.Normalize
        if (self.norm == 'log' or self.norm == 'linear'):
            norm = self.norm
        else:
            norm = None

        #if not isinstance(t_start, (int, float)):
        #    t_start = None

        tick_label_size = 18
        axis_label_size = 25

        if norm == 'log':
            norm = mpl.colors.LogNorm(vmin=cmin, vmax=cmax)
        elif norm == 'linear':
            norm = mpl.colors.Normalize(vmin=cmin, vmax=cmax)

        if density == str(True):
            density = True
        elif density == str(False):
            density = False
        elif density == None:
            density = False

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

        # Make a 2d histogram of the data
        fig = plt.figure(num=None, figsize=(4, 4), dpi=200, facecolor='w', edgecolor='k')
        fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0., hspace=0)

        gs = gridspec.GridSpec(1, 1, height_ratios=[1], width_ratios=[1])

        axs1 = plt.subplot(gs[0, 0])
        #im1 = sns.jointplot(data=df[["x_val", "y_val"]], kind="kde")
        im1 = axs1.imshow(z_counts, cmap='Spectral', norm=norm,
                          extent=[x_range[0], x_range[1], y_range[0], y_range[1]], origin='lower',
                          aspect='auto')

        divider1 = make_axes_locatable(axs1)
        cax1 = divider1.append_axes("top", size="5%", pad=0.02)
        cbar1 = plt.colorbar(im1, cax=cax1, orientation='horizontal', ticks=None, fraction=0.05,
                             pad=0.0)

        cbar1.ax.tick_params(axis='x', which='both', direction='in', labeltop=True, top=True,
                             labelbottom=False, bottom=False, width=1, length=10,
                             labelsize=15, labelrotation=0, pad=0)

        cbar1.ax.xaxis.set_label_position('top')

        if density is True:
            cbar1.set_label('Density', fontsize=20)
        else:
            cbar1.set_label(r'$N$', fontsize=15, labelpad=0.0, rotation=0)

        axs1.set_xlabel('Strip = V1/(V1+V3)', fontsize=axis_label_size)
        axs1.set_ylabel('Wedge = V2/(V2+V4)', fontsize=axis_label_size)
        axs1.set_xlim(x_min, x_max)
        axs1.set_ylim(y_min, y_max)
        axs1.tick_params(axis="both", which="major", labelsize=tick_label_size)

        # Save the figure
        save_file_path = "../figures/hist_plots/"
        # Check if the save folder exists, if not then create it
        if not Path(save_file_path).exists():
            Path(save_file_path).mkdir(parents=True, exist_ok=True)

        plt.savefig(f"{save_file_path}/hist_plot.png", dpi=100, bbox_inches='tight',
                    pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)

        plt.close("all")
        return fig

    def hist_plots_volt(self):

        # Try to convert the start_time and end_time to float or int
        try:
            t_start = float(self.start_time)
        except Exception:
            # print(f"Error: {e} failed start")
            t_start = self.df_slice_sci.index.min()
            pass
        try:
            t_end = float(self.end_time)
        except Exception:
            # print(f"Error: {e}, failed end")
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

        axs1 = sns.jointplot(x=v1, y=v2, palette='Spectral',
                             hue_norm=mpl.colors.LogNorm(vmin=1, vmax=100),
                             xlim=[0.1, 4], ylim=[0.1, 4], height=8, ratio=6, space=0.)

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
