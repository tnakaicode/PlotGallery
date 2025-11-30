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

# Unit scaling: currently set to meters (no scale). If you later edit
# coordinates that are in mm, change this to 1e-3 to convert mm->m.
UNIT_SCALE = 1.0

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
    thru_section2.AddWire(wire_moved(wire_cir2, 0.5, length, 0, 0))
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


def run_gmsh_on_step(
    stepfile, out_msh, mesh_size=None, occ_shape=None, surface_only=False
):
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
    curves = gmsh.model.getEntities(1)
    if len(curves) > 0:
        # pick the curve with smallest bounding-box extent (likely the hole)
        best = None
        best_extent = None
        for dim, tag in curves:
            bb = gmsh.model.getBoundingBox(dim, tag)
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

    # First generate 2D mesh for surface diagnostics
    print("gmsh: generating 2D surface mesh (for diagnostics)")
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
            from OCC.Core.Bnd import Bnd_Box
            from OCC.Core.BRepBndLib import brepbndlib_Add
            from OCC.Core.TopExp import TopExp_Explorer
            from OCC.Core.TopAbs import TopAbs_FACE
            from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
            from OCC.Core.IFSelect import IFSelect_RetDone

            exp = TopExp_Explorer(occ_shape, TopAbs_FACE)
            faces_to_export = []
            idx = 0
            while exp.More():
                # use the explorer's current shape directly (it's a face)
                f = exp.Current()
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
                    os.path.dirname(stepfile), f"gmsh_candidates_surface_{dup_tag}.step"
                )
                writer = STEPControl_Writer()
                writer.Transfer(comp, STEPControl_AsIs)
                status = writer.Write(out_step)
                if status == IFSelect_RetDone:
                    print(f"Exported candidate faces to {out_step}")
                else:
                    raise RuntimeError("Failed to write candidate faces STEP")
            else:
                raise RuntimeError(
                    "No OCC faces found whose bbox contains the duplicate triangle centroid"
                )
        else:
            print("occ_shape not provided; cannot export candidate OCC faces")

    if surface_only:
        # User requested only surface mesh: write and return surface elements
        gmsh.write(out_msh)
        print(f"gmsh: wrote surface mesh to {out_msh}")
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
        elements = []
        for i, etype in enumerate(types):
            etags = elem_tags[i]
            nodes_flat = elem_node_tags[i]
            props = gmsh.model.mesh.getElementProperties(etype)
            num_nodes_per_elem = props[3]
            elems = []
            for j in range(len(etags)):
                start = j * num_nodes_per_elem
                elems.append(
                    [int(n) for n in nodes_flat[start : start + num_nodes_per_elem]]
                )
            elements.append((int(etype), etags, elems))

        gmsh.finalize()
        return coords, elements

    # Now try 3D mesh generation
    print("gmsh: generating 3D mesh (this may take a moment)")
    gmsh.model.mesh.generate(3)
    print("gmsh: 3D mesh generation succeeded")
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
    mesh_size = 0.5  # global target characteristic length for mesh (reduced)
    # tighten local refinement around the hole (non-destructive)
    local_size_min = 0.5  # min element size near hole
    local_dist_min = 0.5
    local_dist_max = 2.0
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

    # run gmsh: request volume mesh (tetrahedralization of solid)
    coords, elements = run_gmsh_on_step(
        stepfile,
        out_msh,
        mesh_size=mesh_size,
        occ_shape=sewed_shape,
        surface_only=False,
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

    # Try to build an in-memory skfem MeshTet (no intermediate files)
    def try_make_skfem_mesh(coords_map, tets_list):
        # build contiguous node list and mapping
        node_tags = sorted(coords_map.keys())
        tag_to_idx = {tag: i for i, tag in enumerate(node_tags)}
        nodes = np.array([coords_map[tag] for tag in node_tags], dtype=float)

        # build tet index array
        tets_idx = np.array(
            [[tag_to_idx[int(n)] for n in tet] for tet in tets_list], dtype=int
        )

        # import skfem MeshTet — let ImportError propagate if missing
        from skfem import MeshTet

        # skfem.MeshTet expects nodes as shape (3, n_points) and elems as (4, n_elems)
        # transpose our arrays to match that convention and let errors propagate
        mesh = MeshTet(nodes.T, tets_idx.T)
        print(
            "skfem MeshTet created with nodes.shape",
            nodes.T.shape,
            "tets.shape",
            tets_idx.T.shape,
        )
        return mesh

    skfem_mesh = None
    # container for shapes of the deformed surface triangles (populated after solve)
    deformed_tri_shapes = None
    if len(tets) > 0:
        skfem_mesh = try_make_skfem_mesh(coords, tets)
        if skfem_mesh is not None:
            print("In-memory skfem mesh ready for analysis (no files written)")
            # --- run a simple 3D linear elasticity self-weight analysis ---
            from skfem import Basis, ElementVector, ElementTetP1, asm, solve, condense
            from skfem.models.elasticity import (
                linear_elasticity,
                lame_parameters,
                linear_stress,
            )
            from skfem import LinearForm, BilinearForm
            from skfem.helpers import dot, sym_grad

            # material and loading
            E = 2.1e11  # Pa (steel-like)
            nu = 0.3
            rho = 7800.0  # kg/m3
            g = 9.81  # m/s2
            # gravity along negative Y as requested
            body_force = rho * g * np.array([0.0, -1.0, 0.0])

            # setup vector basis on the tetra mesh
            vbasis = Basis(skfem_mesh, ElementVector(ElementTetP1()))

            # elasticity weak form
            weak = linear_elasticity(*lame_parameters(E, nu))

            @LinearForm
            def lf(v, w):
                # constant body force
                return (
                    body_force[0] * v[0] + body_force[1] * v[1] + body_force[2] * v[2]
                )

            print("Assembling elasticity system...")
            A = asm(weak, vbasis)
            fvec = asm(lf, vbasis)

            # apply clamped BC at the y==0 face (cantilever at start of geometry)
            tol = 1e-6
            clamped = vbasis.get_dofs(lambda x: x[1] <= tol).flatten()
            D = clamped

            print(f"Dirichlet DOFs (clamped) count: {D.size}")

            # solve
            print("Solving linear system...")
            u = solve(*condense(A, fvec, D=D))
            # recover full vector with condensed values
            from skfem import condense

            # expand reduced solution `u` into full DOF vector using complement dofs
            # compute free DOF indices as complement of Dirichlet dofs
            all_dofs = np.arange(vbasis.N)
            D_arr = np.asarray(D, dtype=int).flatten()
            interior = np.setdiff1d(all_dofs, D_arr)
            print(
                "reduced solution length (u):",
                getattr(u, "shape", getattr(u, "__len__", lambda: "unknown")()),
            )
            print("interior dofs length:", interior.size)
            ufull = np.zeros(vbasis.N)
            # if u length matches interior, assign; if u matches full, just take it
            try:
                if getattr(u, "shape", None) and u.shape[0] == interior.size:
                    ufull[interior] = u
                elif getattr(u, "shape", None) and u.shape[0] == vbasis.N:
                    ufull = u
                else:
                    # attempt to flatten and assign conservatively
                    uarr = np.asarray(u).ravel()
                    if uarr.size == interior.size:
                        ufull[interior] = uarr
                    elif uarr.size == vbasis.N:
                        ufull = uarr
                    else:
                        raise ValueError("Unexpected solution vector size")
            except Exception:
                raise

            print("Elastic solve complete. Computing von Mises at nodal points...")
            print(
                "ufull length:",
                getattr(ufull, "shape", getattr(ufull, "__len__", lambda: "unknown")()),
            )
            print("vbasis N:", vbasis.N)
            # compute stress tensor via C(sym_grad(u)) and project — attempt element-wise projection
            C = linear_stress(*lame_parameters(E, nu))
            # create a DG basis for stress projection (raise if ElementTetDG unavailable)
            try:
                from skfem import ElementTetDG
            except Exception as e:
                raise ImportError(
                    "ElementTetDG not available in this skfem installation; install a skfem version that provides ElementTetDG to perform DG stress projection"
                ) from e
            dg = vbasis.with_element(ElementTetDG(ElementTetP1()))

            # build nodal displacement array (shape (3, n_nodes)) from `ufull` robustly
            # skfem vector basis has vbasis.N == 3 * n_nodes
            ufarr = np.asarray(ufull).ravel()
            n_nodes = getattr(vbasis.mesh, "p", None)
            if n_nodes is None:
                # fallback to skfem_mesh
                n_nodes = skfem_mesh.p.shape[1]
            else:
                n_nodes = vbasis.mesh.p.shape[1]

            u_nodal = None
            try:
                if ufarr.size == 3 * n_nodes:
                    # try ordering [ux0,uy0,uz0, ux1,uy1,uz1, ...]
                    try:
                        u_nodal = ufarr.reshape((n_nodes, 3)).T
                    except Exception:
                        u_nodal = ufarr.reshape((3, n_nodes))
                elif ufarr.size == vbasis.N:
                    u_nodal = ufarr.reshape((3, n_nodes))
                else:
                    # last resort: use interpolate (may return unexpected shape)
                    u_nodal = vbasis.interpolate(ufull)
            except Exception as e:
                raise RuntimeError(f"Failed to construct nodal displacement array: {e}")

            # ensure u_nodal is a numpy array with shape (3, n_nodes)
            u_nodal = np.asarray(u_nodal)
            if u_nodal.ndim != 2 or u_nodal.shape[0] != 3:
                # if interpolate returned extra dims (e.g., (3, n, m)), try to squeeze
                u_nodal = np.squeeze(u_nodal)
            if u_nodal.ndim != 2 or u_nodal.shape[0] != 3:
                raise RuntimeError(
                    f"Unexpected u_nodal shape after construction: {u_nodal.shape}"
                )

            # obtain a skfem Function view for stress evaluation (let errors propagate)
            from skfem.helpers import sym_grad

            u_func = vbasis.interpolate(ufull)
            stress = C(sym_grad(u_func))
            # stress expected to be a 3x3 array-like per node/element; compute von Mises
            sxx = stress[0, 0]
            syy = stress[1, 1]
            szz = stress[2, 2]
            sxy = stress[0, 1]
            syz = stress[1, 2]
            sxz = stress[0, 2]
            von = np.sqrt(
                0.5
                * (
                    (sxx - syy) ** 2
                    + (syy - szz) ** 2
                    + (szz - sxx) ** 2
                    + 6.0 * (sxy**2 + syz**2 + sxz**2)
                )
            )

            if von is not None:
                vnod = von
                print("von Mises: min", float(np.min(vnod)), "max", float(np.max(vnod)))
                # compute nodal displacement magnitudes and report maximum (let errors raise)
                un = np.asarray(u_nodal)
                disp_mag = np.sqrt(un[0, :] ** 2 + un[1, :] ** 2 + un[2, :] ** 2)
                imax = int(np.argmax(disp_mag))
                max_disp = float(disp_mag[imax])
                # node coordinates from the mesh
                pcoords = skfem_mesh.p[:, imax]
                node_coord = (float(pcoords[0]), float(pcoords[1]), float(pcoords[2]))
                print(
                    "Max displacement:",
                    max_disp,
                    "m at node index",
                    imax,
                    "coord:",
                    node_coord,
                )
                # prepare deformed triangle faces (amplify Y component by 1000x)
                deformed_tri_shapes = []
                node_tags_sorted = sorted(coords.keys())
                tag_to_idx = {tag: i for i, tag in enumerate(node_tags_sorted)}
                for tri in tris:
                    t0, t1, t2 = int(tri[0]), int(tri[1]), int(tri[2])
                    i0 = tag_to_idx[t0]
                    i1 = tag_to_idx[t1]
                    i2 = tag_to_idx[t2]
                    d0 = u_nodal[:, i0].copy()
                    d1 = u_nodal[:, i1].copy()
                    d2 = u_nodal[:, i2].copy()
                    # d0[1] *= 10.0**4
                    # d1[1] *= 10.0**4
                    # d2[1] *= 10.0**4
                    p0c = coords[t0]
                    p1c = coords[t1]
                    p2c = coords[t2]
                    p0d = gp_Pnt(
                        p0c[0] + float(d0[0]),
                        p0c[1] + float(d0[1]),
                        p0c[2] + float(d0[2]),
                    )
                    p1d = gp_Pnt(
                        p1c[0] + float(d1[0]),
                        p1c[1] + float(d1[1]),
                        p1c[2] + float(d1[2]),
                    )
                    p2d = gp_Pnt(
                        p2c[0] + float(d2[0]),
                        p2c[1] + float(d2[1]),
                        p2c[2] + float(d2[2]),
                    )
                    fd = make_face(make_polygon([p0d, p1d, p2d], True))
                    deformed_tri_shapes.append(fd)
            else:
                print("von Mises could not be computed with current projection method.")

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

        # display deformed surface (if prepared): BLUE1
        if deformed_tri_shapes:
            for idx, shp in enumerate(deformed_tri_shapes):
                # display without immediate update for speed, set color to BLUE1
                display.DisplayShape(shp, color="BLUE1", update=False)
            # final update
            # display.View.Redraw()

    for tri in tris:
        t0, t1, t2 = int(tri[0]), int(tri[1]), int(tri[2])
        p0c = coords[t0]
        p1c = coords[t1]
        p2c = coords[t2]
        p0 = gp_Pnt(p0c[0], p0c[1], p0c[2])
        p1 = gp_Pnt(p1c[0], p1c[1], p1c[2])
        p2 = gp_Pnt(p2c[0], p2c[1], p2c[2])
        f = make_face(make_polygon([p0, p1, p2], True))
        display.DisplayShape(p0)
        display.DisplayShape(p1)
        display.DisplayShape(p2)
        # display.DisplayShape(f, transparency=0.5)
    display.DisplayShape(shape, transparency=0.5)

    display.FitAll()
    display.View.Dump("core_solid_volmesh_occ.png")
    start_display()
