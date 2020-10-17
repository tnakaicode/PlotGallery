#!/usr/bin/env python
# coding: utf-8

# Matplotlib: colormap transformations
# ======================================================================
# 
# Operating on color vectors
# --------------------------
# 
# Ever wanted to manipulate an existing colormap? Here is a routine to apply a function to the look up table of a colormap:

# In[ ]:


import matplotlib
import numpy as np
import matplotlib.pyplot as plt

def cmap_map(function, cmap):
    """ Applies function (which should operate on vectors of shape 3: [r, g, b]), on colormap cmap.
    This routine will break any discontinuous points in a colormap.
    """
    cdict = cmap._segmentdata
    step_dict = {}
    # Firt get the list of points where the segments start or end
    for key in ('red', 'green', 'blue'):
        step_dict[key] = list(map(lambda x: x[0], cdict[key]))
    step_list = sum(step_dict.values(), [])
    step_list = np.array(list(set(step_list)))
    # Then compute the LUT, and apply the function to the LUT
    reduced_cmap = lambda step : np.array(cmap(step)[0:3])
    old_LUT = np.array(list(map(reduced_cmap, step_list)))
    new_LUT = np.array(list(map(function, old_LUT)))
    # Now try to make a minimal segment definition of the new LUT
    cdict = {}
    for i, key in enumerate(['red','green','blue']):
        this_cdict = {}
        for j, step in enumerate(step_list):
            if step in step_dict[key]:
                this_cdict[step] = new_LUT[j, i]
            elif new_LUT[j,i] != old_LUT[j, i]:
                this_cdict[step] = new_LUT[j, i]
        colorvector = list(map(lambda x: x + (x[1], ), this_cdict.items()))
        colorvector.sort()
        cdict[key] = colorvector

    return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)


# Lets try it out: I want a jet colormap, but lighter, so that I can plot
# things on top of it:

# In[ ]:


light_jet = cmap_map(lambda x: x/2 + 0.5, matplotlib.cm.jet)

x, y = np.mgrid[1:2, 1:10:0.01]
plt.figure(figsize=[15, 1])
plt.imshow(y, cmap=light_jet, aspect='auto')
plt.axis('off')
plt.show()


# ![](files/attachments/Matplotlib_ColormapTransformations/jet_light.png)

# Similarly, if a darker jet colormap is desired:

# In[ ]:


dark_jet = cmap_map(lambda x: x*0.75, matplotlib.cm.jet)

x, y = np.mgrid[1:2, 1:10:0.01]
plt.figure(figsize=[15, 1])
plt.imshow(y, cmap=dark_jet, aspect='auto')
plt.axis('off')
plt.show()


# ![](files/attachments/Matplotlib_ColormapTransformations/jet_dark.png)

# As a comparison, this is what the original jet looks like:
# ![](files/attachments/Matplotlib_ColormapTransformations/jet_original.png)

# Operating on indices
# --------------------
# 
# OK, but what if you want to change the indices of a colormap, but not
# its colors.

# In[ ]:


def cmap_xmap(function, cmap):
    """ Applies function, on the indices of colormap cmap. Beware, function
    should map the [0, 1] segment to itself, or you are in for surprises.

    See also cmap_xmap.
    """
    cdict = cmap._segmentdata
    function_to_map = lambda x : (function(x[0]), x[1], x[2])
    for key in ('red','green','blue'):
        cdict[key] = map(function_to_map, cdict[key])
        cdict[key].sort()
        assert (cdict[key][0]<0 or cdict[key][-1]>1), "Resulting indices extend out of the [0, 1] segment."

    return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)


# Discrete colormap
# -----------------
# 
# Here is how you can discretize a continuous colormap.

# In[ ]:


def cmap_discretize(cmap, N):
    """Return a discrete colormap from the continuous colormap cmap.
    
        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.
    """
    if type(cmap) == str:
        cmap = get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N+1)
    cdict = {}
    for ki, key in enumerate(('red','green','blue')):
        cdict[key] = [(indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in range(N+1)]
    # Return colormap object.
    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)


# So for instance, consider a discretized jet colormap with 6 colors:

# In[ ]:


discretized_jet = cmap_discretize(matplotlib.cm.jet, 6)

x, y = np.mgrid[1:2, 1:10:0.01]
plt.figure(figsize=[15, 1])
plt.imshow(y, cmap=discretized_jet, aspect='auto')
plt.axis('off')
plt.show()


# ![](files/attachments/Matplotlib_ColormapTransformations/jet_discretized.png)
