#!/usr/bin/env python
"""Create 3D offset curves and build a surface through the section wires.

This script tries to use BRepOffsetAPI_ThruSections to create a face/shell
through multiple section wires built from offset curves. If the BRep
classes are not available in the installed pythonOCC, the script will still
build and display the base and offset curves and print an explanatory message.

The approach:
 - create a base 3D spline curve from points
 - create two offsets of that curve using different distances
 - make edges and wires from the curves
 - feed the wires to BRepOffsetAPI_ThruSections and build the resulting shape

"""
from __future__ import print_function

import numpy as np
import math
from OCC.Core.gp import gp_Pnt, gp_Dir
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_HArray1OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline, GeomAPI_Interpolate
from OCC.Core.Geom import Geom_OffsetCurve
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
)
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRep import BRep_Builder

from OCC.Display.SimpleGui import init_display


def make_base_spline():
    pnts = TColgp_Array1OfPnt(1, 5)
    pnts.SetValue(1, gp_Pnt(-4, 0, 0.1))
    pnts.SetValue(2, gp_Pnt(-7, 2, 0.2))
    pnts.SetValue(3, gp_Pnt(-6, 3, -0.1))
    pnts.SetValue(4, gp_Pnt(-4, 3, 0.3))
    pnts.SetValue(5, gp_Pnt(-3, 5, 0.1))

    pnts_h = TColgp_HArray1OfPnt(1, 5)
    for i in range(pnts.Lower(), pnts.Upper() + 1):
        pnts_h.SetValue(i, pnts.Value(i))

    spline_1 = GeomAPI_PointsToBSpline(pnts).Curve()
    spline_2_api = GeomAPI_Interpolate(pnts_h, True, 0.1e-3)
    spline_2_api.Perform()
    spline_2 = spline_2_api.Curve()
    return spline_1, spline_2


def try_build_thru_sections(wires):
    """Try to build a shell/face through wires using BRepOffsetAPI_ThruSections.
    Returns the resulting TopoDS_Shape or None if the API is not available.
    """

    # wires is a list of TopoDS_Wire objects; construct ThruSections
    builder = BRepOffsetAPI_ThruSections(True, False, 1.0e-6)
    for w in wires:
        builder.AddWire(w)
    builder.CheckCompatibility(False)
    builder.Build()
    shape = builder.Shape()
    return shape


def curve_to_wire(curve):
    """Convert a Geom_Curve to a TopoDS_Wire by making an edge and a wire.
    Returns the wire or None on failure.
    """
    edge = BRepBuilderAPI_MakeEdge(curve).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return wire


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    spline_1, spline_2 = make_base_spline()

    # create a few offsets at different distances and tilt their offset directions
    # so that the resulting wires are not coplanar and a 3D shape can be built
    offsets = [-0.5, 0.5, 1.0]
    # tilt angles in degrees for each offset (rotate around Y axis)
    angles_deg = [25, 0, 25]
    curves = []
    for d, ang in zip(offsets, angles_deg):
        if d == 0.0:
            # keep the base curve as the first section
            curves.append(spline_1)
        else:
            rad = math.radians(ang)
            # create a direction tilted from Z by angle 'ang' around Y axis
            dir_vec = gp_Dir(math.sin(rad), 0.5, math.cos(rad))
            off = Geom_OffsetCurve(spline_1, d, dir_vec)
            curves.append(off)

    # display base curves (and sample points)
    for c in curves:
        display.DisplayShape(c)

    # try to convert each curve to wire and build thru-sections
    wires = []
    for c in curves:
        w = curve_to_wire(c)
        if w is not None:
            wires.append(w)

    shape = try_build_thru_sections(wires)
    display.DisplayShape(shape, transparency=0.8)
    print("ThruSections built and displayed.")

    # always display original curve points for reference
    # sample and display a few points on the base spline
    for u in np.linspace(spline_1.FirstParameter(), spline_1.LastParameter(), 11):
        p = gp_Pnt()
        spline_1.D0(u, p)
        display.DisplayShape(p)

    display.FitAll()
    start_display()
