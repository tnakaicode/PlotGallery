# 2D Histogram Contours or Density Contours

# A 2D histogram contour plot, also known as a density contour plot, is a 2-dimensional generalization of a [histogram](/python/histograms/) which resembles a [contour plot](/python/contour-plots/) but is computed by grouping a set of points specified by their `x` and `y` coordinates into bins, and applying an aggregation function such as `count` or `sum` (if `z` is provided) to compute the value to be used to compute contours. This kind of visualization (and the related [2D histogram, or density heatmap](/python/2d-histogram/)) is often used to manage over-plotting, or situations where showing large data sets as [scatter plots](/python/line-and-scatter/) would result in points overlapping each other and hiding patterns.

# Density Contours with Plotly Express

# [Plotly Express](/python/plotly-express/) is the easy-to-use, high-level interface to Plotly, which [operates on a variety of types of data](/python/px-arguments/) and produces [easy-to-style figures](/python/styling-plotly-express/). The Plotly Express function `density_contour()` can be used to produce density contours.

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

df = px.data.tips()
fig = px.density_contour(df, x="total_bill", y="tip")
fig.show()


# Marginal plots can be added to visualize the 1-dimensional distributions of the two variables. Here we use a marginal [`histogram`](/python/histograms/). Other allowable values are `violin`, `box` and `rug`.

df = px.data.tips()
fig = px.density_contour(df, x="total_bill", y="tip",
                         marginal_x="histogram", marginal_y="histogram")
fig.show()

# Density contours can also be [faceted](/python/facet-plots/) and [discretely colored](/python/discrete-color/):

df = px.data.tips()
fig = px.density_contour(df, x="total_bill", y="tip",
                         facet_col="sex", color="smoker")
fig.show()


# Plotly Express density contours can be [continuously-colored](/python/colorscales/) and labeled:

df = px.data.tips()

fig = px.density_contour(df, x="total_bill", y="tip")
fig.update_traces(contours_coloring="fill", contours_showlabels=True)
fig.show()


# Other aggregation functions than `count`

# By passing in a `z` value and a `histfunc`, density contours can perform basic aggregation operations. Here we show average Sepal Length grouped by Petal Length and Petal Width for the Iris dataset.

df = px.data.iris()
fig = px.density_contour(df, x="petal_length",
                         y="petal_width", z="sepal_length", histfunc="avg")
fig.show()


# 2D Histograms with Graph Objects

# To build this kind of figure with [graph objects](/python/graph-objects/) without using Plotly Express, we can use the `go.Histogram2d` class.

# Basic 2D Histogram Contour


np.random.seed(1)

x = np.random.uniform(-1, 1, size=500)
y = np.random.uniform(-1, 1, size=500)

fig = go.Figure(go.Histogram2dContour(
    x=x,
    y=y
))
fig.show()


# 2D Histogram Contour Colorscale

x = np.random.uniform(-1, 1, size=500)
y = np.random.uniform(-1, 1, size=500)

fig = go.Figure(go.Histogram2dContour(
    x=x,
    y=y,
    colorscale='Blues'
))
fig.show()


# 2D Histogram Contour Styled

x = np.random.uniform(-1, 1, size=500)
y = np.random.uniform(-1, 1, size=500)

fig = go.Figure(go.Histogram2dContour(
    x=x,
    y=y,
    colorscale='Jet',
    contours=dict(
        showlabels=True,
        labelfont=dict(
                family='Raleway',
                color='white'
                )
    ),
    hoverlabel=dict(
        bgcolor='white',
        bordercolor='black',
        font=dict(
            family='Raleway',
            color='black'
        )
    )

))

fig.show()


# 2D Histogram Contour Subplot

t = np.linspace(-1, 1.2, 2000)
x = (t**3) + (0.3 * np.random.randn(2000))
y = (t**6) + (0.3 * np.random.randn(2000))

fig = go.Figure()
fig.add_trace(go.Histogram2dContour(
    x=x,
    y=y,
    colorscale='Blues',
    reversescale=True,
    xaxis='x',
    yaxis='y'
))
fig.add_trace(go.Scatter(
    x=x,
    y=y,
    xaxis='x',
    yaxis='y',
    mode='markers',
    marker=dict(
        color='rgba(0,0,0,0.3)',
        size=3
    )
))
fig.add_trace(go.Histogram(
    y=y,
    xaxis='x2',
    marker=dict(
        color='rgba(0,0,0,1)'
    )
))
fig.add_trace(go.Histogram(
    x=x,
    yaxis='y2',
    marker=dict(
        color='rgba(0,0,0,1)'
    )
))

fig.update_layout(
    autosize=False,
    xaxis=dict(
        zeroline=False,
        domain=[0, 0.85],
        showgrid=False
    ),
    yaxis=dict(
        zeroline=False,
        domain=[0, 0.85],
        showgrid=False
    ),
    xaxis2=dict(
        zeroline=False,
        domain=[0.85, 1],
        showgrid=False
    ),
    yaxis2=dict(
        zeroline=False,
        domain=[0.85, 1],
        showgrid=False
    ),
    height=600,
    width=600,
    bargap=0,
    hovermode='closest',
    showlegend=False
)

fig.show()


# Reference
# See https://plotly.com/python/reference/#histogram2dcontour for more information and chart attribute options!
