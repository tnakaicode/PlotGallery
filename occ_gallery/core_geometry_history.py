from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepTools import BRepTools_History

# Create the first shape: a box
box = BRepPrimAPI_MakeBox(100, 100, 100).Shape()

# Create the second shape: a cylinder
cylinder = BRepPrimAPI_MakeCylinder(
    gp_Ax2(gp_Pnt(50, 50, 0), gp_Dir(0, 0, 1)), 50, 150).Shape()

# Perform the merge operation
fuse = BRepAlgoAPI_Fuse(box, cylinder)
fuse.Build()

# Get the resulting shape
merged_shape = fuse.Shape()

# Create a history object to track the operation
history = BRepTools_History()
history.Merge(fuse.History())

# Print out the history of the merge operation
print("History of the merge operation:")
for i in range(history.Generated(box).Length()):
    print(f"Generated from box: {history.Generated(box).Value(i + 1)}")
for i in range(history.Generated(cylinder).Length()):
    print(
        f"Generated from cylinder: {history.Generated(cylinder).Value(i + 1)}")
