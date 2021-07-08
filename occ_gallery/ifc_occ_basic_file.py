#!/usr/bin/env python
# coding: utf-8

import os

from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer, format_color
from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()

import ifcopenshell
import ifcopenshell.geom


ifc_filename = os.path.join(
    '..', 'assets', 'ifc_models', 'AC-11-Smiley-West-04-07-2007.ifc')
assert os.path.isfile(ifc_filename)

settings = ifcopenshell.geom.settings()
# tells ifcopenshell to use pythonocc
settings.set(settings.USE_PYTHON_OPENCASCADE, True)

ifc_file = ifcopenshell.open(ifc_filename)

products = ifc_file.by_type("IfcProduct")  # traverse all IfcProducts

for product in products:
    if product.Representation is not None:
        # some IfcProducts don't have any 3d representation
        pdct_shape = ifcopenshell.geom.create_shape(settings, inst=product)
        r, g, b, alpha = pdct_shape.styles[0]  # the shape color
        #color = format_color(int(abs(r)*255), int(abs(g)*255), int(abs(b)*255))
        # below, the pdct_shape.geometry is a TopoDS_Shape, i.e. can be rendered using
        # any renderer (threejs, x3dom, jupyter, qt5 based etc.)
        display.DisplayShape(pdct_shape.geometry)

start_display()
