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
    version: 3.7.3
  plotly:
    description: How to display image data in Python with Plotly.
    display_as: scientific
    has_thumbnail: true
    ipynb: ~notebook_demo/34
    language: python
    layout: base
    name: Imshow
    order: 3
    page_type: example_index
    permalink: python/imshow/
    thumbnail: thumbnail/imshow.jpg
    v4upgrade: true
---

This tutorial shows how to display and explore image data. If you would like
instead a logo or static image, use `go.layout.Image` as explained
[here](/python/images).

### Displaying RBG image data with px.imshow

`px.imshow` displays multichannel (RGB) or single-channel ("grayscale") image data.

```python
import plotly.express as px
import numpy as np
img_rgb = np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
                    [[0, 255, 0], [0, 0, 255], [255, 0, 0]]
                   ], dtype=np.uint8)
fig = px.imshow(img_rgb)
fig.show()
```

### Read image arrays from image files

In order to create a numerical array to be passed to `px.imshow`, you can use a third-party library like [PIL](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.open), [scikit-image](https://scikit-image.org/docs/dev/user_guide/getting_started.html) or [opencv](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_image_display/py_image_display.html). We show below how to open an image from a file with `skimage.io.imread`, and alternatively how to load a demo image from `skimage.data`.

```python
import plotly.express as px
from skimage import io
img = io.imread('https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Crab_Nebula.jpg/240px-Crab_Nebula.jpg')
fig = px.imshow(img)
fig.show()
```

```python
import plotly.express as px
from skimage import data
img = data.astronaut()
fig = px.imshow(img)
fig.show()
```

### Display single-channel 2D data as a heatmap

For a 2D image, `px.imshow` uses a colorscale to map scalar data to colors. The default colorscale is the one of the active template (see [the tutorial on templates](/python/templates/)).

```python
import plotly.express as px
import numpy as np
img = np.arange(15**2).reshape((15, 15))
fig = px.imshow(img)
fig.show()
```

### Choose the colorscale to display a single-channel image

You can customize the [continuous color scale](/python/colorscales/) just like with any other Plotly Express function:

```python
import plotly.express as px
import numpy as np
img = np.arange(100).reshape((10, 10))
fig = px.imshow(img, color_continuous_scale='Viridis')
fig.show()
```

You can use this to make the image grayscale as well:

```python
import plotly.express as px
import numpy as np
img = np.arange(100).reshape((10, 10))
fig = px.imshow(img, color_continuous_scale='gray')
fig.show()
```

### Hiding the colorbar and axis labels

See the [continuous color](/python/colorscales/) and [cartesian axes](/python/axes/) pages for more details.

```python
import plotly.express as px
from skimage import data
img = data.camera()
fig = px.imshow(img, color_continuous_scale='gray')
fig.update_layout(coloraxis_showscale=False)
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
fig.show()
```

### Customizing the axes and labels on a single-channel image

You can use the `x`, `y` and `labels` arguments to customize the display of a heatmap, and use `.update_xaxes()` to move the x axis tick labels to the top:

```python
import plotly.express as px
data=[[1, 25, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, 5, 20]]
fig = px.imshow(data,
                labels=dict(x="Day of Week", y="Time of Day", color="Productivity"),
                x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                y=['Morning', 'Afternoon', 'Evening']
               )
fig.update_xaxes(side="top")
fig.show()
```

### Display an xarray image with px.imshow

[xarrays](http://xarray.pydata.org/en/stable/) are labeled arrays (with labeled axes and coordinates). If you pass an xarray image to `px.imshow`, its axes labels and coordinates will be used for axis titles. If you don't want this behavior, you can pass `img.values` which is a NumPy array if `img` is an xarray. Alternatively, you can override axis titles hover labels and colorbar title using the `labels` attribute, as above.

```python
import plotly.express as px
import xarray as xr
# Load xarray from dataset included in the xarray tutorial
airtemps = xr.tutorial.open_dataset('air_temperature').air.sel(lon=250.0)
fig = px.imshow(airtemps.T, color_continuous_scale='RdBu_r', origin='lower')
fig.show()
```

### Display an xarray image with square pixels

For xarrays, by default `px.imshow` does not constrain pixels to be square, since axes often correspond to different physical quantities (e.g. time and space), contrary to a plain camera image where pixels are square (most of the time). If you want to impose square pixels, set the parameter `aspect` to "equal" as below.

```python
import plotly.express as px
import xarray as xr
airtemps = xr.tutorial.open_dataset('air_temperature').air.isel(time=500)
colorbar_title = airtemps.attrs['var_desc'] + '<br>(%s)'%airtemps.attrs['units']
fig = px.imshow(airtemps, color_continuous_scale='RdBu_r', aspect='equal')
fig.show()
```

### Display multichannel image data with go.Image

It is also possible to use the `go.Image` trace from the low-level `graph_objects` API in order to display image data. Note that `go.Image` only accepts multichannel images. For single images, use [`go.Heatmap`](/python/heatmaps).

Note that the `go.Image` trace is different from the `go.layout.Image` class, which can be used for [adding background images or logos to figures](/python/images).

```python
import plotly.graph_objects as go
img_rgb = [[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
           [[0, 255, 0], [0, 0, 255], [255, 0, 0]]]
fig = go.Figure(go.Image(z=img_rgb))
fig.show()
```

### Defining the data range covered by the color range with zmin and zmax

The data range and color range are mapped together using the parameters `zmin` and `zmax`, which correspond respectively to the data values mapped to black `[0, 0, 0]` and white `[255, 255, 255]`, or to the extreme colors of the colorscale in the case on single-channel data.

For single-channel data, the defaults values of `zmin` and `zmax` used by `px.imshow` and `go.Heatmap` are the extrema of the data range. For multichannel data, `px.imshow` and `go.Image` use slightly different default values for `zmin` and `zmax`. For `go.Image`, the default value is `zmin=[0, 0, 0]` and `zmax=[255, 255, 255]`, no matter the data type. On the other hand, `px.imshow` adapts the default `zmin` and `zmax` to the data type:
- for integer data types, `zmin` and `zmax` correspond to the extreme values of the data type, for example 0 and 255 for `uint8`, 0 and 65535 for `uint16`, etc.
- for float numbers, the maximum value of the data is computed, and zmax is 1 if the max is smaller than 1, 255 if the max is smaller than 255, etc. (with higher thresholds 2**16 - 1 and 2**32 -1).

These defaults can be overriden by setting the values of `zmin` and `zmax`. For `go.Image`, `zmin` and `zmax` need to be given for all channels, whereas it is also possible to pass a scalar value (used for all channels) to `px.imshow`.

```python
import plotly.express as px
from skimage import data
img = data.astronaut()
# Increase contrast by clipping the data range between 50 and 200
fig = px.imshow(img, zmin=50, zmax=200)
# We customize the hovertemplate to show both the data and the color values
# See https://plotly.com/python/hover-text-and-formatting/#customize-tooltip-text-with-a-hovertemplate
fig.update_traces(hovertemplate="x: %{x} <br> y: %{y} <br> z: %{z} <br> color: %{color}")
fig.show()
```

```python
import plotly.express as px
from skimage import data
img = data.astronaut()
# Stretch the contrast of the red channel only, resulting in a more red image
fig = px.imshow(img, zmin=[50, 0, 0], zmax=[200, 255, 255])
fig.show()
```

### Ticks and margins around image data

```python
import plotly.express as px
from skimage import data
img = data.astronaut()
fig = px.imshow(img)
fig.update_layout(width=400, height=400, margin=dict(l=10, r=10, b=10, t=10))
fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
fig.show()
```

### Combining image charts and other traces

```python
import plotly.express as px
import plotly.graph_objects as go
from skimage import data
img = data.camera()
fig = px.imshow(img, color_continuous_scale='gray')
fig.add_trace(go.Contour(z=img, showscale=False,
                         contours=dict(start=0, end=70, size=70, coloring='lines'),
                         line_width=2))
fig.add_trace(go.Scatter(x=[230], y=[100], marker=dict(color='red', size=16)))
fig.show()
```

### Displaying an image and the histogram of color values

```python
from plotly.subplots import make_subplots
from skimage import data
img = data.chelsea()
fig = make_subplots(1, 2)
# We use go.Image because subplots require traces, whereas px functions return a figure
fig.add_trace(go.Image(z=img), 1, 1)
for channel, color in enumerate(['red', 'green', 'blue']):
    fig.add_trace(go.Histogram(x=img[..., channel].ravel(), opacity=0.5,
                               marker_color=color, name='%s channel' %color), 1, 2)
fig.update_layout(height=400)
fig.show()
```

### imshow and datashader

Arrays of rasterized values build by datashader can be visualized using
imshow. See the [plotly and datashader tutorial](/python/datashader/) for
examples on how to use plotly and datashader.


### Annotating image traces with shapes

_introduced in plotly 4.7_

It can be useful to add shapes to an image trace, for highlighting an object, drawing bounding boxes as part of a machine learning training set, or identifying seeds for a segmentation algorithm. 

In order to enable shape drawing, you need to
- define a dragmode corresponding to a drawing tool (`'drawline'`,`'drawopenpath'`, `'drawclosedpath'`, `'drawcircle'`, or `'drawrect'`)
- add modebar buttons corresponding to the drawing tools you wish to use.

The style of new shapes is specified by the `newshape` layout attribute. Shapes can be selected and modified after they have been drawn. More details and examples are given in the [tutorial on shapes](/python/shapes#drawing-shapes-on-cartesian-plots).

Drawing or modifying a shape triggers a `relayout` event, which [can be captured by a callback inside a Dash application](https://dash.plotly.com/interactive-graphing). 

```python
import plotly.express as px
from skimage import data
img = data.chelsea()
fig = px.imshow(img)
fig.add_annotation(
    x=0.5,
    y=0.9,
    text="Drag and draw annotations",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=20, font_color='cyan')
# Shape defined programatically
fig.add_shape(
    type='rect',
    x0=230, x1=290, y0=230, y1=280,
    xref='x', yref='y',
    line_color='cyan'
)
# Define dragmode, newshape parameters, amd add modebar buttons
fig.update_layout(
    dragmode='drawrect',
    newshape=dict(line_color='cyan'))
fig.show(config={'modeBarButtonsToAdd':['drawline',
                                        'drawopenpath',
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]})
```

#### Reference
See https://plotly.com/python/reference/#image for more information and chart attribute options!