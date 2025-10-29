#!/usr/bin/env python

from __future__ import print_function

import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_HArray1OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline, GeomAPI_Interpolate
from OCC.Core.Geom import Geom_OffsetCurve

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


def curves3d_from_offset(event=None):
    """Create two 3D base curves from points and build offset curves using a fixed direction.
    This mirrors the 2D example but uses Geom_OffsetCurve with a gp_Dir (Z axis).
    """
    # create 3D points (lying in the Z=0 plane to be comparable with 2D example)
    pnts = TColgp_Array1OfPnt(1, 5)
    pnts.SetValue(1, gp_Pnt(-4, 0, 0))
    pnts.SetValue(2, gp_Pnt(-7, 2, 0.1))
    pnts.SetValue(3, gp_Pnt(-6, 3, 0.2))
    pnts.SetValue(4, gp_Pnt(-4, 3, -0.1))
    pnts.SetValue(5, gp_Pnt(-3, 5, 0))

    pnts_h = TColgp_HArray1OfPnt(1, 5)
    for i in range(pnts.Lower(), pnts.Upper() + 1):
        pnts_h.SetValue(i, pnts.Value(i))

    # two ways to build curves: approximate BSpline and interpolate
    spline_1 = GeomAPI_PointsToBSpline(pnts).Curve()
    spline_2_api = GeomAPI_Interpolate(pnts_h, True, 0.1e-3)
    spline_2_api.Perform()
    spline_2 = spline_2_api.Curve()
    print(
        "spline_2 continuity:",
        spline_2.Continuity(),
        "end point:",
        spline_2.EndPoint(),
    )

    # offset direction: use +Z direction so offset is perpendicular to XY plane
    direction = gp_Dir(0, 0.1, 1)

    dist = 1.0
    offset_curve1 = Geom_OffsetCurve(spline_1, dist, direction)
    print(
        "offset_curve1 IsCN(2):",
        offset_curve1.IsCN(2),
        "Continuity:",
        offset_curve1.Continuity(),
    )

    dist2 = 0.1
    offset_curve2 = Geom_OffsetCurve(spline_2, dist2, direction)
    print(
        "offset_curve2 IsCN(2):",
        offset_curve2.IsCN(2),
        "Continuity:",
        offset_curve2.Continuity(),
    )

    # display tangent/normal-ish vectors along the base curve
    for u in np.linspace(spline_1.FirstParameter(), spline_1.LastParameter(), 11):
        p, v1, v2 = gp_Pnt(), gp_Vec(), gp_Vec()
        spline_1.D2(u, p, v1, v2)
        # use second derivative as a direction hint (normalized)
        v2.Normalize()
        display.DisplayVector(v2, p)

    # sample offset curve 2 and display sample points
    for u in np.linspace(
        offset_curve2.FirstParameter(), offset_curve2.LastParameter(), 11
    ):
        p, v1, v2 = gp_Pnt(), gp_Vec(), gp_Vec()
        offset_curve2.D2(u, p, v1, v2)
        display.DisplayShape(p)

    display.DisplayShape(spline_1)
    display.DisplayShape(spline_2)
    for i in range(pnts.Lower(), pnts.Upper() + 1):
        display.DisplayShape(pnts.Value(i))
    display.DisplayShape(offset_curve1, color="YELLOW")
    display.DisplayShape(offset_curve2, color="BLUE1", update=True)


if __name__ == "__main__":
    curves3d_from_offset()
    start_display()
