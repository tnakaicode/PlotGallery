import numpy as np
import pandas as pd
import argiope
import time

ELEMENTS = argiope.mesh.ELEMENTS

t0 = time.time()
mesh = argiope.mesh.read_msh("data/demo.msh")
t1 = time.time()
print "# Loaded mesh in {0:.2f} s".format(t1 -t0)
out = mesh.elements.faces()
  
t2 = time.time()    
print "# Exported faces in {0:.2f} s".format(t2 -t1)

