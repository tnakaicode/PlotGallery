#!/usr/bin/env python

"""
Physical Batten Simulation using FairCurve
- Creates a 3D box representing a physical batten (thin plate)
- Uses FairCurve to calculate bending deformation
- Applies deformation to the box using ThroughSections or Spine
- Visualizes the realistic physical bending behavior
"""

import math
import time
import sys
import numpy as np

from OCC.Core.gp import (gp_Pnt2d, gp_Pnt, gp_Vec, gp_Dir, gp_Ax2, gp_Pln, 
                         gp_Trsf, gp_GTrsf)
from OCC.Core.Geom import Geom_Plane, Geom_BSplineCurve
from OCC.Core.Geom2d import Geom2d_BSplineCurve
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.FairCurve import FairCurve_MinimalVariation
from OCC.Core.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire,
                                     BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_HArray1OfPnt
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


class PhysicalBatten:
    """Physical batten simulation class"""
    
    def __init__(self, length=120.0, width=20.0, thickness=2.0):
        """
        Initialize physical batten parameters
        
        Parameters:
        - length: batten length (mm)
        - width: batten width (mm) 
        - thickness: batten thickness (mm)
        """
        self.length = length
        self.width = width
        self.thickness = thickness
        
        # Physical material properties
        self.young_modulus = 200000.0  # Steel: 200 GPa
        self.poisson_ratio = 0.3
        
        # FairCurve parameters
        self.fair_height = self.calculate_fair_height()
        
    def calculate_fair_height(self):
        """
        Convert physical thickness to FairCurve height parameter
        Based on bending rigidity: EI = E * (b*t^3)/12
        """
        # Moment of inertia for rectangular cross-section
        moment_inertia = (self.width * self.thickness**3) / 12.0
        bending_rigidity = self.young_modulus * moment_inertia
        
        # Normalize to FairCurve scale (empirical scaling)
        fair_height = math.sqrt(bending_rigidity / 1000000.0)
        return max(fair_height, 10.0)  # Minimum value for stability
        
    def create_original_batten(self):
        """Create the original straight batten as a Box"""
        box = BRepPrimAPI_MakeBox(
            gp_Pnt(0, -self.width/2, -self.thickness/2),
            self.length, self.width, self.thickness
        ).Shape()
        return box
        
    def calculate_fair_curve(self, angle1=0.0, angle2=0.0, slope=0.0):
        """
        Calculate FairCurve based on end constraints
        
        Parameters:
        - angle1: angle at start point (radians)
        - angle2: angle at end point (radians) 
        - slope: global slope parameter
        """
        pt1 = gp_Pnt2d(0.0, 0.0)
        pt2 = gp_Pnt2d(self.length, 0.0)
        
        # Create FairCurve
        fc = FairCurve_MinimalVariation(pt1, pt2, self.fair_height, slope)
        fc.SetConstraintOrder1(2)  # Position + Tangent + Curvature
        fc.SetConstraintOrder2(2)
        fc.SetAngle1(angle1)
        fc.SetAngle2(angle2)
        fc.SetFreeSliding(True)
        
        # Compute the curve
        status = fc.Compute()
        print(f"FairCurve status: {status}")
        
        if fc.Curve() is not None:
            return fc.Curve()
        return None
        
    def curve_2d_to_3d_spine(self, curve_2d, num_sections=20):
        """
        Convert 2D FairCurve to 3D spine curve and create cross-sections
        
        Parameters:
        - curve_2d: 2D B-spline curve from FairCurve
        - num_sections: number of cross-sections along the spine
        """
        if curve_2d is None:
            return None, []
            
        # Create 3D spine points from 2D curve
        spine_points = TColgp_Array1OfPnt(1, num_sections)
        
        u_start = curve_2d.FirstParameter()
        u_end = curve_2d.LastParameter()
        
        for i in range(num_sections):
            u = u_start + (u_end - u_start) * i / (num_sections - 1)
            pt_2d = curve_2d.Value(u)
            
            # Convert 2D point to 3D spine point
            spine_pt = gp_Pnt(pt_2d.X(), 0.0, pt_2d.Y())
            spine_points.SetValue(i + 1, spine_pt)
            
        # Create HArray1 for GeomAPI_Interpolate
        h_spine_points = TColgp_HArray1OfPnt(1, num_sections)
        for i in range(num_sections):
            h_spine_points.SetValue(i + 1, spine_points.Value(i + 1))
        
        # Create spine curve through 3D points
        spine_interp = GeomAPI_Interpolate(h_spine_points, False, 0.01)
        spine_interp.Perform()
        
        if spine_interp.IsDone():
            spine_curve = spine_interp.Curve()
            
            # Create cross-sections perpendicular to spine
            sections = []
            for i in range(num_sections):
                u = spine_curve.FirstParameter() + (spine_curve.LastParameter() - spine_curve.FirstParameter()) * i / (num_sections - 1)
                
                # Get point and tangent on spine
                pt = spine_curve.Value(u)
                tangent_vec = gp_Vec()
                spine_curve.D1(u, pt, tangent_vec)
                
                # Create local coordinate system
                normal = gp_Dir(tangent_vec)
                if abs(normal.Z()) < 0.9:
                    ref_vec = gp_Dir(0, 0, 1)
                else:
                    ref_vec = gp_Dir(1, 0, 0)
                    
                y_dir = normal.Crossed(ref_vec)
                z_dir = normal.Crossed(y_dir)
                
                # Create rectangular cross-section
                width_vec = gp_Vec(y_dir).Multiplied(self.width/2)
                thickness_vec = gp_Vec(z_dir).Multiplied(self.thickness/2)
                
                corner1 = gp_Pnt(pt.X() - width_vec.X() - thickness_vec.X(),
                                pt.Y() - width_vec.Y() - thickness_vec.Y(),
                                pt.Z() - width_vec.Z() - thickness_vec.Z())
                corner2 = gp_Pnt(pt.X() + width_vec.X() - thickness_vec.X(),
                                pt.Y() + width_vec.Y() - thickness_vec.Y(),
                                pt.Z() + width_vec.Z() - thickness_vec.Z())
                corner3 = gp_Pnt(pt.X() + width_vec.X() + thickness_vec.X(),
                                pt.Y() + width_vec.Y() + thickness_vec.Y(),
                                pt.Z() + width_vec.Z() + thickness_vec.Z())
                corner4 = gp_Pnt(pt.X() - width_vec.X() + thickness_vec.X(),
                                pt.Y() - width_vec.Y() + thickness_vec.Y(),
                                pt.Z() - width_vec.Z() + thickness_vec.Z())
                
                # Create wire for cross-section
                edge1 = BRepBuilderAPI_MakeEdge(corner1, corner2).Edge()
                edge2 = BRepBuilderAPI_MakeEdge(corner2, corner3).Edge()
                edge3 = BRepBuilderAPI_MakeEdge(corner3, corner4).Edge()
                edge4 = BRepBuilderAPI_MakeEdge(corner4, corner1).Edge()
                
                wire_builder = BRepBuilderAPI_MakeWire()
                wire_builder.Add(edge1)
                wire_builder.Add(edge2)
                wire_builder.Add(edge3)
                wire_builder.Add(edge4)
                
                if wire_builder.IsDone():
                    sections.append(wire_builder.Wire())
                    
            return spine_curve, sections
            
        return None, []
        
    def create_deformed_batten(self, curve_2d):
        """Create deformed batten using ThroughSections"""
        spine_curve, sections = self.curve_2d_to_3d_spine(curve_2d)
        
        if len(sections) < 2:
            print("Not enough sections for ThroughSections")
            return self.create_original_batten()
            
        # Create solid through sections
        thru_sections = BRepOffsetAPI_ThruSections(True, False)  # solid=True, ruled=False
        
        for section in sections:
            thru_sections.AddWire(section)
            
        thru_sections.Build()
        
        if thru_sections.IsDone():
            return thru_sections.Shape()
        else:
            print("ThroughSections failed")
            return self.create_original_batten()


