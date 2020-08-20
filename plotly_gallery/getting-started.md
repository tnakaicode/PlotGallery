---
jupyter:
  jupytext:
    notebook_metadata_filter: all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: "1.1"
      jupytext_version: 1.1.1
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
    description: Getting Started with Plotly for Python.
    has_thumbnail: false
    language: python
    layout: base
    name: Getting Started with Plotly
    page_type: u-guide
    permalink: python/getting-started/
    redirect_from:
      - python/getting_started/
      - /python/pytables/
---

<!-- #region -->

### Overview

The [`plotly` Python library](/python/) is an interactive, [open-source](/python/is-plotly-free) plotting library that supports over 40 unique chart types covering a wide range of statistical, financial, geographic, scientific, and 3-dimensional use-cases.

Built on top of the Plotly JavaScript library ([plotly.js](https://plotly.com/javascript/)), `plotly` enables Python users to create beautiful interactive web-based visualizations that can be displayed in Jupyter notebooks, saved to standalone HTML files, or served as part of pure Python-built web applications using Dash. The `plotly` Python library is sometimes referred to as "plotly.py" to differentiate it from the JavaScript library.

Thanks to deep integration with the [orca](https://github.com/plotly/orca) image export utility, `plotly` also provides great support for non-web contexts including desktop editors (e.g. QtConsole, Spyder, PyCharm) and static document publishing (e.g. exporting notebooks to PDF with high-quality vector images).

This Getting Started guide explains how to install `plotly` and related optional pages. Once you've installed, you can use our documentation in three main ways:

1. You jump right in to **examples** of how to make [basic charts](/python/basic-charts/), [statistical charts](/python/statistical-charts/), [scientific charts](/python/scientific-charts/), [financial charts](/python/financial-charts/), [maps](/python/maps/), and [3-dimensional charts](/python/3d-charts/).
2. If you prefer to learn about the **fundamentals** of the library first, you can read about [the structure of figures](/python/figure-structure/), [how to create and update figures](/python/creating-and-updating-figures/), [how to display figures](/python/renderers/), [how to theme figures with templates](/python/templates/), [how to export figures to various formats](/python/static-image-export/) and about [Plotly Express, the high-level API](/python/plotly-express/) for doing all of the above.
3. You can check out our exhaustive **reference** guides: the [Python API reference](/python-api-reference) or the [Figure Reference](/python/reference)

For information on using Python to build web applications containing plotly figures, see the [_Dash User Guide_](https://dash.plotly.com/).

We also encourage you to join the [Plotly Community Forum](http://community.plotly.com/) if you want help with anything related to `plotly`.

### Installation

`plotly` may be installed using pip...

```
$ pip install plotly==4.9.0
```

or conda.

```
$ conda install -c plotly plotly=4.9.0
```

This package contains everything you need to write figures to standalone HTML files.

> Note: **No internet connection, account, or payment is required to use plotly.py.** Prior to version 4, this library could operate in either an "online" or "offline" mode. The documentation tended to emphasize the online mode, where graphs get published to the Chart Studio web service. In version 4, all "online" functionality was removed from the `plotly` package and is now available as the separate, optional, `chart-studio` package (See below). **plotly.py version 4 is "offline" only, and does not include any functionality for uploading figures or data to cloud services.**

<!-- #endregion -->

```python
import plotly.graph_objects as go
fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
fig.write_html('first_figure.html', auto_open=True)
```

<!-- #region -->

#### Jupyter Notebook Support

For use in the classic [Jupyter Notebook](https://jupyter.org/), install the `notebook` and `ipywidgets`
packages using pip...

```
$ pip install "notebook>=5.3" "ipywidgets>=7.2"
```

or conda.

```
$ conda install "notebook>=5.3" "ipywidgets>=7.2"
```

These packages contain everything you need to run a Jupyter notebook...

```
$ jupyter notebook
```

and display plotly figures inline using the notebook renderer...

<!-- #endregion -->

```python
import plotly.graph_objects as go
fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
fig.show()
```

or using `FigureWidget` objects.

```python
import plotly.graph_objects as go
fig = go.FigureWidget(data=go.Bar(y=[2, 3, 1]))
fig
```

<!-- #region -->

See [_Displaying Figures in Python_](/python/renderers/) for more information on the renderers framework, and see [_Plotly FigureWidget Overview_](/python/figurewidget/) for more information on using `FigureWidget`.

#### JupyterLab Support (Python 3.5+)

For use in [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/), install the `jupyterlab` and `ipywidgets`
packages using pip...

```
$ pip install jupyterlab "ipywidgets>=7.5"
```

or conda.

```
$ conda install jupyterlab "ipywidgets=7.5"
```

Then run the following commands to install the required JupyterLab extensions (note that this will require [`node`](https://nodejs.org/) to be installed):

```
# JupyterLab renderer support
jupyter labextension install jupyterlab-plotly@4.9.0

# OPTIONAL: Jupyter widgets extension
jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget@4.9.0
```

These packages contain everything you need to run JupyterLab...

```
$ jupyter lab
```

and display plotly figures inline using the `plotly_mimetype` renderer...

<!-- #endregion -->

```python
import plotly.graph_objects as go
fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
fig.show()
```

or using `FigureWidget` objects (if the "OPTIONAL" step above was executed).

```python
import plotly.graph_objects as go
fig = go.FigureWidget(data=go.Bar(y=[2, 3, 1]))
fig
```

Please check out our [Troubleshooting guide](/python/troubleshooting/) if you run into any problems with JupyterLab.

<!-- #region -->

See [_Displaying Figures in Python_](/python/renderers/) for more information on the renderers framework, and see [_Plotly FigureWidget Overview_](/python/figurewidget/) for more information on using `FigureWidget`.

### Static Image Export

plotly.py supports [static image export](https://plotly.com/python/static-image-export/),
using the either the [`kaleido`](https://github.com/plotly/Kaleido)
package (recommended, supported as of `plotly` version 4.9) or the [orca](https://github.com/plotly/orca)
command line utility (legacy as of `plotly` version 4.9).

#### Kaleido

The [`kaleido`](https://github.com/plotly/Kaleido) package has no dependencies and can be installed
using pip...

```
$ pip install -U kaleido
```

or conda.

```
$ conda install -c plotly python-kaleido
```

#### Orca

While Kaleido is now the recommended image export approach because it is easier to install
and more widely compatible, [static image export](https://plotly.com/python/static-image-export/)
can also be supported
by the legacy [orca](https://github.com/plotly/orca) command line utility and the
 [`psutil`](https://github.com/giampaolo/psutil) Python package.

These dependencies can both be installed using conda:

```
conda install -c plotly plotly-orca==1.3.1 psutil
```

Or, `psutil` can be installed using pip...

```
pip install psutil
```

and orca can be installed according to the instructions in the [orca README](https://github.com/plotly/orca).

#### Extended Geo Support

Some plotly.py features rely on fairly large geographic shape files. The county
choropleth figure factory is one such example. These shape files are distributed as a
separate `plotly-geo` package. This package can be installed using pip...

```
$ pip install plotly-geo==1.0.0
```

or conda.

```
$ conda install -c plotly plotly-geo=1.0.0
```

See [_USA County Choropleth Maps in Python_](/python/county-choropleth/) for more information on the county choropleth figure factory.

#### Chart Studio Support

The `chart-studio` package can be used to upload plotly figures to Plotly's Chart
Studio Cloud or On-Prem services. This package can be installed using pip...

```
$ pip install chart-studio==1.0.0
```

or conda.

```
$ conda install -c plotly chart-studio=1.0.0
```

> **Note:** This package is optional, and if it is not installed it is not possible for figures to be uploaded to the Chart Studio cloud service.

### Where to next?

Once you've installed, you can use our documentation in three main ways:

1. You jump right in to **examples** of how to make [basic charts](/python/basic-charts/), [statistical charts](/python/statistical-charts/), [scientific charts](/python/scientific-charts/), [financial charts](/python/financial-charts/), [maps](/python/maps/), and [3-dimensional charts](/python/3d-charts/).
2. If you prefer to learn about the **fundamentals** of the library first, you can read about [the structure of figures](/python/figure-structure/), [how to create and update figures](/python/creating-and-updating-figures/), [how to display figures](/python/renderers/), [how to theme figures with templates](/python/templates/), [how to export figures to various formats](/python/static-image-export/) and about [Plotly Express, the high-level API](/python/plotly-express/) for doing all of the above.
3. You can check out our exhaustive **reference** guides: the [Python API reference](/python-api-reference) or the [Figure Reference](/python/reference)

For information on using Python to build web applications containing plotly figures, see the [_Dash User Guide_](https://dash.plotly.com/).

We also encourage you to join the [Plotly Community Forum](http://community.plotly.com/) if you want help with anything related to `plotly`.

<!-- #endregion -->
