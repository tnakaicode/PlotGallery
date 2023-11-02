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
from OCC.Core.BRepGProp import brepgprop_LinearProperties, brepgprop_SurfaceProperties


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
    brepgprop_LinearProperties(shape, Properties, True)

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
    brepgprop_SurfaceProperties(shape, Properties, True)

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


if __name__ == "__main__":
    from OCC.Display.SimpleGui import init_display
    from OCC.Extend.DataExchange import read_step_file
    display, start_display, add_menu, add_function_to_menu = init_display()

    shp = read_step_file("./assets/models/array3_2mm3_area_edge.step")
    print(occ_core_edge_length_skipshared(shp))
    print(occ_core_surface_area_skipshared(shp))
    display.DisplayShape(shp)
    display.FitAll()
    start_display()
