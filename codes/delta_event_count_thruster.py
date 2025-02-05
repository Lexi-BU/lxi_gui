import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def forward(y):
    """Custom forward scale function"""
    return np.where(np.abs(y) <= 1, y, np.sign(y) * (1 + np.log10(np.abs(y))))


def inverse(y):
    """Custom inverse scale function"""
    return np.where(np.abs(y) <= 1, y, np.sign(y) * 10 ** (np.abs(y) - 1))


hk_file_name = "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/from_LEXI/L1a/hk/20250204/payload_lexi_1738679519_25096_1738684713_9851_hk_output_L1a.csv"

thuster_file_name = "/home/cephadrius/Desktop/git/Lexi-BU/lxi_gui/data/from_LEXI/orbit/20250204/LEXI Transit Op 18 - ACS Thruster Cycle Count Data.csv"

df_hk = pd.read_csv(hk_file_name, parse_dates=["Date"])
# Set Date as index and set it to UTC
df_hk.index = df_hk["Date"].dt.tz_localize("UTC")

df_thruster = pd.read_csv(thuster_file_name, parse_dates=["Time"])
# Set Time as index and set it to UTC
df_thruster.index = df_thruster["Time"].dt.tz_localize("UTC")

hk_key = "DeltaEvntCount"
thruster_key = "Sum_All"

# Get 1 minute rolling average of hk_key
df_hk[f"{hk_key}_rolling"] = df_hk[hk_key].rolling("1min").mean()

fontsize = 18

plt.style.use("dark_background")

# Plot the data
fig, axs = plt.subplots(1, 1, figsize=(10, 8), sharex=True)

axs.scatter(df_hk.index, df_hk[hk_key], s=0.5, c="m", alpha=0.5, label=hk_key)
axs.plot(df_hk.index, df_hk[f"{hk_key}_rolling"], color="w", lw=1.5, label=f"1-minute rolling-{hk_key}")
twin_ax = axs.twinx()
twin_ax.plot(df_thruster.index, df_thruster[thruster_key], color="c", lw=1.5, label="Thurst Events", zorder=0)

axs.set_xlabel("Time [DD HH:MM] (UTC)", fontdict={"fontsize": fontsize})
axs.set_ylabel(hk_key, fontdict={"color": "m", "alpha": 1, "fontsize": fontsize})
# Set the y-axis spine color to the same as the line color
axs.spines["left"].set_color("m")
# Set the y-axis tick color to the same as the line color
axs.tick_params(axis="y", colors="m")

# Set the y-axis spine color to the same as the line color
twin_ax.spines["right"].set_color("c")
twin_ax.spines["left"].set_color("m")
# Set the y-axis tick color to the same as the line color
twin_ax.tick_params(axis="y", colors="c")
twin_ax.set_ylabel("Thrust number", fontdict={"color": "c", "alpha": 1, "fontsize": fontsize})
axs.grid(True, which="both", ls="--", lw=0.5, alpha=0.5)

axs.set_yscale("function", functions=(forward, inverse))

# Se y-axis tick labels at [0, 1, 5, 10, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000]
axs.set_yticks([0, 1, 5, 10, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000])
# Set the major locator for the x-axis to Date Formatter
# axs.xaxis.set_major_locator(plt.MaxNLocator(10))

# Set the x-axis limits to minimum and maximum time in df_hk
axs.set_xlim(df_hk.index.min(), df_hk.index.max())
# Set the y-axis limits to minimum and maximum of hk_key
axs.set_ylim(df_hk[hk_key].min(), 10 * df_hk[hk_key].max())

# Set legend location
axs.legend(loc="upper left", fontsize=0.75 * fontsize)
twin_ax.legend(loc="upper right", fontsize=0.75 * fontsize)
# Rotate the x-axis labels
plt.setp(axs.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=0.75 * fontsize)

# Set y-axis label size
axs.yaxis.label.set_size(0.75 * fontsize)
twin_ax.yaxis.label.set_size(0.75 * fontsize)

plt.title("HK and Thruster Data", fontdict={"fontsize": fontsize})
plt.savefig("../figures/hk_thruster_data.png", dpi=300, bbox_inches="tight")
