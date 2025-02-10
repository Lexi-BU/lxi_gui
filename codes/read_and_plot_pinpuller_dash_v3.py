import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import lxi_save_figures as lsf
import prepare_thrust_data_files as ptdf
import importlib
import colorsys
import glob
from pathlib import Path

importlib.reload(lsf)
importlib.reload(ptdf)

read_data = True
if read_data:
    df = lsf.read_and_plot_all_files()
    # Add HV_value column to df
    df["HV_value"] = df["AnodeVoltMon"] * 599
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
    df["DateTime"] = df.index
    unique_operations = sorted(df["operation_number"].unique())

    # Get the thruster data
    df_thruster = ptdf.prepare_thruster_data()
    # Merge the two DataFrames, df and df_thruster, on the DateTime index
    df = pd.merge_asof(df, df_thruster, left_index=True, right_index=True, direction="nearest")
    available_columns = list(df.columns)
    default_columns = [available_columns[18]]  # Default to first column

# Assign unique base colors for columns
column_colors = {
    column: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
    for i, column in enumerate(available_columns)
}


# Function to adjust brightness for different operations
def adjust_color_brightness(hex_color, factor):
    """Darkens or lightens a color based on the factor"""
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    hls = colorsys.rgb_to_hls(*rgb)
    adjusted_rgb = colorsys.hls_to_rgb(hls[0], min(1, max(0, hls[1] * factor)), hls[2])
    return f"#{int(adjusted_rgb[0] * 255):02x}{int(adjusted_rgb[1] * 255):02x}{int(adjusted_rgb[2] * 255):02x}"


app = dash.Dash(__name__)

app.layout = html.Div(
    style={"height": "99vh", "width": "99vw", "backgroundColor": "#121212", "color": "white", "padding": "0px", "overflow": "hidden", "display": "flex", "flexDirection": "column", "alignItems": "left", "justifyContent": "center", "marginLeft": "0vw", "marginRight": "0vw", "justify": "center"},
    children=[
        # html.H1("Select Columns and Operations", style={"textAlign": "center", "color": "white"}),
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
        ], style={"width": "50%", "marginBottom": "2px", "marginTop": "2px", "marginLeft": "5px", "marginRight": "5px"}),
        html.Div([
            html.Label("Select Operations:", style={"color": "white"}),
            dcc.Checklist(
                id="operation_filter",
                options=[{"label": f"Operation {op}", "value": op} for op in unique_operations],
                value=[unique_operations[-1]],
                inline=True,
                # style={"maxHeight": "150px", "overflowY": "hidden"}
                style={"display": "grid", "gridTemplateColumns": "repeat(11, 1fr)", "maxWidth": "100%", "marginRight": "1px", "marginLeft": "5px", "marginBottom": "1px", "marginTop": "1px", "color": "white", "alignItems": "center", "gap": "2px", "justifyContent": "center", "width": "98%", "flexDirection": "row", "padding": "5px", "border": "1px solid white", "borderRadius": "5px", "backgroundColor": "#121212", "overflow": "hidden"}
            )
        ]),
        dcc.Graph(id="line_plot", style={"height": "70vh", "width": "95vw", "overflow": "hidden"}),
        html.Div([
            html.Label("Filtering Length (s):", style={"color": "white"}),
            dcc.Input(id="filtering_length", type="number", value=15, style={"marginRight": "10px", "width": "50px", "textAlign": "center", "backgroundColor": "#121212", "color": "white", "border": "1px solid white", "borderRadius": "5px", "padding": "5px", "marginBottom": "10px", "marginTop": "10px"}),
            html.Label("HV Threshold Low:", style={"color": "white"}),
            dcc.Input(id="hv_threshold_low", type="number", value=1505, style={"marginRight": "10px", "width": "50px", "textAlign": "center", "backgroundColor": "#121212", "color": "white", "border": "1px solid white", "borderRadius": "5px", "padding": "5px", "marginBottom": "10px", "marginTop": "10px"}),
            html.Label("HV Threshold High:", style={"color": "white"}),
            dcc.Input(id="hv_threshold_high", type="number", value=1520, style={"marginRight": "10px", "width": "50px", "textAlign": "center", "backgroundColor": "#121212", "color": "white", "border": "1px solid white", "borderRadius": "5px", "padding": "5px", "marginBottom": "10px", "marginTop": "10px"}),
            dcc.Checklist(
                id="hv_threshold_check",
                options=[{"label": "Enable HV Threshold", "value": "hv_threshold"}],
                value=["hv_threshold"],
                inline=True,
                style={"marginRight": "1px", "marginBottom": "1px", "marginTop": "1px", "color": "white", "display": "flex", "alignItems": "center", "gap": "2px", "justifyContent": "center", "width": "200px", "flexDirection": "row", "padding": "5px", "border": "1px solid white", "borderRadius": "5px", "backgroundColor": "#121212", "overflow": "hidden"}
            ),
            dcc.Checklist(
                id="save_fig_check",
                options=[{"label": "Save Figure", "value": "save_fig"}],
                value=[],
                inline=True,
                style={"marginRight": "1px", "marginBottom": "1px", "marginTop": "1px", "color": "white", "display": "flex", "alignItems": "center", "gap": "2px", "justifyContent": "center", "width": "200px", "flexDirection": "row", "padding": "5px", "border": "1px solid white", "borderRadius": "5px", "backgroundColor": "#121212", "overflow": "hidden"}
            )
        ], style={"marginTop": "10px", "display": "flex", "justifyContent": "center", "gap": "10px", "alignItems": "center"}),
    ]
)


@app.callback(
    Output("line_plot", "figure"),
    [Input("operation_filter", "value"),
     Input("column_selector", "value"),
     Input("filtering_length", "value"),
     Input("hv_threshold_low", "value"),
     Input("hv_threshold_high", "value"),
     Input("hv_threshold_check", "value"),
     Input("save_fig_check", "value")]
)
def update_plot(selected_operations, selected_columns, filtering_length, hv_threshold_low, hv_threshold_high, hv_threshold_check, save_fig_check):
    if not selected_columns:
        return px.line(template="plotly_dark", title="No Column Selected")

    fig = px.line(template="plotly_dark")
    secondary_y = len(selected_columns) == 2

    # If hv_threshold_check is not checked, then set the hv_threshold_low and hv_threshold_high to
    # None
    if not hv_threshold_check:
        hv_threshold_low = 0
        hv_threshold_high = 2500
    for idx, col in enumerate(selected_columns):
        df[f"{col}_smooth"] = df[col].rolling(f"{filtering_length}s", center=False).mean()
        filtered_df = df[df["operation_number"].isin(selected_operations)]
        filtered_df = filtered_df[(filtered_df["HV_value"] > hv_threshold_low) & (filtered_df["HV_value"] < hv_threshold_high)][filtering_length:-filtering_length]

        # Set the maximum number of sig figs for each column to 2
        filtered_df[col] = filtered_df[col].round(2)
        base_color = column_colors[col]
        # Modify the DateTime column to have the following format: "YYYY-MM-DD HH:MM:SS"
        filtered_df["DateTime"] = filtered_df.index.strftime("%Y-%m-%d %H:%M:%S")

        for i, op in enumerate(selected_operations):
            temp_df = filtered_df[filtered_df["operation_number"] == op].reset_index(drop=True)
            temp_df["event_number"] = temp_df.index
            shade_factor = 1 - (i * 0.15) if (i * 0.15) < 1 else 2
            color_shade = adjust_color_brightness(base_color, shade_factor)
            y_axis = "y" if idx == 0 else "y2"

            # Define hover data dynamically
            common_hover_data = {"event_number": False, "operation_number": False, "DateTime": False, f"{col}_smooth": False, col: True}  # Common hover data
            specific_hover_data = {col: True, "event_number": False, f"{col}_smooth": False, "DateTime": True, "operation_number": True}  # Only show column-specific data

            hover_data = common_hover_data if idx != 0 else specific_hover_data  # Include common hover data only once

            # hovertemplate = (
            #     f"Event Number: {{event_number}}\n"  # Display event number
            #     f"Operation Number: {{operation_number}}\n"  # Display operation number
            #     f"DateTime: {{DateTime}}\n"  # Display DateTime
            #     f"{col}: {{:{col}.2g}}\n"  # Limit to 2 significant figures for the current column
            # )
            temp_fig = px.line(
                temp_df,
                x="event_number",
                y=f"{col}_smooth",
                labels={"event_number": "Event Number"},
                color_discrete_sequence=[color_shade],
                hover_data=hover_data,
            )

            for trace in temp_fig["data"]:
                trace["name"] = f"{col} - Operation {op}"
                trace["line"]["color"] = color_shade
                trace["yaxis"] = y_axis
                # trace["hovertemplate"] = hovertemplate
                fig.add_trace(trace)

    fig.update_layout(
        plot_bgcolor="#121212",
        paper_bgcolor="#121212",
        font={"color": "white"},
        xaxis=dict(title="Event Number", title_font=dict(size=20)),
        yaxis=dict(
            title=f"{selected_columns[0]} {input_key_unit}",
            title_font=dict(size=20),
            showline=True,
            linewidth=2,
            linecolor=column_colors[selected_columns[0]],
        ),
        hovermode="x unified",
    )

    # Always add secondary y-axis when there are multiple columns
    if len(selected_columns) > 1:
        fig.update_layout(
            yaxis2=dict(
                title=f"{', '.join(selected_columns[1:])} {input_key_unit}",
                title_font=dict(size=20),
                overlaying="y",
                side="right",
                showline=True,
                linewidth=2,
                linecolor=column_colors[selected_columns[1]],  # Use color of second column
            )
        )

    fig.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
    fig.update_yaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")

    if "save_fig" in save_fig_check:
        fig_name = "_".join(selected_columns) + "_Operations_" + "_".join(map(str, selected_operations))
        fig.write_html(f"../figures/{fig_name}_plot.html")
    return fig


if __name__ == "__main__":
    host = "127.0.0.4"
    port = "8050"
    app.run_server(debug=False, host=host, port=port)
    print(f"Dash server running on http://{host}:{port}/")
