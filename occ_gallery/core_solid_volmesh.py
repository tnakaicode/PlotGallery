"""
Create a Solid with pythonocc, export to STEP, and run gmsh to produce a 3D (tetrahedral) mesh.

Usage:
    python core_solid_to_gmsh.py --shape box --out out.msh

Requirements:
 - pythonocc (OCC)
 - gmsh Python module (optional, script will print instructions if not installed)
 - meshio (optional, for reading/writing mesh formats)

Behavior:
 - Builds a simple box or torus/cylinder as a TopoDS_Shape
 - Writes a temporary STEP file using STEPControl_Writer
 - If gmsh is available: `gmsh.merge(stepfile)` then `gmsh.model.mesh.generate(3)`
 - Writes the resulting volume mesh to `--out` (default `solid_vol.msh`)

"""

import numpy as np
import os
import tempfile
import sys
import meshio

from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeSphere,
)
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone
from OCCUtils.Construct import make_face, make_polygon, make_edge, make_wire
from OCC.Core.gp import (
    gp_Pnt,
    gp_Ax3,
    gp_Dir,
    gp_Ax1,
    gp_Trsf,
    gp_Circ,
    gp_Ax2,
    gp_Elips,
)
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing


def wire_moved(wire, x=0, y=0, z=0, deg=0):
    axis = gp_Ax3(gp_Pnt(x, y, z), gp_Dir(0, 1, 0), gp_Dir(1, 0, 0))
    axis.Rotate(gp_Ax1(axis.Location(), axis.Direction()), np.deg2rad(deg))
    trsf = gp_Trsf()
    trsf.SetTransformation(axis, gp_Ax3())
    return wire.Located(TopLoc_Location(trsf))


def make_shape_box(length=100.0):
    pts1 = [
        gp_Pnt(-2.5, -1.5, 0),
        gp_Pnt(2.5, -1.5, 0),
        gp_Pnt(2.5, 1.5, 0),
        gp_Pnt(-2.5, 1.5, 0),
    ]
    wire_rec1 = make_polygon(pts1, True)

    pts2 = [
        gp_Pnt(-2.5, -1.5, 0),
        gp_Pnt(3.5, -1.5, 0),
        gp_Pnt(3.5, 1.5, 0),
        gp_Pnt(-2.5, 1.5, 0),
    ]
    wire_rec2 = make_polygon(pts2, True)

    edge_cir1 = make_edge(gp_Circ(gp_Ax2(gp_Pnt(), gp_Dir(0, 0, 1)), 0.3))
    wire_cir1 = make_wire(edge_cir1)

    edge_cir2 = make_edge(gp_Elips(gp_Ax2(gp_Pnt(), gp_Dir(0, 0, 1)), 0.2, 0.15))
    wire_cir2 = make_wire(edge_cir2)

    thru_section1 = BRepOffsetAPI_ThruSections(True, True)  # solid=True, ruled=True
    thru_section1.AddWire(wire_moved(wire_rec1, 0, 0, 0, 0))
    thru_section1.AddWire(wire_moved(wire_rec2, 0, length, 0, 10))
    solid_shape1 = thru_section1.Shape()

    thru_section2 = BRepOffsetAPI_ThruSections(True, True)  # solid=True, ruled=True
    thru_section2.AddWire(wire_moved(wire_cir1, 0.0, 0, 0, 0))
    thru_section2.AddWire(wire_moved(wire_cir1, 0.5, length, 0, 0))
    solid_shape2 = thru_section2.Shape()

    thru_section3 = BRepOffsetAPI_ThruSections(True, True)  # solid=True, ruled=True
    thru_section3.AddWire(wire_moved(wire_cir1, +1.0, 1, 0, 0))
    thru_section3.AddWire(wire_moved(wire_cir2, +1.0, length - 1, 0, 0))
    solid_shape3 = thru_section3.Shape()

    fuse_op = BRepAlgoAPI_Fuse(solid_shape2, solid_shape3)
    fuse_op.Build()
    fused_shape = fuse_op.Shape()

    cut_op = BRepAlgoAPI_Cut(solid_shape1, solid_shape2)
    cut_op.Build()
    solid_shape = cut_op.Shape()
    return solid_shape


