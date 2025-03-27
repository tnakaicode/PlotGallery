from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeEdge
from OCC.Core.gp import gp_Pnt, gp_Ax1, gp_OZ, gp_Circ, gp_Ax2, gp_Dir
from OCC.Core.GC import GC_MakeArcOfCircle
from OCC.Core.GeomAbs import *
from OCC.Display.SimpleGui import init_display


def create_revolved_solid():
    # Define a half-circle arc as the profile
    radius = 50.0
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), radius)
    arc = GC_MakeArcOfCircle(circle, gp_Pnt(
        0, radius, 0), gp_Pnt(0, -radius, 0), True).Value()

    # Create edges from the arc
    arc_edge = BRepBuilderAPI_MakeEdge(arc).Edge()

    # Close the profile by adding a vertical line to the Z-axis
    line_edge = BRepBuilderAPI_MakeEdge(
        gp_Pnt(0, radius, 0), gp_Pnt(0, -radius, 0)).Edge()

    # Create a closed wire
    wire_maker = BRepBuilderAPI_MakeWire()
    wire_maker.Add(arc_edge)
    wire_maker.Add(line_edge)
    wire = wire_maker.Wire()

    # Define the axis of revolution (Z-axis)
    revolution_axis = gp_Ax1(gp_Pnt(0, 2 * radius, 0), gp_Dir(1, 0, 0))

    # Perform the revolution
    revolved_solid = BRepPrimAPI_MakeRevol(wire, revolution_axis).Shape()

    return revolved_solid


if __name__ == "__main__":
    shape = create_revolved_solid()

    display, start_display, _, _ = init_display()

    # adjust default display properties (Prs3d_Drawer in AIS_InteractiveContext)
    display.Context.DefaultDrawer().SetFaceBoundaryDraw(True)
    display.Context.DefaultDrawer().SetFaceBoundaryUpperContinuity(GeomAbs_G2)

    display.DisplayShape(shape, update=True)
    display.FitAll()
    start_display()
