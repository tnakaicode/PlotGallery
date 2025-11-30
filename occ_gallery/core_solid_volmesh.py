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


def run_gmsh_on_step(stepfile, out_msh, mesh_size=None, size=100.0):
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

    # NOTE: avoid automatic fallback geometry construction here — prefer to
    # let the user see the import/meshing error and adjust source geometry.

    print("gmsh: generating 3D mesh (this may take a moment)")
    try:
        gmsh.model.mesh.generate(3)
    except Exception as e:
        print("gmsh: mesh generation failed with exception:", e)
        # Diagnostic: inspect 2D surface meshes for duplicated facets
        try:
            print("gmsh: running surface diagnostics...")
            node_tags_all, node_coords_all, _ = gmsh.model.mesh.getNodes()
            # build node coord map
            node_map = {int(node_tags_all[i]): (node_coords_all[3 * i], node_coords_all[3 * i + 1], node_coords_all[3 * i + 2]) for i in range(len(node_tags_all))}
            for (dim, tag) in ents2:
                print(f"--- Surface dim={dim} tag={tag} diagnostics ---")
                try:
                    types_s, elemTags_s, nodeTags_s = gmsh.model.mesh.getElements(2, tag)
                except Exception as e2:
                    print(f"  could not get elements for surface {tag}:", e2)
                    continue
                tri_count = {}
                # iterate element types on this surface
                for ii, etype in enumerate(types_s):
                    etags = elemTags_s[ii]
                    nodes_flat = nodeTags_s[ii]
                    props = gmsh.model.mesh.getElementProperties(etype)
                    num_nodes = props[3]
                    for j in range(len(etags)):
                        start = j * num_nodes
                        elem_nodes = [int(n) for n in nodes_flat[start:start + num_nodes]]
                        if num_nodes == 3:
                            key = tuple(sorted(elem_nodes))
                            tri_count[key] = tri_count.get(key, 0) + 1
                        else:
                            # for non-triangle (e.g., quads), split into triangles for diagnostics
                            if num_nodes == 4:
                                a, b, c, d = elem_nodes
                                tris = [tuple(sorted((a, b, c))), tuple(sorted((a, c, d)))]
                                for key in tris:
                                    tri_count[key] = tri_count.get(key, 0) + 1
                duplicates = {tri:cnt for tri,cnt in tri_count.items() if cnt > 1}
                if duplicates:
                    print(f"  Found {len(duplicates)} duplicated triangle(s) on surface {tag} - showing up to 10:")
                    for idx, (tri, cnt) in enumerate(duplicates.items()):
                        if idx >= 10:
                            break
                        print(f"    tri nodes={tri} duplicated {cnt} times")
                        for nt in tri:
                            coord = node_map.get(nt)
                            print(f"      node {nt}: {coord}")
                else:
                    print(f"  No duplicated triangles found on surface {tag}")
        except Exception as diag_e:
            print("gmsh: diagnostic step failed:", diag_e)
        # Re-raise original exception to preserve behavior
        raise
    # write using MSH v2 format for better compatibility with mesh readers
    gmsh.write(out_msh, mshVersion=2)
    print(f"gmsh: wrote volume mesh to {out_msh} (MSH v2)")

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
            elems.append([int(n) for n in nodes_flat[start:start + num_nodes_per_elem]])
        elements.append((int(etype), etags, elems))

    gmsh.finalize()
    return coords, elements


if __name__ == "__main__":
    display, start_display, _, _ = init_display()

    # --- User-editable parameters (no CLI allowed) ---
    out_msh = "core_solid_volmesh.msh"  # output mesh filename
    mesh_size = 5.0  # target characteristic length for mesh
    size = 10.0  # shape size parameter
    # -------------------------------------------------

    shape = make_shape_box(length=size)
    display.DisplayShape(shape, transparency=0.5)
    display.FitAll()
    display.View.Dump("core_solid_volmesh_occ.png")

    td = tempfile.mkdtemp(prefix="occ2gmsh_")
    stepfile = os.path.join(td, "shape.step")
    print(f"Writing STEP to {stepfile}")
    write_step(shape, stepfile)

    coords, elements = run_gmsh_on_step(stepfile, out_msh, mesh_size=mesh_size, size=size)

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

    for tri in tris:
        t0, t1, t2 = int(tri[0]), int(tri[1]), int(tri[2])
        p0c = coords[t0]
        p1c = coords[t1]
        p2c = coords[t2]
        p0 = gp_Pnt(p0c[0], p0c[1], p0c[2])
        p1 = gp_Pnt(p1c[0], p1c[1], p1c[2])
        p2 = gp_Pnt(p2c[0], p2c[1], p2c[2])
        f = make_face(make_polygon([p0, p1, p2], True))
        display.DisplayShape(f, transparency=0.5)
    display.DisplayShape(shape, transparency=0.5)

    display.FitAll()
    display.View.Dump("core_solid_volmesh_occ.png")
    start_display()