def demo_physical_batten(event=None):
    """Demo function showing physical batten bending simulation"""
    display.EraseAll()
    
    # Create batten instance
    batten = PhysicalBatten(length=120.0, width=15.0, thickness=3.0)
    
    print(f"Batten properties:")
    print(f"  Dimensions: {batten.length} x {batten.width} x {batten.thickness} mm")
    print(f"  Fair height: {batten.fair_height:.2f}")
    
    # Show original straight batten
    original = batten.create_original_batten()
    display.DisplayShape(original, color='blue', transparency=0.7)
    
    # Animate bending with different angles
    angle_range = np.linspace(-30, 30, 15)  # degrees
    
    for i, angle_deg in enumerate(angle_range):
        angle_rad = math.radians(angle_deg)
        slope = 0.1 + i * 0.02  # gradually increase slope
        
        # Calculate fair curve
        fair_curve = batten.calculate_fair_curve(
            angle1=angle_rad, 
            angle2=-angle_rad * 0.7,  # asymmetric bending
            slope=slope
        )
        
        if fair_curve:
            # Create deformed batten
            deformed = batten.create_deformed_batten(fair_curve)
            
            # Display with color indicating deformation level
            color_intensity = abs(angle_deg) / 30.0
            red_component = int(255 * color_intensity)
            color = f"rgb({red_component}, {100}, {255 - red_component})"
            
            display.EraseAll()
            display.DisplayShape(original, color='lightblue', transparency=0.8)
            display.DisplayShape(deformed, color='red', transparency=0.3)
            
            # Display 2D curve for reference
            pl = Geom_Plane(gp_Pln(gp_Pnt(0, 0, -10), gp_Dir(0, 0, 1)))
            curve_edge = BRepBuilderAPI_MakeEdge(fair_curve, pl).Edge()
            display.DisplayShape(curve_edge, color='green')
            
            print(f"Angle: {angle_deg:.1f}°, Slope: {slope:.3f}")
            time.sleep(0.5)
    
    print("Physical batten simulation completed!")


