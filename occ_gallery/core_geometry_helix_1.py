import sys
import numpy as np
from OCC.Display.backend import load_backend
load_backend("pyqt5") # Ensure Qt backend is loaded

from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections, BRepOffsetAPI_MakeThickSolid
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display.qtDisplay import qtViewer3d
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRep import BRep_Builder

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QFormLayout, QLineEdit, QDialogButtonBox

class InputDialog(QDialog):
def init(self):
super().init()
self.setWindowTitle("Enter Parameters")

    self.radius_input = QLineEdit("5.0")
    self.height_input = QLineEdit("20.0")
    self.turns_input = QLineEdit("5")
    self.width_input = QLineEdit("1.0")
    self.thickness_input = QLineEdit("1.0")
    
    self.layout.addRow("Cylinder Radius:", self.radius_input)
    self.layout.addRow("Cylinder Height:", self.height_input)
    self.layout.addRow("Helix Turns:", self.turns_input)
    self.layout.addRow("Ribbon Width:", self.width_input)
    self.layout.addRow("Ribbon Thickness:", self.thickness_input)
    
    self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    self.buttons.accepted.connect(self.accept)
    self.buttons.rejected.connect(self.reject)
    self.layout.addWidget(self.buttons)
    
    self.setLayout(self.layout)

def get_values(self):
    return {
        "cylinder_radius": float(self.radius_input.text()),
        "cylinder_height": float(self.height_input.text()),
        "helix_turns": int(self.turns_input.text()),
        "ribbon_width": float(self.width_input.text()),
        "ribbon_thickness": float(self.thickness_input.text()),
    }

class HelixRibbonApp(QMainWindow):
def init(self):
super().init()
self.setWindowTitle("Helix Ribbon on Cylinder")
self.setGeometry(100, 100, 800, 600)

    self.display_widget = qtViewer3d(self)
    self.display_widget.setMinimumSize(800, 600)
    self.display = self.display_widget._display
    self.display.EraseAll()

    self.params = {
        "cylinder_radius": 75.0,
        "cylinder_height": 300.0,
        "helix_turns": 5,
        "ribbon_width": 1.0,
        "ribbon_thickness": 1.0,
    }

    self.shapes = []  # Store references to displayed shapes
    self.initUI()

def initUI(self):
    central_widget = QWidget()
    layout = QVBoxLayout()

    layout.addWidget(self.display_widget)

    input_button = QPushButton("Enter Inputs")
    input_button.clicked.connect(self.open_input_dialog)
    layout.addWidget(input_button)

    generate_button = QPushButton("Generate Model")
    generate_button.clicked.connect(self.generate_model)
    layout.addWidget(generate_button)

    export_button = QPushButton("Export as STEP")  # NEW BUTTON
    export_button.clicked.connect(self.export_as_step)
    layout.addWidget(export_button)

    central_widget.setLayout(layout)
    self.setCentralWidget(central_widget)

def open_input_dialog(self):
    # Set initial values in dialog based on current params
    dialog = InputDialog()

    # Set initial values to dialog fields
    dialog.radius_input.setText(str(self.params["cylinder_radius"]))
    dialog.height_input.setText(str(self.params["cylinder_height"]))
    dialog.turns_input.setText(str(self.params["helix_turns"]))
    dialog.width_input.setText(str(self.params["ribbon_width"]))
    dialog.thickness_input.setText(str(self.params["ribbon_thickness"]))

    if dialog.exec_() == QDialog.Accepted:
        # After dialog is accepted, get the new values and update the params
        self.params = dialog.get_values()
        print(self.params)  # You can print or log to check the updated values

def clear_previous_shapes(self):
    """Remove all previously displayed shapes from the viewer."""
    context = self.display.Context  # Get the interactive context

    for shape in self.shapes:
        ais_object = context.SelectedInteractive()  # Try getting the AIS object
        if ais_object:
            context.Remove(ais_object, True)  # Remove AIS object from context

    self.display.EraseAll()  # Ensure all objects are erased from the viewer
    self.shapes.clear()  # Clear the stored shapes list

