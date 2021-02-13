#!/usr/bin/env python
# coding: utf-8

import os

from OCC.Display.SimpleGui import init_display
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
import ifcopenshell
import ifcopenshell.geom


ifc_filename = "./assets/ifc_models/AC-11-Smiley-West-04-07-2007.ifc"

#my_renderer = JupyterRenderer(size=(700, 700))


settings = ifcopenshell.geom.settings()
# tells ifcopenshell to use pythonocc
settings.set(settings.USE_PYTHON_OPENCASCADE, True)

ifc_file = ifcopenshell.open(ifc_filename)

products = ifc_file.by_type("IfcProduct")  # traverse all IfcProducts

display, start_display, add_menu, add_function_to_menu = init_display()

for product in products:
    if product.Representation is not None:  # some IfcProducts don't have any 3d representation
        pdct_shape = ifcopenshell.geom.create_shape(settings, inst=product)
        r, g, b, alpha = pdct_shape.styles[0]  # the shape color
        #print(r, g, b)
        color = Quantity_Color(abs(r), abs(g), abs(b), Quantity_TOC_RGB)
        display.DisplayShape(pdct_shape.geometry, color=color)
        # below, the pdct_shape.geometry is a TopoDS_Shape, i.e. can be rendered using
        # any renderer (threejs, x3dom, jupyter, qt5 based etc.)
        #my_renderer.DisplayShape(pdct_shape.geometry, shape_color = color, transparency=True, opacity=alpha)

display.FitAll()
start_display()

# my_renderer