def demo_material_comparison(event=None):
    """Compare different material thicknesses"""
    display.EraseAll()
    
    thicknesses = [1.0, 2.0, 4.0, 8.0]  # mm
    colors = ['red', 'orange', 'yellow', 'green']
    
    angle = math.radians(20)  # 20 degree bend
    
    for i, thickness in enumerate(thicknesses):
        batten = PhysicalBatten(length=120.0, width=15.0, thickness=thickness)
        
        # Calculate bending with same angle
        fair_curve = batten.calculate_fair_curve(angle1=angle, angle2=-angle*0.5, slope=0.1)
        
        if fair_curve:
            deformed = batten.create_deformed_batten(fair_curve)
            
            # Offset each batten vertically for comparison
            transform = gp_Trsf()
            transform.SetTranslation(gp_Vec(0, 0, i * 20))
            transformed = BRepBuilderAPI_Transform(deformed, transform).Shape()
            
            display.DisplayShape(transformed, color=colors[i], transparency=0.5)
            print(f"Thickness {thickness}mm: Fair height = {batten.fair_height:.2f}")
    
    print("Material comparison completed!")


def exit_demo(event=None):
    """Exit the demo"""
    sys.exit(0)


if __name__ == "__main__":
    add_menu('Physical Batten')
    add_function_to_menu('Physical Batten', demo_physical_batten)
    add_function_to_menu('Physical Batten', demo_material_comparison)
    add_function_to_menu('Physical Batten', exit_demo)
    start_display()