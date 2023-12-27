# Copyright 2020 Thomas Paviot (tpaviot@gmail.com)
# and Andreas Plesch (gh id @andreasplesch)
##
# This file is part of pythonOCC.
##
# pythonOCC is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# pythonOCC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface

from OCC.Extend.DataExchange import read_step_file
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.GeomAbs import GeomAbs_BSplineSurface


display, start_display, add_menu, add_function_to_menu = init_display()

from OCC.Core.BRepTools import breptools
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.BRep import BRep_Builder
base_shape = TopoDS_Shape()
builder = BRep_Builder()
breptools.Read(base_shape, "../assets/models/cylinder_head.brep", builder)
base_shape = read_step_file("../assets/models/as1-oc-214.stp")
print(base_shape)
# display.DisplayShape(base_shape)

# conversion to a nurbs representation
nurbs_converter = BRepBuilderAPI_NurbsConvert(base_shape, True)
#nurbs_converter.Perform()
converted_shape = nurbs_converter.Shape()

# now, all edges should be BSpline curves and surfaces BSpline surfaces

# https://castle-engine.io/x3d_implementation_nurbs.php#section_homogeneous_coordinates
expl = TopologyExplorer(converted_shape)

# loop over faces
fc_idx = 1

for face in expl.faces():
    print("=== Face %i ===" % fc_idx)
    surf = BRepAdaptor_Surface(face, True)
    surf_type = surf.GetType()
    # check each of the is a BSpline surface
    # it should be, since we used the nurbs converter before
    if not surf_type == GeomAbs_BSplineSurface:
        raise AssertionError(
            "the face was not converted to a GeomAbs_BSplineSurface")
    # get the nurbs
    bsrf = surf.BSpline()
    print("UDegree:", bsrf.UDegree())
    print("VDegree:", bsrf.VDegree())
    # uknots array
    uknots = bsrf.UKnots()
    print("Uknots:", end="")
    for i in range(bsrf.NbUKnots()):
        print(uknots.Value(i + 1), end=" ")
    # vknots array
    vknots = bsrf.VKnots()
    print("\nVknots:", end="")
    for i in range(bsrf.NbVKnots()):
        print(vknots.Value(i + 1), end=" ")
    print("\n")
    # weights, a 2d array
    weights = bsrf.Weights()
    # weights can be None
    if weights is not None:
        print("Weights:", end="")
        for i in range(bsrf.NbUKnots()):
            for j in range(bsrf.NbVKnots()):
                print(weights.Value(i + 1, j + 1), end=" ")
    # control points (aka poles), as a 2d array
    poles = bsrf.Poles()
    # weights can be None
    if poles is not None:
        print("Poles (control points):", end="")
        for i in range(bsrf.NbUPoles()):
            for j in range(bsrf.NbVPoles()):
                p = poles.Value(i + 1, j + 1)
                print(p.X(), p.Y(), p.Z(), end=" ")
                # display.DisplayShape(p)
    print()
    fc_idx += 1

display.DisplayShape(base_shape, transparency=0.9)
display.DisplayShape(converted_shape, transparency=0.9)
display.FitAll()
start_display()
