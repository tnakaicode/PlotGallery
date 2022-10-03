import numpy as np

from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Ax3
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir
from OCC.Core.gp import gp_XYZ
from OCC.Core.gp import gp_Lin, gp_Elips, gp_Pln
from OCC.Core.gp import gp_Mat, gp_GTrsf, gp_Trsf
from OCC.Core.gp import gp_Cylinder
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_Array2OfPnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepProj import BRepProj_Projection
from OCC.Core.BRepAlgo import BRepAlgo_FaceRestrictor
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.GeomAbs import GeomAbs_G1, GeomAbs_G2
from OCC.Extend.DataExchange import write_step_file
from OCCUtils.Construct import make_face, make_polygon, make_plane


def spl_face(px, py, pz):
    nx, ny = px.shape
    pnt_2d = TColgp_Array2OfPnt(1, nx, 1, ny)
    for row in range(pnt_2d.LowerRow(), pnt_2d.UpperRow() + 1):
        for col in range(pnt_2d.LowerCol(), pnt_2d.UpperCol() + 1):
            i, j = row - 1, col - 1
            pnt = gp_Pnt(px[i, j], py[i, j], pz[i, j])
            pnt_2d.SetValue(row, col, pnt)
            #print (i, j, px[i, j], py[i, j], pz[i, j])

    api = GeomAPI_PointsToBSplineSurface(pnt_2d, 3, 8, GeomAbs_G2, 0.001)
    api.Interpolate(pnt_2d)
    face = BRepBuilderAPI_MakeFace(api.Surface(), 1e-6).Face()
    return face


def make_trimmedface(poly, face, axs=gp_Ax3()):
    """make trimmed face by projected poly
    Args:
        poly (TopoDS_Wire): 
        face (TopoDS_Face): 
        axs (gp_Ax3, optional): Defaults to gp_Ax3().
    Returns:
        face (TopoDS_Face)
    """
    proj = BRepProj_Projection(poly, face, axs.Direction())
    # make hole
    # face = make_face(face, poly_proj)
    api_face = BRepAlgo_FaceRestrictor()
    api_face.Init(face, True, True)
    api_face.Add(poly)
    api_face.Perform()
    return api_face.Current()


display, start_display, add_menu, add_function_to_menu = init_display()

# make polygon on XY-plane
pts = [
    gp_Pnt(-50, -50, 0),
    gp_Pnt(50, -50, 0),
    gp_Pnt(50, 50, 0),
    gp_Pnt(0, 60, 0),
    gp_Pnt(-50, 50, 0)
]
poly_2d = make_polygon(pts, True)
display.DisplayShape(poly_2d)

# make plane on gp_Pnt(0,0,10) which size is over polygon on XY-plane
plan = make_plane(gp_Pnt(0, 0, 10),
                  extent_x_min=-60, extent_x_max=60,
                  extent_y_min=-40, extent_y_max=55)
display.DisplayShape(plan, transparency=0.7)

# make curved surface by spline on gp_Pnt(0,0,10) which size is same plane
px = np.linspace(-60, 60, 100)
py = np.linspace(-40, 50, 200)
mesh = np.meshgrid(px, py)
surf = mesh[0]**2 / 1000 + mesh[1]**2 / 2000 + 10.0
face = spl_face(*mesh, surf)
display.DisplayShape(face, transparency=0.9)

# projection polygon to curved surface
# the current TopoDS_Wire is not connectted each other beacause the size of curved surface is larger than polygon on XY-Plane.
idx = 10
proj_idx = 0
proj = BRepProj_Projection(poly_2d, face, gp_Dir(0, 0, 1))
while proj.More() and proj_idx < idx:
    poly = proj.Current()
    proj.Next()
    proj_idx += 1
    display.DisplayShape(poly, color="BLUE1")

face_trim = make_trimmedface(poly_2d, face)
print(face_trim)
#display.DisplayShape(face_trim, color="RED")

display.FitAll()
start_display()

# TopoDS_FaceをPolygonで制限する方法について
# あるTopoDS_FaceをClosedなTopoDS_Wire(Polygon)で制限する方法を考えています。その過程で、ある平面上にあるPolygonをFaceに射影する必要があります。
# FaceをPolygonのある平面(コード中のXY-Plane)に射影した領域が、Polygonの領域と比べて小さかった場合、射影されるFace上のPolygonは不連結になります。
# この問題を解決し、TopoDS_Faceを任意のPolygonで制限する方法良い方法はないでしょうか？

# How to restrict a TopoDS_Face with Polygon
# I am trying to figure out how to restrict a certain TopoDS_Face with a closed TopoDS_Wire (Polygon). In the process, I need to project a Polygon on a certain plane onto a Face.
# If the area of the projection of Face onto a plane of Polygon (XY-Plane in the sample code) is small compared to the area of Polygon, the Polygon on the projected Face will be dis-connected.
# Is there a better way to solve this problem and limit TopoDS_Face to any Polygon?
