version_to_run = 3

if version_to_run == 1:
    import numpy as np
    from scipy.stats import gaussian_kde

    from bokeh.palettes import Blues9
    from bokeh.plotting import figure, show
    from bokeh.sampledata.autompg import autompg as df


    def kde(x, y, N):
        xmin, xmax = x.min(), x.max()
        ymin, ymax = y.min(), y.max()

        X, Y = np.mgrid[xmin:xmax:N*1j, ymin:ymax:N*1j]
        positions = np.vstack([X.ravel(), Y.ravel()])
        values = np.vstack([x, y])
        kernel = gaussian_kde(values)
        Z = np.reshape(kernel(positions).T, X.shape)

        return X, Y, Z

    x, y, z = kde(df.hp, df.mpg, 300)

    p = figure(height=400, x_axis_label="hp", y_axis_label="mpg",
            background_fill_color="#fafafa", tools="", toolbar_location=None,
            title="Kernel density estimation plot of HP vs MPG")
    p.grid.level = "overlay"
    p.grid.grid_line_color = "black"
    p.grid.grid_line_alpha = 0.05

    palette = Blues9[::-1]
    levels = np.linspace(np.min(z), np.max(z), 10)
    p.contour(x, y, z, levels[1:], fill_color=palette, line_color=palette)

    show(p)

elif version_to_run == 2:
    import numpy as np

    from bokeh.plotting import figure, show
    from bokeh.transform import linear_cmap
    from bokeh.util.hex import hexbin

    n = 50000
    x = np.random.standard_normal(n)
    y = np.random.standard_normal(n)

    bins = hexbin(x, y, 0.1)

    p = figure(title="Manual hex bin for 50000 points", tools="wheel_zoom,pan,reset",
            match_aspect=True, background_fill_color='#440154')
    p.grid.visible = False

    p.hex_tile(q="q", r="r", size=0.1, line_color=None, source=bins,
            fill_color=linear_cmap('counts', 'Viridis256', 0, max(bins.counts)))

    show(p)

elif version_to_run == 3:
    import numpy as np

    from bokeh.models import HoverTool
    from bokeh.plotting import figure, show

    n = 500
    x = 2 + 2*np.random.standard_normal(n)
    y = 2 + 2*np.random.standard_normal(n)

    p = figure(title="Hexbin for 500 points", match_aspect=True,
               tools="wheel_zoom,reset", background_fill_color='#440154')
    p.grid.visible = False

    r, bins = p.hexbin(x, y, size=0.5, hover_color="pink", hover_alpha=0.8)

    p.circle(x, y, color="white", size=1)

    p.add_tools(HoverTool(
        tooltips=[("count", "@c"), ("(q,r)", "(@q, @r)")],
        mode="mouse", point_policy="follow_mouse", renderers=[r]
    ))

    show(p)
