# -*- coding:utf-8 -*-

# Copyright 2013-2014 Guillaume Florent (florentsailing@gmail.com)
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

# https://github.com/tpaviot/pythonocc-core/issues/1268

from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop
from OCC.Display.SimpleGui import init_display
from OCC.Extend.DataExchange import read_step_file
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax3, gp_Ax2
from OCC.Core.TopoDS import TopoDS_Shell, TopoDS_Compound
from OCC.Core.BOPAlgo import BOPAlgo_Builder
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.LocOpe import LocOpe_FindEdges, LocOpe_FindEdgesInFace
from OCCUtils.Construct import make_box


def occ_core_edge_length_skipshared(shape):  # , Properties) -> float:
    """Calculates the edge length of input shape

    Parameters
    ----------
    shape : TopoDS_Shape / TopoDS_Solid

    Returns
    -------
    Length : scalar
        Calculated edge length
    """
    Properties = GProp_GProps()
    brepgprop.LinearProperties(shape, Properties, True)

    Length_skipshared = Properties.Mass()

    return Length_skipshared


def occ_core_surface_area_skipshared(shape):  # , Properties) -> float:
    """Calculates the surface area of input shape
    ! ! ! SkipShared = False: Calculates also the overlapping surfaces

    Parameters
    ----------
    shape : TopoDS_Shape / TopoDS_Solid

    Returns
    -------
    Area : scalar
        Calculated surface area
    """
    Properties = GProp_GProps()
    brepgprop.SurfaceProperties(shape, Properties, True)

    Area_skipshared = Properties.Mass()

    return Area_skipshared


def _Tcol_dim_1(li, _type):
    """
    Function factory for 1-dimensional TCol* types
    """
    pts = _type(0, len(li) - 1)
    for n, i in enumerate(li):
        pts.SetValue(n, i)
    return pts


def property_of_box(box=make_box(1, 1, 1)):
    skip_shared = True
    use_triangle = False
    only_closed = True

    print(box)
    print("Skip Shared: ", skip_shared)

    boxs_prop_line = GProp_GProps()
    brepgprop.LinearProperties(box,
                               boxs_prop_line,
                               skip_shared, use_triangle)
    print("Mass of Lines", boxs_prop_line.Mass())

    boxs_prop_surf = GProp_GProps()
    brepgprop.SurfaceProperties(box,
                                boxs_prop_surf,
                                skip_shared, use_triangle)
    print("Mass of Surfaces", boxs_prop_surf.Mass())

    boxs_prop_volm = GProp_GProps()
    brepgprop.VolumeProperties(box,
                               boxs_prop_volm,
                               only_closed, skip_shared, use_triangle)
    print("Mass of Volume", boxs_prop_volm.Mass())


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    shp = read_step_file("./assets/models/array3_2mm3_area_edge.step")
    print(occ_core_edge_length_skipshared(shp))
    print(occ_core_surface_area_skipshared(shp))
    # display.DisplayShape(shp)

    box1 = make_box(gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 1))
    box2 = make_box(gp_Pnt(0, 0, 0), gp_Pnt(-1, -1, -1))
    box3 = make_box(gp_Pnt(1, 0, 0), gp_Pnt(2, 1, 1))
    box4 = make_box(gp_Pnt(0, 0, 0), gp_Pnt(1, -1, -1))
    box5 = make_box(gp_Pnt(0.5, 0, 0), gp_Pnt(1.5, -1, -1))

    boxs = [box1, box3]

    # Make Compound by few boxs
    boxs_comp = TopoDS_Compound()
    bild = BRep_Builder()
    bild.MakeCompound(boxs_comp)
    for shp in boxs:
        bild.Add(boxs_comp, shp)
    property_of_box(boxs_comp)  # Line: NG, Surface: NG

    # Make Shell by only two faces that are sewed
    sew = BRepBuilderAPI_Sewing()
    for shp in boxs:
        sew.Add(shp)
    sew.Perform()
    boxs_sewed = sew.SewedShape()
    property_of_box(boxs_sewed)  # Line: NG, Surface: NG

    # Make Shape by only two faces that are fused
    fuse = BOPAlgo_Builder()
    for shp in boxs:
        fuse.AddArgument(shp)
    fuse.Perform()
    boxs_fuse = fuse.Shape()
    property_of_box(boxs_fuse)  # Line: OK, Surface: OK, Volume: OK

    # <class 'TopoDS_Compound'>
    # Skip Shared:  True
    # Mass of Lines 24.0
    # Mass of Surfaces 12.0
    # Mass of Volume 1.9999999999999991
    #
    # <class 'TopoDS_Compound'>
    # Skip Shared:  True
    # Mass of Lines 24.0
    # Mass of Surfaces 12.0
    # Mass of Volume 1.9999999999999991
    #
    # <class 'TopoDS_Compound'>
    # Skip Shared:  True
    # Mass of Lines 20.0
    # Mass of Surfaces 10.0
    # Mass of Volume 1.9999999999999993

    # Find Edge that the two boxes share
    find_edge = LocOpe_FindEdges(boxs[0], boxs[1])
    find_edge.InitIterator()
    while find_edge.More():
        display.DisplayShape(find_edge.EdgeTo(), color="BLUE1")
        display.DisplayShape(find_edge.EdgeFrom(), color="RED")
        find_edge.Next()

    def display_box(box=make_box(1, 1, 1), name="box"):
        display.DisplayShape(box, transparency=0.9)
        prop = GProp_GProps()
        brepgprop.SurfaceProperties(box, prop, True, False)
        pnt = prop.CentreOfMass()
        display.DisplayMessage(pnt, name)

    display_box(box=box1, name="box1")
    display_box(box=box2, name="box2")
    display_box(box=box3, name="box3")
    display_box(box=box4, name="box4")
    display_box(box=box5, name="box5")
    display.FitAll()
    start_display()
