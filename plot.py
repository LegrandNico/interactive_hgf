from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.palettes import Dark2_5
from bokeh.models import LinearAxis, Range1d, RangeTool
from pyhgf.model import HGF
import itertools
from typing import Tuple
import numpy as np


def plot_trajectories(
    hgf: "HGF",
    ci: bool = True,
    surprise: bool = True,
    figsize: Tuple[int, int] = 200,
    slider: bool = True,
):
    r"""Plot the trajectories of the nodes' sufficient statistics and surprise.

    This function will plot :math:`\hat{mu}`, :math:`\¨hat{pi}` (converted into standard
    deviation) and the surprise at each level of the node structure.

    Parameters
    ----------
    hgf : :py:class:`pyhgf.model.HGF`
        Instance of the HGF model.
    ci : bool
        Show the uncertainty aroud the values estimates (standard deviation).
    surprise : bool
        If `True` plot each node's surprise together witt the sufficient statistics.
        If `False`, only the input node's surprise is depicted.
    figsize : tuple
        The width and height of the figure. Defaults to `(18, 9)` for a 2-levels model,
        or to `(18, 12)` for a 3-levels model.
    slider : bool
        If `True`, add a slider to zoom in/out in the signal (only working with
        bokeh backend).

    Returns
    -------
    cols

    """
    trajectories_df = hgf.to_pandas()
    n_nodes = trajectories_df.columns.str.contains("_muhat").sum()
    palette = itertools.cycle(Dark2_5)

    cols = []

    # loop over the node idexes
    # -------------------------
    for i in range(n_nodes, 0, -1):

        # use different colors for each nodes
        color = next(palette)

        # extract the sufficient statistics from the data frame
        mu = trajectories_df[f"node_{i}_muhat"]
        pi = trajectories_df[f"node_{i}_pihat"]

        level_plot = figure(
            title=f"Node {i}",
            sizing_mode="stretch_width",
            height=figsize,
            x_axis_label="Time",
            y_axis_label="Input",
            output_backend="webgl",
            x_range=level_plot.x_range if len(cols) != 0  else (trajectories_df.time.iloc[0], trajectories_df.time.iloc[-1])
        )

        # input node
        # ----------
        if i == 1:
            if hgf.model_type == "continuous":
                level_plot.circle(
                    trajectories_df.time,
                    trajectories_df.observation,
                    size=2,
                    legend_label="Input",
                    fill_color="#2a2a2a",
                    line_color="#2a2a2a",
                    alpha=0.5,
                )
            elif hgf.model_type == "binary":
                level_plot.circle(
                    x=trajectories_df.time,
                    y=trajectories_df.observation,
                    legend_label="Input",
                    fill_color="#4c72b0",
                    line_color="grey",
                    alpha=0.4,
                    edgecolors="k",
                    size=10,
                )

        # node parameters
        # ---------------
        # plotting mean
        level_plot.line(
            trajectories_df.time,
            mu,
            color=color,
            line_width=0.5,
        )

        # plotting standard deviation
        if ci is True:

            # if this is the first level of a binary model do not show CI
            if not (hgf.model_type == "binary") & (i == 1):
                sd = np.sqrt(1 / pi)
                level_plot.varea(
                    x=trajectories_df.time,
                    y1=trajectories_df[f"node_{i}_muhat"] - sd,
                    y2=trajectories_df[f"node_{i}_muhat"] + sd,
                    alpha=0.4,
                    color=color,
                )
                level_plot.y_range = Range1d(
                (trajectories_df[f"node_{i}_muhat"] - sd).min(), 
                (trajectories_df[f"node_{i}_muhat"] + sd).max()
            )

        # plotting surprise
        if surprise:
            level_plot.extra_y_ranges['surprise'] = Range1d(
                trajectories_df[f"node_{i}_surprise"].min(), 
                trajectories_df[f"node_{i}_surprise"].max()
            )
            level_plot.line(
                x=trajectories_df.time,
                y=trajectories_df[f"node_{i}_surprise"],
                color="#2a2a2a",
                line_width=0.5,
                y_range_name="surprise"
            )
            level_plot.varea(
                x=trajectories_df.time,
                y1=trajectories_df[f"node_{i}_surprise"],
                y2=trajectories_df[f"node_{i}_surprise"].min(),
                color="#7f7f7f",
                alpha=0.2,
                y_range_name="surprise"
            )
            ax2 = LinearAxis(y_range_name="surprise", axis_label="Surprise")
            level_plot.add_layout(ax2, 'right')
        
        cols.append(level_plot)

    # global surprise
    # ---------------
    surprise_plot = figure(
        title=f"Global surprise: {round(hgf.surprise(), 2)}",
        sizing_mode="stretch_width",
        height=figsize,
        x_axis_label="Time",
        y_axis_label="Surprise",
        output_backend="webgl",
        x_range=level_plot.x_range
    )
    surprise_plot.varea(
        x=trajectories_df.time,
        y1=trajectories_df.surprise,
        y2=trajectories_df.surprise.min(),
        color="#7f7f7f",
        alpha=0.2,
    )
    surprise_plot.line(
        trajectories_df.time,
        trajectories_df.surprise,
        color="#2a2a2a",
        line_width=0.5,
    )
    cols.append(surprise_plot)

    # slider
    # ------
    if slider is True:
        select = figure(
            title="Select the time range",
            y_range=level_plot.y_range,
            y_axis_type=None,
            height=int(figsize * 0.4),
            sizing_mode="stretch_width",
            output_backend="webgl",
            tools="",
            toolbar_location=None,
            background_fill_color="#efefef",
        )

        range_tool = RangeTool(x_range=surprise_plot.x_range)
        range_tool.overlay.fill_color = "navy"
        range_tool.overlay.fill_alpha = 0.2

        select.line(trajectories_df.time, trajectories_df.observation)
        select.ygrid.grid_line_color = None
        select.add_tools(range_tool)
        select.toolbar.active_multi = range_tool

        cols.append(select)

    return column(*cols, sizing_mode="stretch_width")