def export_as_step(self):
    """Export the generated model as a STEP file."""
    if not self.shapes:
        print("No shapes to export!")
        return

    # Create a compound to store all shapes
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)

    for shape in self.shapes:
        builder.Add(compound, shape)

    # Initialize the STEP writer
    step_writer = STEPControl_Writer()
    step_writer.Transfer(compound, STEPControl_AsIs)

    # Write to file
    status = step_writer.Write("exported_model.step")
    if status == IFSelect_RetDone:
        print("STEP file exported successfully: exported_model.step")
    else:
        print("Failed to export STEP file.")

def generate_model(self):
    self.clear_previous_shapes()  # Clear existing shapes before generating new ones
    
    # Remaining code for generating the cylinder and ribbon remains unchanged
    cylinder_radius = self.params["cylinder_radius"]
    cylinder_height = self.params["cylinder_height"]
    helix_turns = self.params["helix_turns"]
    ribbon_width = self.params["ribbon_width"]
    ribbon_thickness = self.params["ribbon_thickness"]
    points_per_turn = 30000
    cylinder_wall_thickness = 0.5
    total_points = helix_turns * points_per_turn
    #dz = cylinder_height / total_points
    dz=0.0005

    inner_points = []
    outer_points = []

    for i in range(total_points):
        angle = 2 * np.pi * i / points_per_turn
        z = dz * i
        x_inner = cylinder_radius * np.cos(angle)
        y_inner = cylinder_radius * np.sin(angle)
        inner_points.append(gp_Pnt(x_inner, y_inner, z))
        x_outer = (cylinder_radius + ribbon_width) * np.cos(angle)
        y_outer = (cylinder_radius + ribbon_width) * np.sin(angle)
        outer_points.append(gp_Pnt(x_outer, y_outer, z))

    def build_bspline(points_list):
        pts_array = TColgp_Array1OfPnt(1, len(points_list))
        for idx, pt in enumerate(points_list):
            pts_array.SetValue(idx + 1, pt)
        return GeomAPI_PointsToBSpline(pts_array).Curve()

    inner_bspline = build_bspline(inner_points)
    outer_bspline = build_bspline(outer_points)

    inner_edge = BRepBuilderAPI_MakeEdge(inner_bspline).Edge()
    outer_edge = BRepBuilderAPI_MakeEdge(outer_bspline).Edge()
    inner_wire = BRepBuilderAPI_MakeWire(inner_edge).Wire()
    outer_wire = BRepBuilderAPI_MakeWire(outer_edge).Wire()

    sections = BRepOffsetAPI_ThruSections(True, True, 1e-6)
    sections.AddWire(inner_wire)
    sections.AddWire(outer_wire)
    ribbon = sections.Shape()

    thick_builder = BRepOffsetAPI_MakeThickSolid()
    thick_builder.MakeThickSolidBySimple(ribbon, ribbon_thickness)
    thick_ribbon = thick_builder.Shape()

    outer_cylinder = BRepPrimAPI_MakeCylinder(cylinder_radius, cylinder_height).Shape()
    inner_cylinder = BRepPrimAPI_MakeCylinder(cylinder_radius - cylinder_wall_thickness, cylinder_height).Shape()
    hollow_cylinder = BRepAlgoAPI_Cut(outer_cylinder, inner_cylinder).Shape()

    self.display.DisplayShape(hollow_cylinder, update=True, transparency=0.5)
    self.shapes.append(hollow_cylinder)  # Keep reference to hollow cylinder

    red_color = Quantity_Color(1.0, 0.0, 0.0, Quantity_TOC_RGB)
    self.display.DisplayShape(thick_ribbon, update=True, color=red_color, transparency=0)
    self.shapes.append(thick_ribbon)  # Keep reference to thick ribbon

    self.display.FitAll()

if __name__ == "main":
    app = QApplication(sys.argv)
    mainWin = HelixRibbonApp()
    mainWin.show()
    sys.exit(app.exec_())
    # https://github.com/tpaviot/pythonocc-core/issues/1409