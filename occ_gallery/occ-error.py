from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.STEPControl import STEPControl_Reader

from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.Geom import (Handle_Geom_SphericalSurface_DownCast, Handle_Geom_ToroidalSurface_DownCast, Handle_Geom_Plane_DownCast,
                           Handle_Geom_CylindricalSurface_DownCast)
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
    hs = BRep_Tool_Surface(face)
    if Handle_Geom_Plane_DownCast(hs) is not None:
        return 'plane'
    elif Handle_Geom_CylindricalSurface_DownCast(hs) is not None:
        return 'cylinder'
    elif  Handle_Geom_SphericalSurface_DownCast(hs) is not None:
        return 'sphere'
    elif Handle_Geom_ToroidalSurface_DownCast(hs) is not None:
        return 'tore'
    else:
        return 'unkown'


if __name__ == "__main__":
    # https://github.com/tpaviot/pythonocc-core/issues/1366
    shape = get_shape_from_path("./occ-error.stp")

    my_topo = TopologyExplorer(shape, ignore_orientation=False)
    res = get_face_types(my_topo)