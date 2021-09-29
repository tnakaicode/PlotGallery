# https://github.com/tpaviot/pythonocc-core/issues/1001

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()
from math import pi

angle1 = 0
angle2 = 45
angle = 90
R1 = 10
R2 = 2

# Make a torus with angles on the small circle.
#   @param r1 [in] distance from the center of the pipe to the center of the torus
#   @param r2 [in] radius of the pipe
#   @param angle1 [in] first angle to create a torus ring segment
#   @param angle2 [in] second angle to create a torus ring segment
#   @param angle [in] angle to create a torus pipe segment.

my_torus = BRepPrimAPI_MakeTorus(
    R1, R2, angle1 / 180 * pi, angle2 / 180 * pi, angle / 180 * pi).Shell()
display.DisplayShape(my_torus, update=True)
start_display()
