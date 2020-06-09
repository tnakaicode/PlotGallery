import numpy as np
import sys
import os
import time
import math
from PIL import Image

from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge,
                                     BRepBuilderAPI_MakeFace,
                                     BRepBuilderAPI_MakeWire)
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.GeomFill import GeomFill_SimpleBound, GeomFill_ConstrainedFilling
from OCC.Core.GeomAbs import GeomAbs_C2
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepAdaptor import BRepAdaptor_CompCurve, BRepAdaptor_HCompCurve
from OCC.Extend.DataExchange import write_step_file


def boundary_curve_from_2_points(p1, p2):
    # first create an edge
    e0 = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
    w0 = BRepBuilderAPI_MakeWire(e0).Wire()
    # boundary for filling
    adap = BRepAdaptor_CompCurve(w0)
    p0_h = BRepAdaptor_HCompCurve(adap)
    boundary = GeomFill_SimpleBound(p0_h, 1e-6, 1e-6)
    return boundary

if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    """ 
    takes the heightmap from a jpeg file and apply a texture
    this example requires numpy/matplotlib
    """
    print("opening image")
    #heightmap = Image.open('images/mountain_heightmap.jpg')
    heightmap = Image.open('./images/map1.jpg')
    heightmap = Image.open('./images/Shurijo.jpg')
    heightmap.show()
    width = int(heightmap.size[0])
    height = int(heightmap.size[1])
    #width = heightmap.size[0]
    #height = heightmap.size[1]
    # create the gp_Pnt array
    print("parse image and fill in point array")
    for i in range(1, width):
        for j in range(1, height):
            # all 3 RGB values are equal, just take the first one
            # vertex 1
            height_value = heightmap.getpixel((i - 1, j - 1))[0]
            v1 = gp_Pnt(i, j, float(height_value) / 10)
            # vertex 2
            height_value = heightmap.getpixel((i, j - 1))[0]
            v2 = gp_Pnt(i + 1, j, float(height_value) / 10)
            # vertex 3
            height_value = heightmap.getpixel((i, j))[0]
            v3 = gp_Pnt(i + 1, j + 1, float(height_value) / 10)
            # vertex 4
            height_value = heightmap.getpixel((i - 1, j))[0]
            v4 = gp_Pnt(i, j + 1, float(height_value) / 10)
            # boundaries
            b1 = boundary_curve_from_2_points(v1, v2)
            b2 = boundary_curve_from_2_points(v2, v3)
            b3 = boundary_curve_from_2_points(v3, v4)
            b4 = boundary_curve_from_2_points(v4, v1)
            #
            bConstrainedFilling = GeomFill_ConstrainedFilling(8, 2)
            bConstrainedFilling.Init(b1, b2, b3, b4, False)
            srf1 = bConstrainedFilling.Surface()
            # make a face from this srf
            patch = BRepBuilderAPI_MakeFace()
            bounds = True
            toldegen = 1e-6
            patch.Init(srf1, bounds, toldegen)
            patch.Build()
            display.DisplayShape(patch.Face())
            # then create faces

            txt = "\r"
            txt += "{:03d} / {:03d}".format(i, width)
            txt += " - "
            txt += "{:03d} / {:03d}".format(j, height)
            sys.stdout.write(txt)
            sys.stdout.flush()

        #print("%s%%" % int(float(i) / width * 100))
        # display.process_events()
    print()
    display.FitAll()
    # finally display image
    start_display()
