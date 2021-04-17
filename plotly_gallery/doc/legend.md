---
jupyter:
  jupytext:
    notebook_metadata_filter: all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.4.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  language_info:
    codemirror_mode:
      name: ipython
      version: 3
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython3
    version: 3.7.7
  plotly:
    description: How to configure and style the legend in Plotly with Python.
    display_as: file_settings
    language: python
    layout: base
    name: Legends
    order: 14
    permalink: python/legend/
    redirect_from: python/horizontal-legend/
    thumbnail: thumbnail/legends.gif
---

### Trace Types, Legends and Color Bars

[Traces](/python/figure-structure) of most types can be optionally associated with a single legend item in the [legend](/python/legend/). Whether or not a given trace appears in the legend is controlled via the `showlegend` attribute. Traces which are their own subplots (see above) do not support this, with the exception of traces of type `pie` and `funnelarea` for which every distinct color represented in the trace gets a separate legend item. Users may show or hide traces by clicking or double-clicking on their associated legend item. Traces that support legend items also support the `legendgroup` attribute, and all traces with the same legend group are treated the same way during click/double-click interactions.

The fact that legend items are linked to traces means that when using [discrete color](/python/discrete-color/), a figure must have one trace per color in order to get a meaningful legend. [Plotly Express has robust support for discrete color](/python/discrete-color/) to make this easy.

Traces which support [continuous color](/python/colorscales/) can also be associated with color axes in the layout via the `coloraxis` attribute. Multiple traces can be linked to the same color axis. Color axes have a legend-like component called color bars. Alternatively, color axes can be configured within the trace itself.


### Legends with Plotly Express

[Plotly Express](/python/plotly-express/) is the easy-to-use, high-level interface to Plotly, which [operates on a variety of types of data](/python/px-arguments/) and produces [easy-to-style figures](/python/styling-plotly-express/).

Plotly Express functions will create one [trace](/python/figure-structure) per animation frame for each unique combination of data values mapped to discrete color, symbol, line-dash, facet-row and/or facet-column. Traces' `legendgroup` and `showlegend` attributed are set such that only one legend item appears per unique combination of discrete color, symbol and/or line-dash. The legend title is automatically set, and can be overrided with the `labels` keyword argument:

```python
import plotly.express as px

df = px.data.tips()
fig = px.scatter(df, x="total_bill", y="tip", color="sex", symbol="smoker", facet_col="time",
          labels={"sex": "Gender", "smoker": "Smokes"})
fig.show()
```

#### Showing and Hiding the Legend

By default the legend is displayed on Plotly charts with multiple traces, and this can be explicitly set with the `layout.showlegend` attribute:

```python
import plotly.express as px

df = px.data.tips()
fig = px.histogram(df, x="sex", y="total_bill", color="time",
                  title="Total Bill by Sex, Colored by Time")
fig.update_layout(showlegend=False)
fig.show()
```


### Legend Positioning

Legends have an anchor point, which can be set to a point within the legend using `layout.legend.xanchor` and `layout.legend.yanchor`. The coordinate of the anchor can be positioned with `layout.legend.x` and `layout.legend.y` in [paper coordinates](/python/figure-structure/). Note that the plot margins will grow so as to accomodate the legend. The legend may also be placed within the plotting area.

```python
import plotly.express as px

df = px.data.gapminder().query("year==2007")
fig = px.scatter(df, x="gdpPercap", y="lifeExp", color="continent",
    size="pop", size_max=45, log_x=True)

fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))

fig.show()
```

#### Horizontal Legends

The `layout.legend.orientation` attribute can be set to `"h"` for a horizontal legend. Here we also position it above the plotting area.

```python
import plotly.express as px

df = px.data.gapminder().query("year==2007")
fig = px.scatter(df, x="gdpPercap", y="lifeExp", color="continent",
    size="pop", size_max=45, log_x=True)

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

fig.show()
```

#### Styling Legends

Legends support many styling options.

```python
import plotly.express as px

df = px.data.gapminder().query("year==2007")
fig = px.scatter(df, x="gdpPercap", y="lifeExp", color="continent",
    size="pop", size_max=45, log_x=True)


fig.update_layout(
    legend=dict(
        x=0,
        y=1,
        traceorder="reversed",
        title_font_family="Times New Roman",
        font=dict(
            family="Courier",
            size=12,
            color="black"
        ),
        bgcolor="LightSteelBlue",
        bordercolor="Black",
        borderwidth=2
    )
)

fig.show()
```

### Legends with Graph Objects

When creating figures using [graph objects](/python/graph-objects/) without using [Plotly Express](/python/plotly-express/), legends must be manually configured using some of the options below.


#### Legend Item Names

Legend items appear per trace, and the legend item name is taken from the trace's `name` attribute.

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1, 2, 3, 4, 5],
    name="Positive"
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[5, 4, 3, 2, 1],
    name="Negative"
))