def write_step(shape, filename):
    print(shape)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    status = writer.Write(filename)
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP write failed: status={status}")


def run_gmsh_on_step(stepfile, out_msh, mesh_size=None):
    import gmsh

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    print(f"gmsh: merging STEP file {stepfile}")
    gmsh.merge(stepfile)
    gmsh.model.occ.synchronize()

    # Report entities found in the merged model for diagnostics
    ents3 = gmsh.model.getEntities(3)
    ents2 = gmsh.model.getEntities(2)
    print("gmsh: entities dim=3:", ents3)
    print("gmsh: entities dim=2:", ents2)

    # If no 3D entities (volumes) were imported, try to construct a volume
    # from the imported surface entities by creating a surface loop and volume.
    if len(ents3) == 0 and len(ents2) > 0:
        # collect surface tags
        surface_tags = [tag for (dim, tag) in ents2]
        print(f"gmsh: no 3D entities found, attempting to build volume from {len(surface_tags)} surfaces")
        # create a surface loop and a volume (may fail if orientations are inconsistent)
        sl = gmsh.model.occ.addSurfaceLoop(surface_tags)
        vol = gmsh.model.occ.addVolume([sl])
        print(f"gmsh: created volume {vol} from surface loop {sl}")
        gmsh.model.occ.synchronize()

    if mesh_size is not None:
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)

    print("gmsh: generating 3D mesh (this may take a moment)")
    gmsh.model.mesh.generate(3)
    gmsh.write(out_msh)
    print(f"gmsh: wrote volume mesh to {out_msh}")
    gmsh.finalize()


if __name__ == "__main__":
    display, start_display, _, _ = init_display()

    # --- User-editable parameters (no CLI allowed) ---
    out_msh = "core_solid_volmesh.msh"  # output mesh filename
    mesh_size = 5.0  # target characteristic length for mesh
    size = 10.0  # shape size parameter
    # -------------------------------------------------

    shape = make_shape_box(length=size)

    td = tempfile.mkdtemp(prefix="occ2gmsh_")
    stepfile = os.path.join(td, "shape.step")
    print(f"Writing STEP to {stepfile}")
    write_step(shape, stepfile)

    run_gmsh_on_step(stepfile, out_msh, mesh_size=mesh_size)

    # --- read generated mesh and display boundary with pythonOCC ---

    print("Reading generated mesh for display:", out_msh)
    mesh = meshio.read(out_msh)
    pts = mesh.points

    # If gmsh produced a volume mesh, extract boundary triangles from tets.
    # Otherwise, if gmsh produced only a surface mesh, use the triangle cells directly.
    tris = []
    if "tetra" in mesh.cells_dict:
        tets = mesh.cells_dict["tetra"]

        face_counts = {}
        faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
        for tet in tets:
            tet = [int(x) for x in tet]
            for i, j, k in faces:
                tri = tuple(sorted((tet[i], tet[j], tet[k])))
                face_counts[tri] = face_counts.get(tri, 0) + 1
        bfaces = [tri for tri, count in face_counts.items() if count == 1]
        tris = bfaces
    elif "triangle" in mesh.cells_dict:
        tris = [tuple(int(x) for x in tri) for tri in mesh.cells_dict["triangle"]]
    else:
        raise RuntimeError("Mesh contains neither 'tetra' nor 'triangle' cells")

    for tri in tris:
        i0, i1, i2 = int(tri[0]), int(tri[1]), int(tri[2])
        p0 = gp_Pnt(float(pts[i0, 0]), float(pts[i0, 1]), float(pts[i0, 2]))
        p1 = gp_Pnt(float(pts[i1, 0]), float(pts[i1, 1]), float(pts[i1, 2]))
        p2 = gp_Pnt(float(pts[i2, 0]), float(pts[i2, 1]), float(pts[i2, 2]))
        f = make_face(make_polygon([p0, p1, p2], True))
        display.DisplayShape(f, transparency=0.5)
    display.DisplayShape(shape, transparency=0.5)

    display.FitAll()
    start_display()
