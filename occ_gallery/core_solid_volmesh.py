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
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRep import BRep_Builder


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
    print("Original shape:", shape)
    # Apply sewing with larger tolerance to unify overlapping edges and faces
    sew = BRepBuilderAPI_Sewing(1e-4)  # increased tolerance
    sew.SetMinTolerance(1e-6)
    sew.SetMaxTolerance(1e-3)
    sew.Add(shape)
    sew.Perform()
    sewed_shape = sew.SewedShape()
    print("Sewed shape:", sewed_shape)

    writer = STEPControl_Writer()
    writer.Transfer(sewed_shape, STEPControl_AsIs)
    status = writer.Write(filename)
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP write failed: status={status}")
    return sewed_shape


def run_gmsh_on_step(stepfile, out_msh, mesh_size=None, occ_shape=None):
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
        print(
            f"gmsh: no 3D entities found, attempting to build volume from {len(surface_tags)} surfaces"
        )
        # create a surface loop and a volume (may fail if orientations are inconsistent)
        sl = gmsh.model.occ.addSurfaceLoop(surface_tags)
        vol = gmsh.model.occ.addVolume([sl])
        print(f"gmsh: created volume {vol} from surface loop {sl}")
        gmsh.model.occ.synchronize()

    # Set mesh tolerance and size parameters
    gmsh.option.setNumber("Geometry.Tolerance", 1e-4)
    gmsh.option.setNumber("Geometry.ToleranceBoolean", 1e-4)
    gmsh.option.setNumber("Mesh.ToleranceInitialDelaunay", 1e-6)
    gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay for 2D
    gmsh.option.setNumber("Mesh.Algorithm3D", 1)  # Delaunay for 3D

    if mesh_size is not None:
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)

    # --- Local refinement around smallest curve (assumed the hole) ---
    try:
        curves = gmsh.model.getEntities(1)
        if len(curves) > 0:
            # pick the curve with smallest bounding-box extent (likely the hole)
            best = None
            best_extent = None
            for dim, tag in curves:
                try:
                    bb = gmsh.model.getBoundingBox(dim, tag)
                except Exception:
                    continue
                extent = max(bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2])
                if best is None or extent < best_extent:
                    best = tag
                    best_extent = extent
            if best is not None:
                hole_curve = best
                print(
                    f"gmsh: selected curve {hole_curve} for local refinement (extent {best_extent})"
                )
                dist_field = gmsh.model.mesh.field.add("Distance")
                gmsh.model.mesh.field.setNumbers(dist_field, "CurvesList", [hole_curve])
                thresh = gmsh.model.mesh.field.add("Threshold")
                gmsh.model.mesh.field.setNumber(thresh, "InField", dist_field)
                # use provided local params if present in globals
                ls_min = globals().get("local_size_min", 0.05)
                ld_min = globals().get("local_dist_min", 0.05)
                ld_max = globals().get("local_dist_max", 1.0)
                gmsh.model.mesh.field.setNumber(thresh, "SizeMin", ls_min)
                gmsh.model.mesh.field.setNumber(
                    thresh, "SizeMax", mesh_size if mesh_size is not None else 0.5
                )
                gmsh.model.mesh.field.setNumber(thresh, "DistMin", ld_min)
                gmsh.model.mesh.field.setNumber(thresh, "DistMax", ld_max)
                gmsh.model.mesh.field.setAsBackgroundMesh(thresh)
    except Exception as ex:
        print("gmsh: local refinement field setup failed:", ex)

    print("gmsh: generating 3D mesh (this may take a moment)")

    # First generate 2D mesh for surface diagnostics
    gmsh.model.mesh.generate(2)

    # Detect duplicate triangles but do NOT remove them (non-destructive).
    # Instead, log duplicates and export the corresponding OCC face(s) for inspection.
    duplicates_found = []
    for dim, tag in ents2:
        elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(dim, tag)
        for i, etype in enumerate(elem_types):
            if len(elem_tags[i]) == 0:
                continue
            # triangle element type is 2 in gmsh
            if etype == 2:
                nodes_flat = list(elem_node_tags[i])
                etags = list(elem_tags[i])
                num_nodes = 3
                tri_to_tag = {}
                for j in range(len(etags)):
                    start = j * num_nodes
                    tri_nodes = tuple(
                        sorted(
                            [
                                int(nodes_flat[start]),
                                int(nodes_flat[start + 1]),
                                int(nodes_flat[start + 2]),
                            ]
                        )
                    )
                    if tri_nodes in tri_to_tag:
                        print(
                            f"gmsh: duplicate triangle {tri_nodes} found on surface {tag}"
                        )
                        duplicates_found.append((tag, tri_nodes))
                    else:
                        tri_to_tag[tri_nodes] = etags[j]

    # If duplicates exist, export a STEP with candidate OCC faces for manual inspection
    if len(duplicates_found) > 0:
        print(
            f"gmsh: {len(duplicates_found)} duplicated triangle(s) detected. Exporting candidate faces."
        )
        # use the first duplicate triangle as representative
        if occ_shape is not None:
            dup_tag, tri = duplicates_found[0]
            # compute centroid of triangle
            n0, n1, n2 = tri
            node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
            coord_map = {}
            for idx, tagid in enumerate(node_tags):
                coord_map[int(tagid)] = (
                    node_coords[3 * idx],
                    node_coords[3 * idx + 1],
                    node_coords[3 * idx + 2],
                )
            p0 = coord_map[n0]
            p1 = coord_map[n1]
            p2 = coord_map[n2]
            centroid = (
                (p0[0] + p1[0] + p2[0]) / 3.0,
                (p0[1] + p1[1] + p2[1]) / 3.0,
                (p0[2] + p1[2] + p2[2]) / 3.0,
            )
            # export OCC faces that contain this centroid in their bounding box
            try:
                from OCC.Core.Bnd import Bnd_Box
                from OCC.Core.BRepBndLib import brepbndlib_Add
                from OCC.Core.TopoDS import topods_Face
                from OCC.Core.TopExp import TopExp_Explorer
                from OCC.Core.TopAbs import TopAbs_FACE
                from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
                from OCC.Core.IFSelect import IFSelect_RetDone

                exp = TopExp_Explorer(occ_shape, TopAbs_FACE)
                faces_to_export = []
                idx = 0
                while exp.More():
                    f = topods_Face(exp.Current())
                    bb = Bnd_Box()
                    brepbndlib_Add(f, bb)
                    xmin, ymin, zmin, xmax, ymax, zmax = bb.Get()
                    x, y, z = centroid
                    if (
                        xmin - 1e-8 <= x <= xmax + 1e-8
                        and ymin - 1e-8 <= y <= ymax + 1e-8
                        and zmin - 1e-8 <= z <= zmax + 1e-8
                    ):
                        faces_to_export.append((idx, f))
                    idx += 1
                    exp.Next()
                if len(faces_to_export) > 0:
                    # build compound of candidate faces and write STEP
                    from OCC.Core.TopoDS import TopoDS_Compound
                    from OCC.Core.BRep import BRep_Builder

                    builder = BRep_Builder()
                    comp = TopoDS_Compound()
                    builder.MakeCompound(comp)
                    for ii, ff in faces_to_export:
                        builder.Add(comp, ff)
                    out_step = os.path.join(
                        os.path.dirname(stepfile),
                        f"gmsh_candidates_surface_{dup_tag}.step",
                    )
                    writer = STEPControl_Writer()
                    writer.Transfer(comp, STEPControl_AsIs)
                    status = writer.Write(out_step)
                    if status == IFSelect_RetDone:
                        print(f"Exported candidate faces to {out_step}")
                    else:
                        print("Failed to write candidate faces STEP")
                else:
                    print(
                        "No OCC faces found whose bbox contains the duplicate triangle centroid"
                    )
            except Exception as ex:
                print("Error during OCC face export:", ex)
        else:
            print("occ_shape not provided; cannot export candidate OCC faces")

    # Now try 3D mesh generation
    try:
        gmsh.model.mesh.generate(3)
        print("gmsh: 3D mesh generation succeeded")
    except Exception as e:
        print(f"gmsh: 3D mesh generation failed: {e}")
        print("gmsh: mesh remains 2D only")
    # write mesh file
    gmsh.write(out_msh)
    print(f"gmsh: wrote mesh to {out_msh}")

    # collect nodes and elements directly from gmsh model for downstream use
    node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
    # build tag->coord mapping
    coords = {}
    for i, tag in enumerate(node_tags):
        x = node_coords[3 * i]
        y = node_coords[3 * i + 1]
        z = node_coords[3 * i + 2]
        coords[int(tag)] = (float(x), float(y), float(z))

    types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements()
    # parse elements into lists per type
    elements = []
    for i, etype in enumerate(types):
        etags = elem_tags[i]
        nodes_flat = elem_node_tags[i]
        # get number of nodes per element for this type
        props = gmsh.model.mesh.getElementProperties(etype)
        # props: (name, dim, order, numNodes, numNodes2)
        num_nodes_per_elem = props[3]
        # split flat nodes list
        elems = []
        for j in range(len(etags)):
            start = j * num_nodes_per_elem
            elems.append(
                [int(n) for n in nodes_flat[start : start + num_nodes_per_elem]]
            )
        elements.append((int(etype), etags, elems))

    gmsh.finalize()
    return coords, elements


