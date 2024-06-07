# https://github.com/tpaviot/pythonocc-core/issues/1300
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox
from OCC.Core.AIS import AIS_InteractiveContext, AIS_InteractiveObject
from OCC.Core.AIS import AIS_Shape, AIS_ListOfInteractive, AIS_PointCloud


class My_AIS_Shape(AIS_Shape):
    def __init__(self, shape, my_id):
        super(My_AIS_Shape, self).__init__(shape)
        self.ID = my_id


display, start_display, add_menu, add_function_to_menu = init_display()
context = display.GetContext()

my_sphere = BRepPrimAPI_MakeSphere(100.).Shape()
my_box = BRepPrimAPI_MakeBox(100, 100, 100).Shape()
new_my_ais_shape1 = My_AIS_Shape(my_sphere, "My_ID1")
new_my_ais_shape2 = My_AIS_Shape(my_box, "My_ID2")
context.Display(new_my_ais_shape1, True)
#context.Display(AIS_Shape(my_box), True)
context.DisplaySelected(True)

# There is no problem assigning an instance of this class to the AIS_Context and manipulating it via the AIS_Context.
# My goal now is to use the "mouse picking logic" functions of the AIS_Context:

# tuple = Window Size in Pixel
size = display.View.Window().Size()
# Sphere is now dynamic highlighted
context.MoveTo(int(size[0] / 2), int(size[1] / 2), display.View, True)

# The problem now is that ais_context.DetectedInteractive() returns an AIS_InteractiveObject
# whose class is AIS_Shape and not My_AIS_Shape as hoped.
ais_list = AIS_ListOfInteractive()

if context.HasDetected():
    detected_interactive = context.DetectedInteractive()
    # detected_interactive = context.DetectedCurrentShape()
    # <class 'AIS_InteractiveObject'>
    print(detected_interactive)
    print(context.DetectedShape())
    # <class 'OCC.Core.AIS.AIS_InteractiveObject'>
    print(type(detected_interactive))
    print(detected_interactive.GetRefCount())
    print(detected_interactive.IsInstance("AIS_Shape"))       # True
    print(detected_interactive.IsInstance("My_AIS_Shape"))    # False

print(context.DisplayedObjects(ais_list))
print(ais_list.Size())
print(ais_list.Last())
display.DisplayShape(context.DetectedShape(), color="BLUE1")
# Could it be that the problem is due to the RTTI (Run Time Type Information)?
# Doesn’t a new class of RTTI need to be announced?
#
# Regarding your proposed solution to create a subclass of the AIS_InteractiveContext:
# How could this happen, can you show me an example of this?
#
# As an alternative, I have already tried assigning an owner to the AIS_Shape (of type TCollection_HAsciiString)
# but unfortunately that doesn't work either (context.DetectedOwner()).
#
# How else could I easily assign a unique ID to an AIS_Shape?

start_display()
