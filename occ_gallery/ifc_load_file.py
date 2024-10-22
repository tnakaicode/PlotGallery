# Copyright 2020 Thomas Paviot (tpaviot@gmail.com)
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

import os
import sys

from OCC.Core.gp import gp_Vec
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.Graphic3d import Graphic3d_ClipPlane
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TDF import TDF_Label, TDF_LabelSequence
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from OCC.Display.SimpleGui import init_display

try:
    import ifcopenshell
    import ifcopenshell.geom
except ModuleNotFoundError:
    print("ifcopenshell package not found.")
    sys.exit(0)


def read_step_file_with_names_colors(filename):
    """ Returns list of tuples (topods_shape, label, color)
    Use OCAF.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError("%s not found." % filename)
    # the list:
    output_shapes = {}

    # create an handle to a document
    doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

    # Get root assembly
    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool(doc.Main())
    # layer_tool = XCAFDoc_DocumentTool_LayerTool(doc.Main())
    # mat_tool = XCAFDoc_DocumentTool_MaterialTool(doc.Main())

    step_reader = STEPCAFControl_Reader()
    step_reader.SetColorMode(True)
    step_reader.SetLayerMode(True)
    step_reader.SetNameMode(True)
    step_reader.SetMatMode(True)
    step_reader.SetGDTMode(True)

    status = step_reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        step_reader.Transfer(doc)

    locs = []

    def _get_sub_shapes(lab, loc):
        # global cnt, lvl
        # cnt += 1
        # print("\n[%d] level %d, handling LABEL %s\n" % (cnt, lvl, _get_label_name(lab)))
        # print()
        # print(lab.DumpToString())
        # print()
        # print("Is Assembly    :", shape_tool.IsAssembly(lab))
        # print("Is Free        :", shape_tool.IsFree(lab))
        # print("Is Shape       :", shape_tool.IsShape(lab))
        # print("Is Compound    :", shape_tool.IsCompound(lab))
        # print("Is Component   :", shape_tool.IsComponent(lab))
        # print("Is SimpleShape :", shape_tool.IsSimpleShape(lab))
        # print("Is Reference   :", shape_tool.IsReference(lab))

        # users = TDF_LabelSequence()
        # users_cnt = shape_tool.GetUsers(lab, users)
        # print("Nr Users       :", users_cnt)

        l_subss = TDF_LabelSequence()
        shape_tool.GetSubShapes(lab, l_subss)
        # print("Nb subshapes   :", l_subss.Length())
        l_comps = TDF_LabelSequence()
        shape_tool.GetComponents(lab, l_comps)
        # print("Nb components  :", l_comps.Length())
        # print()
        name = lab.GetLabelName()
        print("Name :", name)

        if shape_tool.IsAssembly(lab):
            l_c = TDF_LabelSequence()
            shape_tool.GetComponents(lab, l_c)
            for i in range(l_c.Length()):
                label = l_c.Value(i + 1)
                if shape_tool.IsReference(label):
                    # print("\n########  reference label :", label)
                    label_reference = TDF_Label()
                    shape_tool.GetReferredShape(label, label_reference)
                    loc = shape_tool.GetLocation(label)
                    # print("    loc          :", loc)
                    # trans = loc.Transformation()
                    # print("    tran form    :", trans.Form())
                    # rot = trans.GetRotation()
                    # print("    rotation     :", rot)
                    # print("    X            :", rot.X())
                    # print("    Y            :", rot.Y())
                    # print("    Z            :", rot.Z())
                    # print("    W            :", rot.W())
                    # tran = trans.TranslationPart()
                    # print("    translation  :", tran)
                    # print("    X            :", tran.X())
                    # print("    Y            :", tran.Y())
                    # print("    Z            :", tran.Z())

                    locs.append(loc)
                    # print(">>>>")
                    # lvl += 1
                    _get_sub_shapes(label_reference, loc)
                    # lvl -= 1
                    # print("<<<<")
                    locs.pop()

        elif shape_tool.IsSimpleShape(lab):
            # print("\n########  simpleshape label :", lab)
            shape = shape_tool.GetShape(lab)
            # print("    all ass locs   :", locs)

            loc = TopLoc_Location()
            for l in locs:
                # print("    take loc       :", l)
                loc = loc.Multiplied(l)

            # trans = loc.Transformation()
            # print("    FINAL loc    :")
            # print("    tran form    :", trans.Form())
            # rot = trans.GetRotation()
            # print("    rotation     :", rot)
            # print("    X            :", rot.X())
            # print("    Y            :", rot.Y())
            # print("    Z            :", rot.Z())
            # print("    W            :", rot.W())
            # tran = trans.TranslationPart()
            # print("    translation  :", tran)
            # print("    X            :", tran.X())
            # print("    Y            :", tran.Y())
            # print("    Z            :", tran.Z())
            c = Quantity_Color(
                0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
            colorSet = False
            if (color_tool.GetInstanceColor(shape, 0, c) or
                    color_tool.GetInstanceColor(shape, 1, c) or
                    color_tool.GetInstanceColor(shape, 2, c)):
                color_tool.SetInstanceColor(shape, 0, c)
                color_tool.SetInstanceColor(shape, 1, c)
                color_tool.SetInstanceColor(shape, 2, c)
                colorSet = True
                n = c.Name(c.Red(), c.Green(), c.Blue())
                print('    instance color Name & RGB: ',
                      c, n, c.Red(), c.Green(), c.Blue())

            if not colorSet:
                if (color_tool.GetColor(lab, 0, c) or
                        color_tool.GetColor(lab, 1, c) or
                        color_tool.GetColor(lab, 2, c)):

                    color_tool.SetInstanceColor(shape, 0, c)
                    color_tool.SetInstanceColor(shape, 1, c)
                    color_tool.SetInstanceColor(shape, 2, c)

                    n = c.Name(c.Red(), c.Green(), c.Blue())
                    print('    shape color Name & RGB: ', c,
                          n, c.Red(), c.Green(), c.Blue())

            shape_disp = BRepBuilderAPI_Transform(
                shape, loc.Transformation()).Shape()
            if not shape_disp in output_shapes:
                output_shapes[shape_disp] = [lab.GetLabelName(), c]
            for i in range(l_subss.Length()):
                lab_subs = l_subss.Value(i + 1)
                # print("\n########  simpleshape subshape label :", lab)
                shape_sub = shape_tool.GetShape(lab_subs)

                c = Quantity_Color(
                    0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
                colorSet = False
                if (color_tool.GetInstanceColor(shape_sub, 0, c) or
                        color_tool.GetInstanceColor(shape_sub, 1, c) or
                        color_tool.GetInstanceColor(shape_sub, 2, c)):
                    color_tool.SetInstanceColor(shape_sub, 0, c)
                    color_tool.SetInstanceColor(shape_sub, 1, c)
                    color_tool.SetInstanceColor(shape_sub, 2, c)
                    colorSet = True
                    n = c.Name(c.Red(), c.Green(), c.Blue())
                    print('    instance color Name & RGB: ',
                          c, n, c.Red(), c.Green(), c.Blue())

                if not colorSet:
                    if (color_tool.GetColor(lab_subs, 0, c) or
                            color_tool.GetColor(lab_subs, 1, c) or
                            color_tool.GetColor(lab_subs, 2, c)):
                        color_tool.SetInstanceColor(shape, 0, c)
                        color_tool.SetInstanceColor(shape, 1, c)
                        color_tool.SetInstanceColor(shape, 2, c)

                        n = c.Name(c.Red(), c.Green(), c.Blue())
                        print('    shape color Name & RGB: ', c,
                              n, c.Red(), c.Green(), c.Blue())
                shape_to_disp = BRepBuilderAPI_Transform(
                    shape_sub, loc.Transformation()).Shape()
                # position the subshape to display
                if not shape_to_disp in output_shapes:
                    output_shapes[shape_to_disp] = [lab_subs.GetLabelName(), c]

    def _get_shapes():
        labels = TDF_LabelSequence()
        shape_tool.GetFreeShapes(labels)
        # global cnt
        # cnt += 1

        print()
        print("Number of shapes at root :", labels.Length())
        print()
        for i in range(labels.Length()):
            root_item = labels.Value(i + 1)
            _get_sub_shapes(root_item, None)
    _get_shapes()
    return output_shapes


display, start_display, add_menu, add_function_to_menu = init_display()

settings = ifcopenshell.geom.settings()
# tells ifcopenshell to use pythonocc
settings.set(settings.USE_PYTHON_OPENCASCADE, True)

# read the ifc file
print("Loading ifc file ...", end="")
ifc_filename = "./assets/ifc_models/A_IFC_model.ifc"
assert os.path.isfile(ifc_filename)
ifc_file = ifcopenshell.open(ifc_filename)
print("done.")

# the clip plane

# clip plane number one, by default xOy
clip_plane_1 = Graphic3d_ClipPlane()

# set hatch on
clip_plane_1.SetCapping(True)
clip_plane_1.SetCappingHatch(True)

# off by default, user will have to enable it
clip_plane_1.SetOn(False)

# set clip plane color
aMat = clip_plane_1.CappingMaterial()
aColor = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)
aMat.SetAmbientColor(aColor)
aMat.SetDiffuseColor(aColor)
clip_plane_1.SetCappingMaterial(aMat)

# and display each subshape
products = ifc_file.by_type("IfcProduct")  # traverse all IfcProducts
nb_of_products = len(products)
for i, product in enumerate(products):
    if product.Representation is not None:  # some IfcProducts don't have any 3d representation
        try:
            print(i)
            pdct_shape = ifcopenshell.geom.create_shape(settings, inst=product)
            r, g, b, a = pdct_shape.styles[0]  # the shape color
            color = Quantity_Color(abs(r), abs(g), abs(b), Quantity_TOC_RGB)
            # speed up rendering, don't update rendering for each shape
            # only update all 50 shapes
            to_update = i % 50 == 0
            new_ais_shp = display.DisplayShape(
                pdct_shape.geometry, color=color, transparency=abs(1 - a), update=to_update)[0]
            new_ais_shp.AddClipPlane(clip_plane_1)
        except RuntimeError:
            print("Failed to process shape geometry")


def animate_translate_clip_plane(event=None):
    clip_plane_1.SetOn(True)
    plane_definition = clip_plane_1.ToPlane()  # it's a gp_Pln
    h = 0.01
    for _ in range(1000):
        plane_definition.Translate(gp_Vec(0., 0., h))
        clip_plane_1.SetEquation(plane_definition)
        display.Context.UpdateCurrentViewer()


if __name__ == '__main__':
    add_menu('IFC clip plane')
    add_function_to_menu('IFC clip plane', animate_translate_clip_plane)
    display.FitAll()
    start_display()
