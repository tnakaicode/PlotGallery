import numpy as np
import pandas as pd
import argiope

ELEMENTS = argiope.mesh.ELEMENTS

mesh = argiope.mesh.read_msh("data/demo.msh")

data = mesh.elements.data
  element_faces = []
  for element in data.iterrows():
    faces = ELEMENTS[element.etype]
    
