from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.STEPControl import STEPControl_Reader

from OCC.Core.BRep import BRep_Tool
from OCC.Core.Geom import (Geom_SphericalSurface, Geom_ToroidalSurface, Geom_Plane, Geom_CylindricalSurface)
from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Shape

from OCC.Extend.TopologyUtils import TopologyExplorer


def get_shape_from_path(filepath: str) -> TopoDS_Shape:
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(filepath)

    if status == IFSelect_RetDone:  # check status
        step_reader.TransferRoot(1)
        a_res_shape = step_reader.Shape(1)
        try:
            return next(TopologyExplorer(a_res_shape).solids())
        except StopIteration:
            raise ValueError('Could not import file {}'.format(filepath))
    else:
        raise ValueError(filepath)


def get_face_types(topo: TopologyExplorer) -> dict:
    face_types = {}
    for current_face in topo.faces():
        face_types[current_face] = get_face_type(current_face)
    return face_types


def get_face_type(face: TopoDS_Face) -> str:
    hs = BRep_Tool.Surface(face)
    print(hs)
    print(hs.get_type_name())
    print(hs.get_type_descriptor().This())
    print(Geom_CylindricalSurface(hs))
    if Geom_Plane.DownCast(hs) is not None:
        return 'plane'
    elif Geom_CylindricalSurface.DownCast(hs) is not None:
        return 'cylinder'
    elif Geom_SphericalSurface.DownCast(hs) is not None:
        return 'sphere'
    elif Geom_ToroidalSurface.DownCast(hs) is not None:
        return 'tore'
    else:
        return 'unkown'


if __name__ == "__main__":
    # https://github.com/tpaviot/pythonocc-core/issues/1366
    shape = get_shape_from_path("./occ-error.stp")

    my_topo = TopologyExplorer(shape, ignore_orientation=False)
    res = get_face_types(my_topo)
