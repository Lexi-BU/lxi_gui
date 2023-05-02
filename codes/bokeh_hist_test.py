import numpy as np
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import HoverTool

# Read in the data from the CSV file
df = pd.read_csv("/home/cephadrius/Desktop/git/Lexi-BU/lexi_term/data/GSFC/processed_data/csv/2022_04_21_1431_LEXI_raw_LEXI_unit_1_mcp_unit_1_eBox-1987_sci_output.csv", index_col=False)

# Set the "Date" column as the index
df.set_index("Date", inplace=True)

# Mask all "x_mcp_lin" and "y_mcp_lin" values larger than 7 or smaller than -7
df = df[(df.x_mcp_lin > -7) & (df.x_mcp_lin < 7) & (df.y_mcp_lin > -7) & (df.y_mcp_lin < 7)]

n = 200
x = df.x_mcp_lin
y = df.y_mcp_lin

p = figure(title="MCP data", match_aspect=True, background_fill_color='#000000')
p.grid.visible = False

r, bins = p.hexbin(x, y, size=0.5, hover_color="pink", hover_alpha=0.8, palette="Cividis256")

# Add a color bar to the bokeh plot
color_bar = p.hex_tile(q="q", r="r", size=0.5, line_color=None, source=bins,
        fill_color="color")


# p.circle(x, y, color="white", size=1)

p.add_tools(HoverTool(
    tooltips=[("count", "@c"), ("(q,r)", "(@q, @r)")],
    mode="mouse", point_policy="follow_mouse", renderers=[r]
))

show(p)
