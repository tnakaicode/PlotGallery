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

import os
import tempfile
import sys

from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeSphere,
)
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone


def make_shape_box(size=100.0):
    # simple box solid
    return BRepPrimAPI_MakeBox(size, size * 0.6, size * 0.4).Shape()


def write_step(shape, filename):
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

    if mesh_size is not None:
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)

    print("gmsh: generating 3D mesh (this may take a moment)")
    gmsh.model.mesh.generate(3)
    gmsh.write(out_msh)
    print(f"gmsh: wrote volume mesh to {out_msh}")
    gmsh.finalize()


if __name__ == "__main__":
    # --- User-editable parameters (no CLI allowed) ---
    out_msh = "core_solid_volmesh.msh"  # output mesh filename
    mesh_size = 5.0  # target characteristic length for mesh
    size = 100.0  # shape size parameter
    # -------------------------------------------------

    shape = make_shape_box(size=size)

    td = tempfile.mkdtemp(prefix="occ2gmsh_")
    stepfile = os.path.join(td, "shape.step")
    print(f"Writing STEP to {stepfile}")
    write_step(shape, stepfile)

    run_gmsh_on_step(stepfile, out_msh, mesh_size=mesh_size)
