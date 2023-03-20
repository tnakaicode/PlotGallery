# Copyright 2021 Thomas Paviot (tpaviot@gmail.com)
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

from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.TCollection import TCollection_ExtendedString, TCollection_AsciiString
from OCC.Core.XCAFDoc import (
    XCAFDoc_DocumentTool_ShapeTool,
    XCAFDoc_DocumentTool_LayerTool,
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.Core.TColStd import TColStd_IndexedDataMapOfStringString
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.TDF import TDF_LabelSequence
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepTools import breptools_Clean
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.gp import gp_Pnt

from OCC.Core.RWPly import RWPly_CafWriter
from OCC.Core.RWObj import RWObj_CafReader, RWObj_CafWriter

from OCC.Display.SimpleGui import init_display

# create the shapeto export
shp = BRepPrimAPI_MakeSphere(gp_Pnt(0, 0, 0), 60.0).Shape()

# create a document
doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))
shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
layer_tool = XCAFDoc_DocumentTool_LayerTool(doc.Main())

# mesh shape
# breptools_Clean(shp)

# Triangulate
msh_algo = BRepMesh_IncrementalMesh(shp, True)
msh_algo.Perform()

sub_shape_label = shape_tool.AddShape(shp)
sub_shape_label = shape_tool.AddShape(
    BRepPrimAPI_MakeSphere(gp_Pnt(0, 0, 100), 60.0).Shape())
print(sub_shape_label, shape_tool)

# metadata
a_file_info = TColStd_IndexedDataMapOfStringString()
a_file_info.Add(
    TCollection_AsciiString("Authors"), TCollection_AsciiString("pythonocc")
)

rwobj_writer = RWObj_CafWriter(TCollection_AsciiString("sphere.obj"))
pr = Message_ProgressRange()
print(rwobj_writer.GetRefCount())
rwobj_writer.Perform(doc, a_file_info, pr)

# create an handle to a document
doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

# Get root assembly
shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
l_layers = XCAFDoc_DocumentTool_LayerTool(doc.Main())

rwobj_reader = RWObj_CafReader()
rwobj_reader.SetDocument(doc)
rwobj_reader.Perform(TCollection_AsciiString("sphere.obj"), pr)
print(rwobj_reader)

labels = TDF_LabelSequence()
shape_tool.GetFreeShapes(labels)
_shapes = []
for i in range(labels.Length()):
    label = labels.Value(i + 1)
    a_shape = shape_tool.GetShape(label)
    m = l_layers.GetLayers(a_shape)
    _shapes.append(a_shape)

#
# Display
#
display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(_shapes, update=True)
start_display()
