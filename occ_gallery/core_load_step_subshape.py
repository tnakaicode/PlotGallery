import pathlib
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_DocumentTool
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.TDF import TDF_LabelSequence
from OCC.Core.TDF import TDF_Label
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Shape
from OCC.Extend.DataExchange import read_step_file_with_names_colors
import random

app = XCAFApp_Application.GetApplication()
doc = TDocStd_Document("pythonocc-doc")
app.NewDocument("pythonocc-doc", doc)

reader = STEPCAFControl_Reader()
reader.SetColorMode(True)
reader.SetNameMode(True)
reader.SetLayerMode(True)
stepname = pathlib.Path(r"output.step")

filename = "./assets/models/as1-oc-214.stp"
status = reader.ReadFile(filename)

if status:
    reader.Transfer(doc)
    print("STEP file loaded successfully.")
else:
    print("Failed to load STEP file.")

shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
color_tool = XCAFDoc_DocumentTool.ColorTool(doc.Main())

root_labels = TDF_LabelSequence()
shape_tool.GetFreeShapes(root_labels)
print(root_labels.Length())
if root_labels.Length() > 0:
    root_label = root_labels.Value(1)
    sub_labels = TDF_LabelSequence()
    shape_tool.GetSubShapes(root_label, sub_labels)
    print(sub_labels.Length())
