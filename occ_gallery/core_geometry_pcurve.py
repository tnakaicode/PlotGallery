import sys
from typing import Any, NewType

from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepBuilderAPI import (BRepBuilderAPI_NurbsConvert,
                                     BRepBuilderAPI_MakeEdge,
                                     BRepBuilderAPI_MakeFace,
                                     BRepBuilderAPI_MakeWire)
from OCC.Core.BRepTools import breptools
from OCC.Core.GeomConvert import GeomConvert_CompCurveToBSplineCurve, geomconvert_CurveToBSplineCurve, geomconvert
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopoDS import TopoDS_Wire, topods, TopoDS_Face
from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer

NURBSObject = NewType('NURBSObject', Any)


def _bspline_curve_from_wire(wire=NURBSObject):
    if not isinstance(wire, TopoDS_Wire):
        raise TypeError("wire must be a TopoDS_Wire")

    composite_curve_builder = GeomConvert_CompCurveToBSplineCurve()
    edge_explorer = WireExplorer(wire)
    edges = list(edge_explorer.ordered_edges())
    for edge in edges:
        if BRep_Tool.Degenerated(edge):
            continue

        # convert to Nurbs edge
        nurbs_converter = BRepBuilderAPI_NurbsConvert(edge)
        nurbs_converter.Perform(edge)
        nurbs_edge = topods.Edge(nurbs_converter.Shape())
        nurbs_curve = BRep_Tool.Curve(nurbs_edge)[0]
        bspline_curve = geomconvert.CurveToBSplineCurve(nurbs_curve)
        tolerance = 1e-4
        composite_curve_builder.Add(bspline_curve, tolerance)

    comp_curve = composite_curve_builder.BSplineCurve()
    return comp_curve


def _bspline_surface_from_face(face=NURBSObject):
    if not isinstance(face, TopoDS_Face):
        raise TypeError("face must be a TopoDS_Face")

    nurbs_face = topods.Face(BRepBuilderAPI_NurbsConvert(face).Shape())
    surface = BRep_Tool.Surface(nurbs_face)
    return geomconvert.SurfaceToBSplineSurface(surface)


def _new_wire_by_combining_edges(wire=NURBSObject):
    wire = topods.Wire(wire)
    composite_curve = _bspline_curve_from_wire(wire)
    composite_edge = BRepBuilderAPI_MakeEdge(composite_curve).Edge()
    wire_builder = BRepBuilderAPI_MakeWire()
    wire_builder.Add(composite_edge)
    modified_wire = wire_builder.Wire()
    return modified_wire


if __name__ == '__main__':
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile("../assets/models/as1-oc-214.stp")

    if status != IFSelect_RetDone:
        raise ValueError('Error parsing STEP file')

    failsonly = False
    step_reader.PrintCheckLoad(failsonly, IFSelect_ItemsByEntity)
    step_reader.PrintCheckTransfer(failsonly, IFSelect_ItemsByEntity)
    step_reader.TransferRoot()
    shape = step_reader.Shape()
    topo_explorer = TopologyExplorer(shape)
    shape_faces = list(topo_explorer.faces())

    for i, face in enumerate(shape_faces):
        # Only compute Face 22 for illustration purposes
        if i != 22:
            continue

        surface_spline = _bspline_surface_from_face(face)
        face_explorer = TopologyExplorer(face)
        wires = list(face_explorer.wires())
        newwire = None
        for wire in wires:
            if wire == breptools.OuterWire(face):
                newwire = _new_wire_by_combining_edges(wire)
                break

        if newwire is None:
            break  # nothing to do

        # Make new face with new wire
        face_maker = BRepBuilderAPI_MakeFace(surface_spline, newwire)
        newface = face_maker.Face()

        # Now we get the PCurve of this wire
        newface_explorer = TopologyExplorer(newface)
        newface_wires = list(newface_explorer.wires())
        assert len(newface_wires) == 1

        newface_wire_explorer = WireExplorer(newface_wires[0])
        newface_edges = list(newface_wire_explorer.ordered_edges())
        assert len(newface_edges) == 1

        pcurve_object = BRep_Tool().CurveOnSurface(newface_edges[0], newface)
        # ^^^ This object is just a trivial (0.0, 0.0). It does not return pcurve