if __name__ == "__main__":
    display, start_display, _, _ = init_display()

    # --- User-editable parameters (no CLI allowed) ---
    out_msh = "core_solid_volmesh.msh"  # output mesh filename
    mesh_size = 1.0  # global target characteristic length for mesh (reduced)
    local_size_min = 0.2  # min element size near hole
    local_dist_min = 1.0
    local_dist_max = 1.5
    size = 10.0  # shape size parameter
    # -------------------------------------------------

    shape = make_shape_box(length=size)
    display.DisplayShape(shape, transparency=0.5)
    display.FitAll()
    display.View.Dump("core_solid_volmesh_occ.png")

    td = tempfile.mkdtemp(prefix="occ2gmsh_")
    stepfile = os.path.join(td, "shape.step")
    print(f"Writing STEP to {stepfile}")
    sewed_shape = write_step(shape, stepfile)

    coords, elements = run_gmsh_on_step(
        stepfile, out_msh, mesh_size=mesh_size, occ_shape=sewed_shape
    )

    # Build triangle list for display. `coords` maps node tag -> (x,y,z).
    tris = []
    # Look for tetra elements first to extract boundary triangles
    tets = []
    tri_elems = []
    for etype, etags, elems in elements:
        if len(elems) == 0:
            continue
        # check number of nodes in first element
        nnode = len(elems[0])
        if nnode == 4:
            tets.extend(elems)
        elif nnode == 3:
            tri_elems.extend(elems)

    if len(tets) > 0:
        face_counts = {}
        faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
        for tet in tets:
            tet = [int(x) for x in tet]
            for i, j, k in faces:
                tri = tuple(sorted((tet[i], tet[j], tet[k])))
                face_counts[tri] = face_counts.get(tri, 0) + 1
        bfaces = [tri for tri, count in face_counts.items() if count == 1]
        tris = bfaces
    elif len(tri_elems) > 0:
        tris = [tuple(int(x) for x in tri) for tri in tri_elems]
    else:
        raise RuntimeError("Mesh contained no triangle or tetra elements")

    display.EraseAll()
    # Build and display internal edges from tetra elements so volume mesh is visible
    if len(tets) > 0:
        # collect unique edges
        edge_set = set()
        for tet in tets:
            a, b, c, d = [int(x) for x in tet]
            edges = [(a, b), (a, c), (a, d), (b, c), (b, d), (c, d)]
            for e in edges:
                edge_set.add(tuple(sorted(e)))

        builder = BRep_Builder()
        comp = TopoDS_Compound()
        builder.MakeCompound(comp)
        for e in edge_set:
            n0, n1 = e
            p0c = coords[n0]
            p1c = coords[n1]
            p0 = gp_Pnt(p0c[0], p0c[1], p0c[2])
            p1 = gp_Pnt(p1c[0], p1c[1], p1c[2])
            ed = make_edge(p0, p1)
            builder.Add(comp, ed)
        display.DisplayShape(comp, update=True)

    for tri in tris:
        t0, t1, t2 = int(tri[0]), int(tri[1]), int(tri[2])
        p0c = coords[t0]
        p1c = coords[t1]
        p2c = coords[t2]
        p0 = gp_Pnt(p0c[0], p0c[1], p0c[2])
        p1 = gp_Pnt(p1c[0], p1c[1], p1c[2])
        p2 = gp_Pnt(p2c[0], p2c[1], p2c[2])
        f = make_face(make_polygon([p0, p1, p2], True))
        # display.DisplayShape(f, transparency=0.5)
    # display.DisplayShape(shape, transparency=0.5)

    display.FitAll()
    display.View.Dump("core_solid_volmesh_occ.png")
    start_display()
