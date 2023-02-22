# Import the required packages
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Div
from pyhgf import load_data
from .plot import plot_trajectories
from pyhgf.model import HGF
from bokeh.models import Dropdown, Slider

# load data
timeseries = load_data("continuous")

# set up widgets
# --------------

# model type
menu = [("Binary", "binary"), ("Continuous", "continuous")]
dropdown = Dropdown(label="Model type", menu=menu)

# omega values
slider1 = Slider(start=-20.0, end=5.0, value=-4, step=.1, title="Omega 1")
slider2 = Slider(start=-20.0, end=5.0, value=-4, step=.1, title="Omega 2")
slider3 = Slider(start=-20.0, end=20.0, value=1.04, step=.1, title="Mu 1")
slider4 = Slider(start=-20.0, end=20.0, value=0.0, step=.1, title="Mu 2")

# callbacks
# ---------
def fit_hgf(omega1, omega2, mu1, mu2):
    hgf = HGF(
    n_levels=2,
    model_type="continuous",
    initial_mu={"1": mu1, "2": mu2},
    initial_pi={"1": 1e2, "2": 1e1},
    omega={"1": omega1, "2": omega2},
    rho={"1": 0.0, "2": 0.0},
    kappas={"1": 1.0}, verbose=False).input_data(input_data=timeseries)
    return plot_trajectories(hgf)


def on_change(attrname, old, new):
    layout.children[2] = fit_hgf(slider1.value, slider2.value, slider3.value, slider4.value)

slider1.on_change('value', on_change)
slider2.on_change('value', on_change)
slider3.on_change('value', on_change)
slider4.on_change('value', on_change)


# set up layout
# Add a title message to the app
div = Div(
    text="""
        <h1>The Hierarchical Gaussian Filter</h1>
        """,
width=900,
height=60,
)
# Create layouts
app_title = div
widgets = column(
    row(slider1, slider2),
    row(slider3, slider4)
)
layout = column(
    app_title, 
    widgets, 
    fit_hgf(
        omega1=slider1.value, omega2=slider2.value, mu1=slider3.value, mu2=slider4.value
        )
    )

# initialize the app
curdoc().add_root(layout)
curdoc().title = "The Hierarchical Gaussian Filter"