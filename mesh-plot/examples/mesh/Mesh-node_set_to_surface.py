import numpy as np
import pandas as pd
import argiope
import time

ELEMENTS = argiope.mesh.ELEMENTS

t0 = time.time()
mesh = argiope.mesh.read_msh("data/dummy.msh")
t1 = time.time()
print "# Loaded mesh in {0:.2f} s".format(t1 -t0)
mesh.element_set_to_node_set("Top")
mesh.element_set_to_node_set(tag = "Top")
mesh.element_set_to_node_set(tag = "Bottom")
del mesh.elements.sets["Top"]
del mesh.elements.sets["Bottom"]
mesh.elements.data = mesh.elements.data[mesh.elements.data.etype != "Line2"] 
mesh.node_set_to_surface("Top")  
  
  
t2 = time.time()    
print "# Exported faces in {0:.2f} s".format(t2 -t1)
