import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import lxi_save_figures as lsf
import importlib
importlib.reload(lsf)

read_data = False
if read_data:
    df = lsf.read_and_plot_all_files()
    available_columns = list(df.columns)
    default_columns = [available_columns[0]]  # Default to the first column
    input_key_unit = "mA"
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

color_map = {
    operation: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
    for i, operation in enumerate(unique_operations)
}
default_operation = unique_operations[-1]
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
                value=default_columns,  # Default selected column(s)
                multi=True,  # Allows multiple selections
                clearable=False,
                className="dark-dropdown"  # Apply CSS class
            )
        ], style={"width": "25%"}),
        html.Div([
            html.Label("Select Operations:", style={"color": "white"}),
            dcc.Checklist(
                id="operation_filter",
                options=[{"label": f"Operation {op}", "value": op} for op in unique_operations],
                value=[default_operation],
                inline=True,
                style={"maxHeight": "150px", "overflowY": "scroll"}
            )
        ]),
        dcc.Graph(id="line_plot", style={"height": "80vh", "width": "95%"}),
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

    for col in selected_columns:
        # Remove the rows with NaN values in the selected column
        # df_selected = df.dropna(subset=[col])
        df[f"{col}_smooth"] = df[col].rolling(window=1, center=True).median().fillna(method="ffill")
        filtered_df = df[df["operation_number"].isin(selected_operations)]
        temp_fig = px.line(
            filtered_df,
            x="number_of_data_points",
            y=f"{col}_smooth",
            color="operation_number",
            labels={
                "number_of_data_points": "Time since start [Minutes]",
                f"{col}_smooth": f"{col} {input_key_unit}",
                "operation_number": "Operation Number"
            },
            color_discrete_map=color_map,
            hover_data={"Date": True, col: True, "number_of_data_points": True}
        )
        for trace in temp_fig["data"]:
            trace["name"] = f"{col} - " + trace["name"]
            fig.add_trace(trace)

    fig.update_xaxes(range=[0, 130], showline=True, linewidth=2, linecolor="white", mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor="white", mirror=True)
    fig.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
    fig.update_yaxes(showgrid=True, gridwidth=0.2, gridcolor="rgba(0, 255, 255, 0.25)")
    fig.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font={"color": "white"})
    # Modify the tick label font size
    fig.update_xaxes(tickfont=dict(size=18))
    fig.update_yaxes(tickfont=dict(size=18))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
