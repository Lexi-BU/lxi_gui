
import matplotlib.pyplot as plt
import pandas as pd

# Set latex font to true
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# Read in the data from the CSV file and set the "Date" column as the index
df = pd.read_csv("/home/cephadrius/Downloads/payload_lexi_1716500385_19884_1717186843_36505_hk_output.csv", index_col=False)
# df.set_index("Date", inplace=True)

time_min = "2024-05-23 21:39:00"
time_max = "2024-05-31 20:25:00"
key_list = ['PinPullerTemp', 'OpticsTemp', 'LEXIbaseTemp',
            'HVsupplyTemp', '+5.2V_Imon', '+10V_Imon', '+3.3V_Imon', 'AnodeVoltMon',
            '+28V_Imon', 'ADC_Ground', 'Cmd_count', 'Pinpuller_Armed', 'HVmcpAuto', 'HVmcpMan', 'DeltaEvntCount', 'DeltaDroppedCount']

# Specify the time range
time_min = pd.to_datetime("2024-05-23 21:39:00")
time_max = pd.to_datetime("2024-05-31 20:25:00")


# Get a list of unique dates in the 'Date' column
date_list = pd.to_datetime(df['Date']).dt.date.unique()

# Make a list of 16 colors for the 16 subplots
colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray',
          'olive', 'cyan', 'black', 'yellow', 'lime', 'teal', 'aqua', 'magenta']

# Iterate over each date and create plots
for dd, date in enumerate(date_list):
    # Filter the DataFrame for the current date
    df_day = df[pd.to_datetime(df['Date']).dt.date == date]

    # Create a new figure with a 4x4 grid
    fig, axes = plt.subplots(4, 4, figsize=(15, 9))

    # Flatten the axes array
    axes = axes.flatten()

    # Iterate over each key and plot the data
    for i, key in enumerate(key_list):
        # Filter the data for the current key
        data = df_day[key]
        time_day = df_day['Date']

        # Select the corresponding axis
        ax = axes[i]

        # Plot the data
        ax.plot(data.index, data.values, color=colors[i], marker='.', linestyle='none', markersize=1)

        # Set the title for the subplot
        ax.set_title(key)

        # Set the x-axis label
        ax.set_xlabel('Time')

        # Set the y-axis label
        ax.set_ylabel('Value')

    # Add a title for the entire figure (suptitle)
    plt.suptitle(f"Day {str(dd + 1)}, Date: {str(date)}", fontsize=16)

    # Adjust the spacing between subplots
    plt.tight_layout()


    # Save the figure
    filename = f"plot_{str(date)}.png"
    plt.savefig(filename)

    # Close the figure
    plt.close()

    print(f"Plot saved for {str(date)}")

print("All plots saved.")