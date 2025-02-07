import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import lxi_save_figures as lsf
import importlib
import colorsys

importlib.reload(lsf)

read_data = False
if read_data:
    df = lsf.read_and_plot_all_files()
    # Add HV_value column to df
    df["HV_value"] = df["AnodeVoltMon"] * 599
    available_columns = list(df.columns)
    default_columns = [available_columns[18]]  # Default to first column
    input_key_unit = "-"
    df["operation_number"] = 1
    df["number_of_data_points"] = 1
    operation_number = 1
    number_of_data_points = 1

    for i in range(1, len(df)):
        if (df.index[i] - df.index[i - 1]).total_seconds() > 10800:
            operation_number += 1
            number_of_data_points = 1
        else:
            number_of_data_points += 1
        df.loc[df.index[i], "number_of_data_points"] = number_of_data_points
        df.loc[df.index[i], "operation_number"] = operation_number
        if i % 1000 == 0:
            print(f"Progress: {i}/{len(df)}")

    # df = df.dropna()
    df["operation_number"] = df["operation_number"].astype(int)
    df["number_of_data_points"] = df["number_of_data_points"] / 60
    df["Date"] = df.index
    unique_operations = sorted(df["operation_number"].unique())

column_colors = {
    column: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
    for i, column in enumerate(available_columns)
}


def adjust_color_brightness(hex_color, factor):
    """Darkens or lightens a color based on the factor"""
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    hls = colorsys.rgb_to_hls(*rgb)
    adjusted_rgb = colorsys.hls_to_rgb(hls[0], min(1, max(0, hls[1] * factor)), hls[2])
    return f"#{int(adjusted_rgb[0] * 255):02x}{int(adjusted_rgb[1] * 255):02x}{int(adjusted_rgb[2] * 255):02x}"


app = dash.Dash(__name__)

app.layout = html.Div(
    style={"height": "100vh", "width": "100vw", "backgroundColor": "#121212", "color": "white", "padding": "10px"},
    children=[
        html.H1("Select Columns and Operations", style={"textAlign": "center", "color": "white"}),
        html.Div([
            html.Label("Select Columns:", style={"color": "white"}),
            dcc.Dropdown(
                id="column_selector",
                options=[{"label": col, "value": col} for col in available_columns],
                value=default_columns,
                multi=True,
                clearable=False,
                className="dark-dropdown"
            )
        ], style={"width": "50%"}),
        html.Div([
            html.Label("Select Operations:", style={"color": "white"}),
            dcc.Checklist(
                id="operation_filter",
                options=[{"label": f"Operation {op}", "value": op} for op in unique_operations],
                value=[unique_operations[-1]],
                inline=True,
                style={"maxHeight": "150px", "overflowY": "scroll"}
            )
        ]),
        dcc.Graph(id="line_plot", style={"height": "85vh", "width": "100%"}),
    ]
)


@app.callback(
    Output("line_plot", "figure"),
    [Input("operation_filter", "value"),
     Input("column_selector", "value")]
)
def update_plot(selected_operations, selected_columns):
    if not selected_columns:
        return px.line(template="plotly_dark", title="No Column Selected")

    fig = px.line(template="plotly_dark")

    for idx, col in enumerate(selected_columns):
        # Apply rolling average over 60 seconds
        df[f"{col}_smooth"] = df[col].rolling('60s', center=True).mean()
        filtered_df = df[df["operation_number"].isin(selected_operations)]
        # Select only those rows where HV_value is greater than 1500
        filtered_df = filtered_df[filtered_df["HV_value"] > 1500]

        for i, op in enumerate(selected_operations):
            # Adjust brightness based on operation number
            color_shade = adjust_color_brightness(column_colors[col], 1 - (i * 0.2))  # Adjust brightness per operation
            temp_fig = px.line(
                filtered_df[filtered_df["operation_number"] == op],
                x="number_of_data_points",
                y=f"{col}_smooth",
                labels={
                    "number_of_data_points": "Time since start [Minutes]",
                    f"{col}_smooth": f"{col} {input_key_unit}",
                },
                color_discrete_sequence=[color_shade],
                hover_data={"Date": True, col: True, "number_of_data_points": True}
            )

            for trace in temp_fig["data"]:
                trace["name"] = f"{col} - Operation {op}"
                trace["line"]["color"] = color_shade  # Assign adjusted color
                # If this is the second column, plot it on the secondary y-axis
                if idx == 1:
                    trace["yaxis"] = "y2"
                fig.add_trace(trace)

    # Update axes and layout
    fig.update_yaxes(showline=True, linewidth=2, linecolor="white", mirror=True)
    fig.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
    fig.update_yaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
    fig.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font={"color": "white"})
    fig.update_xaxes(title_text="Time since start [Minutes]", title_font=dict(size=20))

    # Set y-axis titles
    if len(selected_columns) > 0:
        fig.update_yaxes(title_text=f"{selected_columns[0]} {input_key_unit}", title_font=dict(size=20), side="left")
    if len(selected_columns) > 1:
        fig.update_yaxes(title_text=f"{selected_columns[1]} {input_key_unit}", title_font=dict(size=20), side="right", overlaying="y")

    # Save the figure as html
    if len(selected_columns) > 0:
        fig.write_html(f"{selected_columns[0]}_plot.html")
    return fig


if __name__ == "__main__":
    host = "127.0.0.3"
    port = "8050"
    app.run_server(debug=False, host=host, port=port)
    print(f"Dash server running on http://{host}:{port}/")
