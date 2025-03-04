from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

file_name = "/home/vetinari/Desktop/git/Lexi-Bu/lxi_gui/data/from_LEXI/L1c/sci/20250304/lexi_payload_1741045011_26370_1741049498_18301_sci_output_L1c.csv"

df = pd.read_csv(file_name, index_col=0)

selected_columns = ["Channel1", "Channel2", "Channel3", "Channel4"]

min_channel_1 = 3
max_channel_1 = 3.3
min_channel_2 = 1.6
max_channel_2 = 3.3
min_channel_3 = 1.6
max_channel_3 = 3.3
min_channel_4 = 1.6
max_channel_4 = 3.3

df_new = df[selected_columns]
# Remove where "IsCommanded" is True
df_new = df_new[df["IsCommanded"] == False]
df_new = df_new[
    (df_new["Channel1"] >= min_channel_1)
    & (df_new["Channel1"] <= max_channel_1)
    & (df_new["Channel2"] >= min_channel_2)
    & (df_new["Channel2"] <= max_channel_2)
    & (df_new["Channel3"] >= min_channel_3)
    & (df_new["Channel3"] <= max_channel_3)
    & (df_new["Channel4"] >= min_channel_4)
    & (df_new["Channel4"] <= max_channel_4)
]

x_val = df_new["Channel3"] / (df_new["Channel3"] + df_new["Channel1"])
y_val = df_new["Channel2"] / (df_new["Channel4"] + df_new["Channel2"])


plt.figure()
plt.scatter(x_val, y_val, s=1, c="black")
plt.xlabel("Channel3 / (Channel3 + Channel1)")
plt.ylabel("Channel2 / (Channel4 + Channel2)")
plt.title("Channel2 vs Channel3")
plt.xlim(0.35, 0.6)
plt.ylim(0.35, 0.6)
# Print the minimum value of each channel on the plot
plt.text(0.35, 0.35, f"Channel1: {min_channel_1}", fontsize=12, color="red")
plt.text(0.35, 0.36, f"Channel2: {min_channel_2}", fontsize=12, color="red")
plt.text(0.35, 0.37, f"Channel3: {min_channel_3}", fontsize=12, color="red")
plt.text(0.35, 0.38, f"Channel4: {min_channel_4}", fontsize=12, color="red")
# plt.show()
plt.savefig("Channel2_vs_Channel3_with_thresholded_channel1.png")

"""

"""
