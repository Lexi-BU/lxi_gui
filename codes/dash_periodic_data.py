import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
from sklearn.linear_model import LinearRegression
from pathlib import Path
import plotly.graph_objects as go

def extract_trends(data, key):
    """
    Extract linear and periodic trends from a time series.

    Parameters:
        data (pd.DataFrame): The dataframe containing the time series.
        key (str): The column name for which to extract trends.

    Returns:
        linear_trend (np.array): The linear trend component.
        periodic_trend (np.array): The periodic trend component.
    """
    # Ensure the data is sorted by time (if applicable)
    if "DateTime" in data.columns:
        data = data.sort_values("DateTime")

    # Extract the time series for the given key
    y = data[key].values

    # Linear Trend: Fit a linear regression model
    X = np.arange(len(y)).reshape(-1, 1)  # Time as the independent variable
    model = LinearRegression()
    model.fit(X, y)
    linear_trend = model.predict(X)

    # Periodic Trend: Subtract the linear trend and use Fourier Transform
    detrended_data = y - linear_trend

    # Use Fourier Transform to extract periodic components
    n = len(detrended_data)
    fft_values = fft(detrended_data)
    freqs = fftfreq(n)

    # Filter out low-frequency components (keep only periodic components)
    threshold = 0.1  # Adjust this threshold based on your data
    fft_values[np.abs(freqs) < threshold] = 0
    periodic_trend = np.real(np.fft.ifft(fft_values))

    return linear_trend, periodic_trend


# Load the data
fn_hk = "../data/processed_data.pkl"
df_hk = pd.read_pickle(fn_hk)

# List of selected keys
selected_keys = ["PinPullerTemp", "LEXIbaseTemp", "HVsupplyTemp", "+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon", "DeltaEvntCount", "DeltaDroppedCount", "DeltaLostEvntCount", "HV_value"]

# Store results in a dictionary
trends = {}
operation_number = 27
df_filtered = df_hk[df_hk["operation_number"] == operation_number]

# Extract trends for each key
for key in selected_keys:
    # Drop the rows with missing values or NaNs
    df_filtered_new = df_filtered.dropna(subset=[key])
    try:
        print(f"Extracting trends for \033[1;33m{key}\033[0m")
        linear_trend, periodic_trend = extract_trends(df_filtered_new, key)
        trends[key] = {"linear_trend": linear_trend, "periodic_trend": periodic_trend}

        # Shift the linear trend to y=0
        shifted_linear_trend = linear_trend - linear_trend  # This will be a horizontal line at y=0
        shifted_data = df_filtered_new[key].values - linear_trend  # Shift original data by the linear trend

        # Create a Plotly figure
        fig = go.Figure()

        # Add shifted original data (on secondary y-axis)
        fig.add_trace(go.Scatter(
            x=df_filtered_new.index,
            y=shifted_data,
            mode="lines",
            name="Shifted Original Data",
            line=dict(color="blue"),
            yaxis="y2"  # Plot on secondary y-axis
        ))

        # Add shifted linear trend (horizontal line at y=0)
        fig.add_trace(go.Scatter(
            x=df_filtered_new.index,
            y=shifted_linear_trend,
            mode="lines",
            name="Linear Trend (y=0)",
            line=dict(color="red", dash="dash")
        ))

        # Add periodic trend
        fig.add_trace(go.Scatter(
            x=df_filtered_new.index,
            y=periodic_trend,
            mode="lines",
            name="Periodic Trend",
            line=dict(color="green", dash="dot")
        ))

        # Add trend line equation
        X = np.arange(len(df_filtered_new[key])).reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, df_filtered_new[key].values)
        slope = model.coef_[0]
        intercept = model.intercept_
        trend_equation = f"Trend Line: y = {slope:.4f}x + {intercept:.4f}"

        # Add periodicity information
        detrended_data = df_filtered_new[key].values - trends[key]["linear_trend"]
        fft_values = fft(detrended_data)
        freqs = fftfreq(len(detrended_data))
        dominant_freq = freqs[np.argmax(np.abs(fft_values))]  # Dominant frequency
        if dominant_freq != 0:
            period = 1 / dominant_freq
            periodicity_info = f"Dominant Period: {abs(period):.2f} units"
        else:
            periodicity_info = "No significant periodicity detected"

        # Add annotations
        fig.update_layout(
            title=f"Trend Analysis for {key} (Operation Number: {operation_number})",
            xaxis_title="Time",
            yaxis_title="Detrended Data",
            yaxis2=dict(
                title="Original Data",
                overlaying="y",
                side="right"
            ),
            annotations=[
                dict(
                    x=0.05,
                    y=0.95,
                    xref="paper",
                    yref="paper",
                    text=trend_equation,
                    showarrow=False,
                    font=dict(size=12),
                    bgcolor="white",
                    bordercolor="black",
                    borderwidth=1
                ),
                dict(
                    x=0.05,
                    y=0.85,
                    xref="paper",
                    yref="paper",
                    text=periodicity_info,
                    showarrow=False,
                    font=dict(size=12),
                    bgcolor="white",
                    bordercolor="black",
                    borderwidth=1
                )
            ]
        )

        # Save the figure as an HTML file
        folder_name = "../figures/trends_plots/"
        Path(folder_name).mkdir(parents=True, exist_ok=True)
        fig.write_html(f"{folder_name}{key}.html")

        print(f"Plot saved for {key} at {folder_name}{key}.html")
    except Exception as e:
        print(f"Error extracting trends for \033[1;91m{key}\033[0m: {e}\n")