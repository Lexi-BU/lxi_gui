import pandas as pd
import plotly.express as px

read_data = False
if read_data:
    # Read the data
    df = pd.read_csv("all_data_v2.csv")

    # Set date as index
    df['Date'] = pd.to_datetime(df['Date'], utc=True)
    df.set_index('Date', inplace=True)

    # Add a new column for day, and each time the day changes, increment the day number by 1
    df['Day'] = 0
    df["number_of_data_points"] = 0
    day = 1
    number_of_data_points = 0
    for i in range(1, len(df)):
        df["number_of_data_points"][df.index[i]] = number_of_data_points + 1
        number_of_data_points += 1
        if df.index[i].day != df.index[i-1].day:
            day += 1
            number_of_data_points = 0
        df['Day'][
            df.index[i]
        ] = day
        # Print the progress every 1000 rows
        if i % 1000 == 0:
            print(f"Progress: {i}/{len(df)}")


# Plot the data using plotly, with number of data points on the x-axis, PinPullerTemp on the y-axis,
# and color-coded by day
fig = px.scatter(
    df,
    x="number_of_data_points",
    y="PinPullerTemp",
    color="Day",
    title="PinPullerTemp vs Number of Data Points (Day 0 = 2025-01-16)",
    labels={"number_of_data_points": "Number of Data Points", "PinPullerTemp": "PinPullerTemp (°C)"},
    color_discrete_map="plasma_r",
    template="plotly_dark",
)
# Add x-limit to the plot
# fig.update_xaxes(range=[0, 8000])
# fig.show()

# Save the figure as a html file
fig.write_html("pinpuller_temp_vs_number_of_data_points.html")
