#!/usr/bin/env python

"""
Simple Arch Bridge FairCurve Demo
- Standalone demonstration of arch bridge optimization using FairCurve
- Clean implementation without complex morphing
"""

import math
import sys

from OCC.Core.gp import (
    gp_Pnt2d,
    gp_Pnt,
    gp_Vec,
    gp_Dir,
    gp_Ax1,
    gp_Pln,
    gp_Trsf,
)
from OCC.Core.Geom import Geom_Plane
from OCC.Core.FairCurve import FairCurve_MinimalVariation
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Transform,
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


class SimpleFairCurveDemo:
    """Simple FairCurve demonstration class"""
    
    def __init__(self, length=160.0):
        self.length = length
    
    def calculate_arch_bridge_curve(self):
        """Calculate arch bridge optimized FairCurve"""
        pt1 = gp_Pnt2d(0.0, 0.0)
        pt2 = gp_Pnt2d(self.length, 0.0)
        
        # Arch bridge parameters
        angle1 = math.radians(30)   # Start angle
        angle2 = math.radians(-30)  # End angle
        height = 20.0               # Arch height
        slope = 0.040               # Slope parameter
        
        # Create FairCurve
        fc = FairCurve_MinimalVariation(pt1, pt2, height, slope)
        fc.SetConstraintOrder1(2)
        fc.SetConstraintOrder2(2)
        fc.SetAngle1(angle1)
        fc.SetAngle2(angle2)
        fc.SetFreeSliding(True)
        
        # Compression curvature for arch
        fc.SetCurvature1(-slope / 30)
        fc.SetCurvature2(-slope / 30)
        
        status = fc.Compute()
        curve = fc.Curve()
        
        print(f"Arch Bridge FairCurve")
        print(f"Angles: {math.degrees(angle1):.1f}° to {math.degrees(angle2):.1f}°")
        print(f"FairCurve status: {status}")
        
        return curve
    
    def create_rectangular_sections(self, curve_2d, width=50.0, height=35.0, num_sections=6):
        """Create rectangular cross-sections along the curve"""
        if curve_2d is None:
            return []
        
        sections = []
        u_start = curve_2d.FirstParameter()
        u_end = curve_2d.LastParameter()
        
        for i in range(num_sections):
            # Parameter along curve
            u_curve = u_start + (u_end - u_start) * i / (num_sections - 1)
            u_normalized = i / (num_sections - 1)  # 0.0 to 1.0
            
            # Get point on curve
            pt_2d = curve_2d.Value(u_curve)
            position = gp_Pnt(pt_2d.X(), 0.0, pt_2d.Y())
            
            # Structural optimization: thicker at center
            moment_factor = 1.0 - abs(2 * u_normalized - 1)  # Max at center
            scale_factor = 0.9 + 0.4 * moment_factor
            
            # Calculate section dimensions
            section_width = width * scale_factor
            section_height = height * scale_factor
            
            # Create rectangle points
            pts = [
                gp_Pnt(position.X() - section_width/2, position.Y() - section_height/2, position.Z()),
                gp_Pnt(position.X() + section_width/2, position.Y() - section_height/2, position.Z()),
                gp_Pnt(position.X() + section_width/2, position.Y() + section_height/2, position.Z()),
                gp_Pnt(position.X() - section_width/2, position.Y() + section_height/2, position.Z())
            ]
            
            # Create wire from points
            section_wire = self._create_wire_from_points(pts)
            if section_wire:
                sections.append(section_wire)
        
        print(f"Created {len(sections)} rectangular sections")
        return sections
    
    def _create_wire_from_points(self, points):
        """Create wire from list of points"""
        try:
            edges = []
            for i in range(len(points)):
                next_i = (i + 1) % len(points)
                edge = BRepBuilderAPI_MakeEdge(points[i], points[next_i]).Edge()
                edges.append(edge)
            
            wire_builder = BRepBuilderAPI_MakeWire()
            for edge in edges:
                wire_builder.Add(edge)
            
            if wire_builder.IsDone():
                return wire_builder.Wire()
            else:
                print("Warning: Failed to create wire")
                return None
        except Exception as e:
            print(f"Error creating wire: {e}")
            return None
    
    def create_bridge_solid(self, sections):
        """Create solid through sections"""
        if len(sections) < 2:
            print("Need at least 2 sections for solid")
            return None
        
        try:
            # Simple ruled ThruSections
            thru_sections = BRepOffsetAPI_ThruSections(True, True)  # solid=True, ruled=True
            
            for section in sections:
                thru_sections.AddWire(section)
            
            thru_sections.Build()
            
            if thru_sections.IsDone():
                return thru_sections.Shape()
            else:
                print("ThruSections failed")
                return None
                
        except Exception as e:
            print(f"ThruSections error: {e}")
            return None


def demo_arch_bridge_optimization(event=None):
    """Demo: Arch bridge with rectangular optimization"""
    display.EraseAll()
    
    print("=== Arch Bridge Rectangular Optimization ===")
    
    # Create demo instance
    demo = SimpleFairCurveDemo(length=160.0)
    
    # Calculate arch bridge curve
    curve_2d = demo.calculate_arch_bridge_curve()
    
    if curve_2d:
        # Create rectangular sections
        sections = demo.create_rectangular_sections(
            curve_2d, 
            width=50.0, 
            height=35.0, 
            num_sections=6
        )
        
        # Create solid bridge
        solid = demo.create_bridge_solid(sections)
        
        if solid:
            display.DisplayShape(solid, color="GREEN", transparency=0.2)
            print("✅ Bridge solid created successfully")
            
            # Show key sections
            for i in [0, len(sections)//2, -1]:
                if i < len(sections):
                    display.DisplayShape(sections[i], color="YELLOW")
        else:
            print("❌ Failed to create bridge solid")
            # Show sections individually
            for section in sections:
                display.DisplayShape(section, color="YELLOW")
        
        # Display the FairCurve path
        pl = Geom_Plane(gp_Pln(gp_Pnt(0, -50, 0), gp_Dir(0, 0, 1)))
        curve_edge = BRepBuilderAPI_MakeEdge(curve_2d, pl).Edge()
        display.DisplayShape(curve_edge, color="BLACK")
        print("📈 FairCurve optimization path displayed")
    
    display.FitAll()


def exit_demo(event=None):
    """Exit the demo"""
    sys.exit(0)


if __name__ == "__main__":
    add_menu("Arch Bridge Demo")
    add_function_to_menu("Arch Bridge Demo", demo_arch_bridge_optimization)
    add_function_to_menu("Arch Bridge Demo", exit_demo)
    
    # Run the demo directly
    demo_arch_bridge_optimization()
    
    start_display()