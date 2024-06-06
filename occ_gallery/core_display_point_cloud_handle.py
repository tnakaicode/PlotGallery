from OCC.Core.gp import gp_Pnt
from OCC.Core.Graphic3d import Graphic3d_ArrayOfPoints
from OCC.Core.AIS import AIS_PointCloud


from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


def pointcloud():

    points3d = Graphic3d_ArrayOfPoints(100000)

    for idx in range(100):
        for idy in range(100):
            for idz in range(10):
                x = 0 + idx * 0.1
                y = 0 + idy * 0.1
                z = 0 + idz * 0.1

                points3d.AddVertex(gp_Pnt(x, y, z))

    pointCloud = AIS_PointCloud()
    # pointHandle = points3d.GetHandle()
    pointCloud.SetPoints(points3d)
    # pointCloudHandle = pointCloud.GetHandle()
    display.Context.Display(pointCloud, True)

    def ErasePointCloud():
        display.Context.Erase(pointCloud)

    add_menu("Erase")
    add_function_to_menu("Erase", ErasePointCloud)
    display.FitAll()
    display.View_Iso()
    start_display()


if __name__ == "__main__":
    pointcloud()
