#!/usr/bin/env python

##Copyright 2025 Thomas paviot (tpaviot@gmail.com)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

from OCC.Core.gp import gp_Pnt
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.GeomLib import geomlib
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRep import BRep_Tool
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.GeomConvert import GeomConvert_CompCurveToBSplineCurve
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()
# a bspline from three points
points = TColgp_HArray1OfPnt(1, 3)
points.SetValue(1, gp_Pnt(0, 0, 0))
points.SetValue(2, gp_Pnt(1, 1, 0))
points.SetValue(3, gp_Pnt(2, 3, 4))

interpolator = GeomAPI_Interpolate(points, False, 1e-6)
interpolator.Perform()
curve_to_extend = interpolator.Curve()

# Create an edge from the curve for proper extension
edge_to_extend = BRepBuilderAPI_MakeEdge(curve_to_extend).Edge()
# Display the edge
display.DisplayShape(edge_to_extend, color="BLUE")

# Extend the curve to another point
# Calculate a more suitable extension point based on curve tangent
u_max = curve_to_extend.LastParameter()
last_point = curve_to_extend.Value(u_max)

# Get tangent vector at the end of the curve
from OCC.Core.gp import gp_Vec

tangent_vec = gp_Vec()
curve_to_extend.D1(u_max, last_point, tangent_vec)

# Normalize the tangent vector and create a point along the tangent direction
tangent_vec.Normalize()
extension_length = 2.0  # Distance to extend

# Create new point along tangent direction
new_pnt_tangent = gp_Pnt(
    last_point.X() + tangent_vec.X() * extension_length,
    last_point.Y() + tangent_vec.Y() * extension_length,
    last_point.Z() + tangent_vec.Z() * extension_length,
)

# Also keep the original challenging point for comparison
new_pnt_original = gp_Pnt(2.5, 6, -1)

# Display both extension points
display.DisplayShape(new_pnt_tangent, color="RED")
display.DisplayShape(new_pnt_original, color="YELLOW")

# Extend the curve using multiple approaches
CONTINUITY = 1  # degree of continuity 1, 2 or 3
AFTER = True  # insert the new point at the end of the curve

print("=== Trying different curve extension methods ===")

# Method 1: geomlib.ExtendCurveToPoint (static function) - try tangent-based point
try:
    print("Method 1: geomlib.ExtendCurveToPoint with tangent-based point...")
    extended_curve_1 = geomlib.ExtendCurveToPoint(
        curve_to_extend, new_pnt_tangent, CONTINUITY, AFTER
    )

    if extended_curve_1 is not None and not extended_curve_1.IsNull():
        print("✅ SUCCESS: geomlib.ExtendCurveToPoint worked!")
        extended_edge = BRepBuilderAPI_MakeEdge(extended_curve_1).Edge()
        display.DisplayShape(extended_edge, color="GREEN", update=True)

        u_max_ext = extended_curve_1.LastParameter()
        end_point_ext = extended_curve_1.Value(u_max_ext)
        print(
            f"Extended curve end point: ({end_point_ext.X():.2f}, {end_point_ext.Y():.2f}, {end_point_ext.Z():.2f})"
        )
        success = True
    else:
        print("❌ Method 1 returned None/Null")
        success = False

except Exception as e:
    print(f"❌ Method 1 failed: {e}")
    success = False

# Display original curve info for comparison
u_max_orig = curve_to_extend.LastParameter()
end_point_orig = curve_to_extend.Value(u_max_orig)
print(
    f"\nOriginal curve end point: ({end_point_orig.X():.2f}, {end_point_orig.Y():.2f}, {end_point_orig.Z():.2f})"
)
print(
    f"Target tangent-based point: ({new_pnt_tangent.X():.2f}, {new_pnt_tangent.Y():.2f}, {new_pnt_tangent.Z():.2f})"
)
print(
    f"Target challenging point: ({new_pnt_original.X():.2f}, {new_pnt_original.Y():.2f}, {new_pnt_original.Z():.2f})"
)

if not success:
    print(
        "\n⚠️  All extension methods failed - geomlib.ExtendCurveToPoint may have implementation limitations"
    )

display.FitAll()
start_display()
