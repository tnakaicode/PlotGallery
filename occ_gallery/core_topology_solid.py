# Copyright 2009-2016 Thomas Paviot (tpaviot@gmail.com)
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
import sys
import time

from OCC.Core.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse,
    BRepAlgoAPI_Common,
    BRepAlgoAPI_Section,
    BRepAlgoAPI_Cut,
)
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeWedge,
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeTorus,
)
from OCC.Display.SimpleGui import init_display
from OCC.Extend.DataExchange import write_step_file
from OCC.Core.gp import gp_Vec, gp_Ax2, gp_Pnt, gp_Dir, gp_Pln, gp_Trsf


def translate_topods_from_vector(brep_or_iterable, vec, copy=False):
    """
    translate a brep over a vector
    @param brep:    the Topo_DS to translate
    @param vec:     the vector defining the translation
    @param copy:    copies to brep if True
    """
    trns = gp_Trsf()
    trns.SetTranslation(vec)
    brep_trns = BRepBuilderAPI_Transform(brep_or_iterable, trns, copy)
    brep_trns.Build()
    return brep_trns.Shape()


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    box1 = BRepPrimAPI_MakeBox(2, 1, 1).Shape()
    box2 = BRepPrimAPI_MakeBox(2, 1, 1).Shape()
    box3 = BRepPrimAPI_MakeBox(1, 1, 1).Shape()
    box1 = translate_topods_from_vector(box1, gp_Vec(0.5, 0.5, 0))
    box3 = translate_topods_from_vector(box3, gp_Vec(-0.5, -2.0, 0.5))
    fuse_box = BRepAlgoAPI_Fuse(box1, box2).Shape()
    fuse_box = BRepAlgoAPI_Fuse(fuse_box, box3).Shape()

    Sphere = BRepPrimAPI_MakeSphere(gp_Pnt(1.5, 0.8, 1.0), 0.5).Shape()
    Cut = BRepAlgoAPI_Cut(fuse_box, Sphere).Shape()

    display.DisplayShape(Cut)
    print(Cut)
    write_step_file(Cut, "./core_topology_solid.stp")
    display.FitAll()
    start_display()
