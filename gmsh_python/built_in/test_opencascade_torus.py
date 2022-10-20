from math import pi

from pygmsh import geo

from helpers import compute_volume

import pygmsh


def test():
    with pygmsh.occ.Geometry() as geom:
        geom.add_torus([0.0, 0.0, 0.0], 1.0, 0.3, 1.25 * pi, mesh_size=0.1)
        mesh = geom.generate_mesh()

    ref = 1.09994740709
    assert abs(compute_volume(mesh) - ref) < 1.0e-2 * ref
    return geom, mesh


if __name__ == "__main__":
    geom, mesh = test()
    mesh.write("occ_torus.vtu")
    geom.synchronize()