fig.show()
```

#### Legend titles

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1, 2, 3, 4, 5],
    name="Increasing"
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[5, 4, 3, 2, 1],
    name="Decreasing"
))

fig.update_layout(legend_title_text='Trend')
fig.show()
```

### Hiding Legend Items

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1, 2, 3, 4, 5],
    showlegend=False
))


fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[5, 4, 3, 2, 1],
))

fig.update_layout(showlegend=True)

fig.show()
```

#### Hiding the Trace Initially

Traces have a `visible` attribute. If set to `legendonly`, the trace is hidden from the graph implicitly. Click on the name in the legend to display the hidden trace.

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1, 2, 3, 4, 5],
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[5, 4, 3, 2, 1],
    visible='legendonly'
))

fig.show()
```

#### Size of Legend Items

In this example [itemsizing](https://plotly.com/python/reference/#layout-legend-itemsizing) attribute determines the legend items symbols remain constant, regardless of how tiny/huge the bubbles would be in the graph.

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1, 2, 3, 4, 5],
    mode='markers',
    marker={'size':10}
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[5, 4, 3, 2, 1],
    mode='markers',
    marker={'size':100}
))

fig.update_layout(legend= {'itemsizing': 'constant'})

fig.show()
```

#### Grouped Legend Items

Grouping legend items together by setting the `legendgroup` attribute of traces causes their legend entries to be next to each other, and clicking on any legend entry in the group will show or hide the whole group.

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[2, 1, 3],
    legendgroup="group",  # this can be any string, not just "group"
    name="first legend group",
    mode="markers",
    marker=dict(color="Crimson", size=10)
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[2, 2, 2],
    legendgroup="group",
    name="first legend group - average",
    mode="lines",
    line=dict(color="Crimson")
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[4, 9, 2],
    legendgroup="group2",
    name="second legend group",
    mode="markers",
    marker=dict(color="MediumPurple", size=10)
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[5, 5, 5],
    legendgroup="group2",
    name="second legend group - average",
    mode="lines",
    line=dict(color="MediumPurple")
))

fig.update_layout(title="Try Clicking on the Legend Items!")

fig.show()
```

You can also hide entries in grouped legends, preserving the grouped show/hide behaviour. This is what Plotly Express does with its legends.

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[2, 1, 3],
    legendgroup="group",  # this can be any string, not just "group"
    name="first legend group",
    mode="markers",
    marker=dict(color="Crimson", size=10)
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[2, 2, 2],
    legendgroup="group",
    name="first legend group - average",
    mode="lines",
    line=dict(color="Crimson"),
    showlegend=False,
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[4, 9, 2],
    legendgroup="group2",
    name="second legend group",
    mode="markers",
    marker=dict(color="MediumPurple", size=10)
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[5, 5, 5],
    legendgroup="group2",
    name="second legend group - average",
    mode="lines",
    line=dict(color="MediumPurple"),
    showlegend=False
))

fig.update_layout(title="Try Clicking on the Legend Items!")
fig.show()
```

### Legend items for continuous fields (2D and 3D)

Traces corresponding to 2D fields (e.g. `go.Heatmap`, `go.Histogram2d`) or 3D fields (e.g. `go.Isosurface`, `go.Volume`, `go.Cone`) can also appear in the legend. They come with legend icons corresponding to each trace type, which are colored using the same colorscale as the trace.

The example below explores a vector field using several traces. Note that you can click on legend items to hide or to select (with a double click) a specific trace. This will make the exploration of your data easier!

```python
import numpy as np
import plotly.graph_objects as go

# Define vector and scalar fields
x, y, z = np.mgrid[0:1:8j, 0:1:8j, 0:1:8j]
u =    np.sin(np.pi*x) * np.cos(np.pi*z)
v = -2*np.sin(np.pi*y) * np.cos(2*np.pi*z)
w = np.cos(np.pi*x)*np.sin(np.pi*z) + np.cos(np.pi*y)*np.sin(2*np.pi*z)
magnitude = np.sqrt(u**2 + v**2 + w**2)
mask1 = np.logical_and(y>=.4, y<=.6)
mask2 = y>.6

fig = go.Figure(go.Isosurface(
                      x=x.ravel(), y=y.ravel(), z=z.ravel(),
                      value=magnitude.ravel(),
                      isomin=1.9, isomax=1.9,
                      colorscale="BuGn",
                      name='isosurface'))


fig.add_trace(go.Cone(x=x[mask1], y=y[mask1], z=z[mask1],
                      u=u[mask1], v=v[mask1], w=w[mask1],
                      colorscale="Blues",
                      name='cones'
))
fig.add_trace(go.Streamtube(
                      x=x[mask2], y=y[mask2], z=z[mask2],
                      u=u[mask2], v=v[mask2], w=w[mask2],
                      colorscale="Reds",
                      name='streamtubes'
))
# Update all traces together
fig.update_traces(showlegend=True, showscale=False)
fig.update_layout(width=600, title_text='Exploration of a vector field using several traces')
fig.show()
```

#### Reference

See https://plotly.com/python/reference/#layout-legend for more information!
