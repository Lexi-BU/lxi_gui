import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
from sklearn.linear_model import LinearRegression
from pathlib import Path
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Load the data
fn_hk = "../data/processed_data.pkl"
df_hk = pd.read_pickle(fn_hk)

# List of selected keys
selected_keys = ["PinPullerTemp", "LEXIbaseTemp", "HVsupplyTemp", "+5.2V_Imon", "+10V_Imon", "+3.3V_Imon", "AnodeVoltMon", "+28V_Imon", "DeltaEvntCount", "DeltaDroppedCount", "DeltaLostEvntCount", "HV_value"]

# Filter data for a specific operation number
operation_number = 27
df_filtered = df_hk[df_hk["operation_number"] == operation_number]

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app with dark mode
app.layout = html.Div(
    style={"backgroundColor": "#121212", "color": "white", "height": "100vh", "padding": "20px"},
    children=[
        html.H1("Trend Analysis Dashboard", style={"color": "white"}),
        html.Label("Select Key:", style={"color": "white"}),
        dcc.Dropdown(
            id="key-dropdown",
            options=[{"label": key, "value": key} for key in selected_keys],
            value=selected_keys[0],  # Default selected key
            clearable=False,
            className="dark-dropdown",
            style={"backgroundColor": "#333333", "color": "white"}
        ),
        dcc.Graph(id="trend-plot")
    ]
)


# Callback to update the plot based on the selected key
@app.callback(
    Output("trend-plot", "figure"),
    Input("key-dropdown", "value")
)
def update_plot(selected_key):
    # Drop rows with missing values for the selected key
    df_filtered_new = df_filtered.dropna(subset=[selected_key])

    try:
        # Extract trends
        linear_trend, periodic_trend = extract_trends(df_filtered_new, selected_key)

        # Shift the linear trend to y=0
        shifted_linear_trend = linear_trend - linear_trend  # Horizontal line at y=0
        shifted_data = df_filtered_new[selected_key].values - linear_trend  # Shift original data by the linear trend

        # Create a Plotly figure with dark mode
        fig = go.Figure()

        # Add shifted original data (on secondary y-axis)
        fig.add_trace(go.Scatter(
            x=df_filtered_new.index,
            y=shifted_data,
            mode="lines",
            name="Shifted Original Data",
            line=dict(color="#1f77b4"),  # Blue
            yaxis="y2"  # Plot on secondary y-axis
        ))

        # Add shifted linear trend (horizontal line at y=0)
        fig.add_trace(go.Scatter(
            x=df_filtered_new.index,
            y=shifted_linear_trend,
            mode="lines",
            name="Linear Trend (y=0)",
            line=dict(color="rgba(255, 255, 0, 1)", width=2)  # Orange
        ))

        # Add periodic trend
        fig.add_trace(go.Scatter(
            x=df_filtered_new.index,
            y=periodic_trend,
            mode="lines",
            name="Periodic Trend",
            line=dict(color="rgba(44, 160, 44, 0.25)", dash="dot")  # Green
        ))

        # Add trend line equation
        X = np.arange(len(df_filtered_new[selected_key])).reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, df_filtered_new[selected_key].values)
        slope = model.coef_[0]
        intercept = model.intercept_
        trend_equation = f"Trend Line: y = {slope:.4f}x + {intercept:.4f}"

        # Add periodicity information
        detrended_data = df_filtered_new[selected_key].values - linear_trend
        fft_values = fft(detrended_data)
        freqs = fftfreq(len(detrended_data))
        dominant_freq = freqs[np.argmax(np.abs(fft_values))]  # Dominant frequency
        if dominant_freq != 0:
            period = 1 / dominant_freq
            periodicity_info = f"Dominant Period: {abs(period):.2f} Seconds"
        else:
            periodicity_info = "No significant periodicity detected"

        # Add annotations and dark mode layout
        fig.update_layout(
            # Adjust the figure height to accommodate the annotations
            height=700,
            title=f"Trend Analysis for {selected_key} (Operation Number: {operation_number})",
            xaxis_title="Time",
            yaxis_title="Detrended Data",
            yaxis2=dict(
                title="Original Data",
                overlaying="y",
                side="right"
            ),
            plot_bgcolor="#121212",  # Dark background
            paper_bgcolor="#121212",  # Dark background
            font=dict(color="white"),  # White text
            xaxis=dict(gridcolor="#333333"),  # Dark grid lines
            yaxis=dict(gridcolor="#333333"),  # Dark grid lines
            annotations=[
                dict(
                    x=0.05,
                    y=0.95,
                    xref="paper",
                    yref="paper",
                    text=trend_equation,
                    showarrow=False,
                    font=dict(size=12, color="white"),
                    bgcolor="#333333",
                    bordercolor="white",
                    borderwidth=1
                ),
                dict(
                    x=0.05,
                    y=0.85,
                    xref="paper",
                    yref="paper",
                    text=periodicity_info,
                    showarrow=False,
                    font=dict(size=12, color="white"),
                    bgcolor="#333333",
                    bordercolor="white",
                    borderwidth=1
                )
            ]
        )

        return fig
    except Exception as e:
        return go.Figure()  # Return an empty figure in case of errors


# Function to extract trends
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


# Run the app
if __name__ == "__main__":
    host = "127.0.0.10"
    port = "8050"
    app.run_server(debug=False, host=host, port=port)
    print(f"Dash server running on http://{host}:{port}/")
