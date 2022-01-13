#!/usr/bin/env python
# coding: utf-8

# # Visualize orbital data with Cesium
# 
# Poliastro allows users to easily convert orbital data to CZML, a JSON format primarily used in applications running Cesium

# ## Dependencies
# 
# You will only need poliastro (obviously) and czml3, a library for easily creating and using CZML packets
# 
# ``pip install poliastro czml3``

# ## Our first example: The Molniya orbit
# 
# We'll start off by using one of the readily usable poliastro examples. Of course, you can use any poliastro ``Orbit`` object.

# In[1]:


from poliastro.czml.extract_czml import CZMLExtractor


# In[2]:


from poliastro.examples import molniya


# To initialize the extractor, you'll only need the starting and ending epoch of the time period you wish to visualize and the number of sample points. The larger the sample point size, the more accurate the trajectory and the bigger your packets. Finding that sweet spot between reasonable package size and visual accuracy depends on the specific orbit. Generally, you'll need a bigger sample for faster satellites. You could also "break" your orbit into different parts and define the sample size individually (for example, this could be useful when the satellite accelerates within a certain time interval).
# 
# For this specific example, we're only interested in a single orbital period.

# In[3]:


start_epoch = molniya.epoch
end_epoch = molniya.epoch + molniya.period
N = 80


# In[4]:


extractor = CZMLExtractor(
        start_epoch,
        end_epoch,
        N
    )


# To add an orbit you can simply call ``add_orbit`` and pass your ``Orbit`` along with an optional precision parameter (``rtol``). However, there are also many optional parameters you can pass to the extractor to specify the visual characteristics of your trajectory:
# 
# #### Id parameters:
# 
# ``id_name``: The orbit id name
# 
# ``id_description``: The orbit's description
# 
# #### Path parameters:
# 
# ``path_width``: The trajectorie's width. It's defined in pixels and defaults to ``1.0``
# 
# ``path_show``: Whether the trajectorie's path is visible (true by default)
# 
# ``path_color``: The trajectorie's color, a simple list with the rgba values (e.g. ``[45, 30, 50, 255]``)
# 
# #### Label parameters:
# 
# ``label_text``: The label text; the text that appears besides the orbit. 
# 
# ``label_show``: Whether the label is visible (true by default)
# 
# ``label_fill_color``: The fill color of the label , a simple list with the rgba values
# 
# ``label_outline_color``: The fill color of the label , a simple list with the rgba values
# 
# ``label_font``:  The font properties (CSS syntax)
# 
# #### Groundtrack parameters:
# 
# ``show_groundtrack``: Whether the groundtrack is visible (true by default)
# 
# ``groundtrack_lead_time``: The time the animation is ahead of the real-time groundtrack
# 
# ``groundtrack_trail_time``: The time the animation is behind the real-time groundtrack
# 
# ``groundtrack_width``: The groundtrack width
# 
# ``groundtrack_color``: The groundtrack color. By default, it is set to the trajectory's color
# 

# In[5]:


extractor.add_orbit(molniya,
              id_name="MolniyaOrbit",
              path_width=2,
              label_text="Molniya", 
              label_fill_color=[125, 80, 120, 255]
             )


# You can now export the extractor packets by simply calling ``extractor.packets`` and load it to the Cesium app as described [here](https://github.com/poliastro/cesium-app)

# In[6]:


extractor.packets


# ## Landing on Mars
# 
# You can customize the attractor of your orbit by defining any valid ellipsoid with the help of poliastro's ``Body`` class. For your convenience, poliastro offers a pre-defined list of all the major planetary bodies of the solar system so you can simply import them.

# In[7]:


from poliastro.bodies import Mars


# Of course, when defining a new attractor you want to be able to identify something other than it's shape. For this reason, the extractor allows you to easily set the UV map by simply providing a valid URL.

# In[8]:


mars_uv = "https://upload.wikimedia.org/wikipedia/commons/f/fd/Mars_2020_LandingSites_Final_8-full.jpg"


# In[9]:


extractor = CZMLExtractor(
        start_epoch,
        end_epoch,
        N,
        attractor=Mars,
        pr_map=mars_uv
)


# In[10]:


extractor.packets


# ## Return to Flatland
# 
# Instead of a 3D globe you may want to visualize your orbit as a 2D projection instead. In this case you can simply set ``scene3D`` to ``false`` and Cesium will automatically render the scene's orthographic projection. This can be of use when plotting animated groundtracks as we'll see in the next section

# In[11]:


extractor = CZMLExtractor(
        start_epoch,
        end_epoch,
        N,
        scene3D=False
)


# In[12]:


extractor.packets


# ## Ground track plotting
# 
# Another useful feature the extractor offers, is the ability to plot the ground track of an orbit. You can set the groundtrack by setting the aforementioned ``groundtrack_show`` parameter to true. Note that this also works in 2D view. 

# In[13]:


extractor = CZMLExtractor(
        start_epoch,
        end_epoch,
        N
    )


# In[14]:


extractor.add_orbit(molniya,
              groundtrack_show=True,
              groundtrack_lead_time=20,
              groundtrack_trail_time=20
             )


# In[15]:


extractor.packets


# In[ ]:




