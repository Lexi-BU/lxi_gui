import pandas as pd
import plotly.express as px
import lxi_save_figures as lsf
import importlib
importlib.reload(lsf)

# Get all the data
df = lsf.read_and_plot_all_files()
# Get rid of all columns except for index and PinPullerTemp
selected_columns = ["PinPullerTemp"]
df = df[selected_columns]
# df["Date"] = pd.to_datetime(df["Date"], utc=True)
# df.set_index("Date", inplace=True)

# Add a new column for day, and each time the day changes, increment the day number by 1 (if the data
# points are separated by more than 1 hour)
df["operation_number"] = 1
df["number_of_data_points"] = 1
operation_number = 1
number_of_data_points = 1
for i in range(1, len(df)):
    # if df.index[i].day != df.index[i - 1].day and (df.index[i] - df.index[i - 1]).seconds > 3600:
    #         day += 1
    #         number_of_data_points = 0
    if (df.index[i] - df.index[i - 1]).total_seconds() > 10800:
        operation_number += 1
        number_of_data_points = 1
        df["number_of_data_points"][df.index[i]] = number_of_data_points
        df["operation_number"][df.index[i]] = operation_number
    else:
        number_of_data_points += 1
        df["number_of_data_points"][df.index[i]] = number_of_data_points
        df["operation_number"][df.index[i]] = operation_number

    # Print the progress every 1000 rows
    if i % 1000 == 0:
        print(f"Progress: {i}/{len(df)}")

# Get rid of the rows with NaN values
df = df.dropna()
df["operation_number"] = df["operation_number"].astype(int)
df["number_of_data_points"] = df["number_of_data_points"] / 60
# Save the data to a csv file
# df.to_csv("all_data_modified.csv")

# Convert operation_number to string
# df = pd.read_csv("all_data_modified.csv")
# df["operation_number"] = df["operation_number"].astype(str)  # If you want discrete color scale
# df["operation_number"] = df["operation_number"].astype(int)  # If you want continuous color scale
# Add Date as a column
df["Date"] = df.index

# Plot the data using plotly, with number of data points on the x-axis, PinPullerTemp on the y-axis,
# # and color-coded by operation number
fig = px.scatter(
    df,
    x="number_of_data_points",
    y="PinPullerTemp",
    color="operation_number",
    # size="PinPullerTemp",
    # symbol="operation_number",
    title="PinPullerTemp vs Time since start for each operation",
    labels={"number_of_data_points": "Time since start [Minutes]", "PinPullerTemp": "PinPullerTemp [°C]"},
    color_discrete_sequence=px.colors.qualitative.Plotly,
    template="plotly_dark",
    # color_continuous_scale="plasma_r",
    opacity=0.5,
    # marginal_y="box",
    # animation_frame="operation_number",
    # animation_group="number_of_data_points",
    hover_data={"operation_number": True, "number_of_data_points": False, "PinPullerTemp": True, "Date": True},
)

# fig.update_traces(marker=dict(size=4), line=dict(width=1, color='DarkSlateGrey'))
fig.update_xaxes(range=[0, 130])
fig.update_yaxes(range=[60, 70])
# Add x-limit to the plot
# fig.update_xaxes(range=[0, 8000])

# Rotate the colorbar label by 270 degrees
fig.update_coloraxes(colorbar_title_side="right", colorbar_title_text="Operation Number")
fig.update_coloraxes(colorbar_title=dict(text="Operation Number", side="right"))


# Add x-limit to the plot
# fig.update_xaxes(range=[0, 8000])
# fig.show()
fig.write_html(f"../figures/pinpuller_temp_vs_number_of_data_points_{selected_columns}.html")
