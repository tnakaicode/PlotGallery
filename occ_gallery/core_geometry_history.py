from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepTools import BRepTools_History

# Create the first shape: a box
box = BRepPrimAPI_MakeBox(100, 100, 100).Shape()

# Create the second shape: a cylinder
cylinder = BRepPrimAPI_MakeCylinder(
    gp_Ax2(gp_Pnt(50, 50, 0), gp_Dir(0, 0, 1)), 50, 150
).Shape()

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
print(f"Merge operation successful: {fuse.IsDone()}")
print(f"Final merged shape: {merged_shape}")

# Get the history directly from the fuse operation
fuse_history = fuse.History()

# Check basic operation details
print(f"\nOriginal box: {box}")
print(f"Original cylinder: {cylinder}")

# Try to get generated shapes using the fuse operation history
try:
    box_generated = fuse_history.Generated(box)
    print(f"Number of shapes generated from box: {box_generated.Size()}")

    cylinder_generated = fuse_history.Generated(cylinder)
    print(f"Number of shapes generated from cylinder: {cylinder_generated.Size()}")

    # Check for modifications
    box_modified = fuse_history.Modified(box)
    print(f"Number of shapes modified from box: {box_modified.Size()}")

    cylinder_modified = fuse_history.Modified(cylinder)
    print(f"Number of shapes modified from cylinder: {cylinder_modified.Size()}")

    # Check if shapes were removed
    print(f"Box removed: {fuse_history.IsRemoved(box)}")
    print(f"Cylinder removed: {fuse_history.IsRemoved(cylinder)}")

except Exception as e:
    print(f"Error accessing history: {e}")

# Alternative: Use the BRepTools_History directly without merging
print("\n--- Using direct BRepTools_History ---")
try:
    direct_history = BRepTools_History()
    # The history might be empty since we're not properly connecting it to operations
    print(f"Direct history object created: {direct_history}")
except Exception as e:
    print(f"Error creating direct history: {e}")

print("\nNote: In OpenCASCADE, history tracking depends on the specific operation and")
print(
    "how the shapes are processed. Some operations may not generate detailed history."
)
