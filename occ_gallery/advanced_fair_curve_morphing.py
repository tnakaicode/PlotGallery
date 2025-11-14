#!/usr/bin/env python

"""
Advanced FairCurve Morphing with Variable Cross-Sections
- Creates adaptive cross-sections that change along the FairCurve
- Implements structural optimization principles through shape morphing
- Uses ThruSections for complex variable geometry
- Demonstrates real engineering applications of FairCurve optimization
"""

import math
import time
import sys
import numpy as np

from OCC.Core.gp import (
    gp_Pnt2d,
    gp_Pnt,
    gp_Vec,
    gp_Vec2d,
    gp_Dir,
    gp_Ax1,
    gp_Ax2,
    gp_Ax3,
    gp_Pln,
    gp_Trsf,
    gp_GTrsf,
)
from OCC.Core.Geom import Geom_Plane, Geom_BSplineCurve, Geom_Circle
from OCC.Core.Geom2d import Geom2d_BSplineCurve, Geom2d_Circle
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.GCE2d import GCE2d_MakeCircle
from OCC.Core.FairCurve import FairCurve_MinimalVariation
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform,
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_HArray1OfPnt
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_WIRE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


class MorphingCrossSection:
    """Variable cross-section definition class"""

    def __init__(self, section_type="rectangle", base_params=None):
        """
        Initialize morphing cross-section

        Parameters:
        - section_type: "rectangle", "ellipse", "I_beam", "T_beam", "hollow_rect"
        - base_params: dict with base dimensions
        """
        self.section_type = section_type
        self.base_params = base_params or {}

    def create_section_at_parameter_with_axis(
        self, u, scale_factor=1.0, aspect_ratio=1.0, section_axis=None
    ):
        """
        Create cross-section at parameter u with specific axis orientation
        
        Parameters:
        - u: parameter along curve (0.0 to 1.0)
        - scale_factor: overall size scaling
        - aspect_ratio: width/height ratio modification  
        - section_axis: gp_Ax2 defining position and orientation
        """
        if section_axis is None:
            section_axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
            
        if self.section_type == "rectangle":
            return self._create_morphing_rectangle_with_axis(u, scale_factor, aspect_ratio, section_axis)
        elif self.section_type == "ellipse":
            return self._create_morphing_ellipse_with_axis(u, scale_factor, aspect_ratio, section_axis)
        elif self.section_type == "I_beam":
            return self._create_morphing_i_beam_with_axis(u, scale_factor, aspect_ratio, section_axis)
        else:
            # Default to rectangle
            return self._create_morphing_rectangle_with_axis(u, scale_factor, aspect_ratio, section_axis)
            
    def _create_morphing_rectangle_with_axis(self, u, scale_factor, aspect_ratio, section_axis):
        """Create morphing rectangular cross-section with specific axis"""
        base_width = self.base_params.get("width", 40.0)
        base_height = self.base_params.get("height", 25.0)

        # Less aggressive morphing for visible thickness
        morph_factor = 0.8 + 0.2 * math.sin(math.pi * u)  # 0.8 to 1.0

        width = base_width * scale_factor * morph_factor
        height = base_height * scale_factor * morph_factor * aspect_ratio

        # Ensure minimum size
        width = max(width, 10.0)
        height = max(height, 8.0)

        # Create rectangle points in local coordinates
        local_pts = [
            gp_Pnt(-width / 2, -height / 2, 0),
            gp_Pnt(width / 2, -height / 2, 0),
            gp_Pnt(width / 2, height / 2, 0),
            gp_Pnt(-width / 2, height / 2, 0),
        ]
        
        # Transform to global coordinates using section_axis
        transform = gp_Trsf()
        # Simple translation to section position
        translation = gp_Vec(gp_Pnt(0, 0, 0), section_axis.Location())
        transform.SetTranslation(translation)
        
        # Apply rotation if needed (simplified)
        if not section_axis.Direction().IsEqual(gp_Dir(0, 0, 1), 1e-6):
            axis = gp_Ax1(section_axis.Location(), section_axis.Direction())
            # Calculate rotation angle (simplified for now)
            transform.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 0.0)
        
        global_pts = []
        for pt in local_pts:
            transformed_pt = pt.Transformed(transform)
            global_pts.append(transformed_pt)

        return self._create_wire_from_points(global_pts, 0.0, gp_Pnt(0,0,0))

    def _create_morphing_ellipse_with_axis(self, u, scale_factor, aspect_ratio, section_axis):
        """Create morphing elliptical cross-section with specific axis"""
        base_radius_major = self.base_params.get("radius_major", 25.0)
        base_radius_minor = self.base_params.get("radius_minor", 15.0)

        # Less aggressive eccentricity change
        eccentricity_factor = 0.85 + 0.15 * math.cos(2 * math.pi * u)

        radius_major = base_radius_major * scale_factor * eccentricity_factor
        radius_minor = base_radius_minor * scale_factor * aspect_ratio
        
        # Ensure minimum size
        radius_major = max(radius_major, 8.0)
        radius_minor = max(radius_minor, 6.0)

        # Create ellipse in local coordinates
        n_points = 12
        local_pts = []
        for i in range(n_points):
            theta = 2 * math.pi * i / n_points
            x = radius_major * math.cos(theta)
            y = radius_minor * math.sin(theta)
            local_pts.append(gp_Pnt(x, y, 0))
            
        # Transform to global coordinates - simple translation only
        transform = gp_Trsf()
        translation = gp_Vec(gp_Pnt(0, 0, 0), section_axis.Location())
        transform.SetTranslation(translation)
        
        global_pts = []
        for pt in local_pts:
            transformed_pt = pt.Transformed(transform)
            global_pts.append(transformed_pt)

        return self._create_wire_from_points(global_pts, 0.0, gp_Pnt(0,0,0), closed=True)

    def _create_morphing_i_beam_with_axis(self, u, scale_factor, aspect_ratio, section_axis):
        """Create morphing I-beam cross-section with specific axis"""
        base_width = self.base_params.get("flange_width", 60.0)
        base_height = self.base_params.get("height", 80.0)
        flange_thickness = self.base_params.get("flange_thickness", 12.0)
        web_thickness = self.base_params.get("web_thickness", 8.0)

        # Morphing: variable flange/web ratio for optimization
        optimization_factor = 0.8 + 0.2 * (1 - abs(2 * u - 1))  # Max at center

        width = base_width * scale_factor * optimization_factor
        height = base_height * scale_factor * aspect_ratio
        f_thick = flange_thickness * scale_factor
        w_thick = web_thickness * scale_factor * optimization_factor

        # I-beam outline points in local coordinates
        local_pts = [
            # Bottom flange
            gp_Pnt(-width / 2, -height / 2, 0),
            gp_Pnt(width / 2, -height / 2, 0),
            gp_Pnt(width / 2, -height / 2 + f_thick, 0),
            gp_Pnt(w_thick / 2, -height / 2 + f_thick, 0),
            # Web
            gp_Pnt(w_thick / 2, height / 2 - f_thick, 0),
            gp_Pnt(width / 2, height / 2 - f_thick, 0),
            # Top flange
            gp_Pnt(width / 2, height / 2, 0),
            gp_Pnt(-width / 2, height / 2, 0),
            gp_Pnt(-width / 2, height / 2 - f_thick, 0),
            gp_Pnt(-w_thick / 2, height / 2 - f_thick, 0),
            # Web (other side)
            gp_Pnt(-w_thick / 2, -height / 2 + f_thick, 0),
            gp_Pnt(-width / 2, -height / 2 + f_thick, 0),
        ]
        
        # Transform to global coordinates - simple translation only
        transform = gp_Trsf()
        translation = gp_Vec(gp_Pnt(0, 0, 0), section_axis.Location())
        transform.SetTranslation(translation)
        
        global_pts = []
        for pt in local_pts:
            transformed_pt = pt.Transformed(transform)
            global_pts.append(transformed_pt)

        return self._create_wire_from_points(global_pts, 0.0, gp_Pnt(0,0,0), closed=True)

    def create_section_at_parameter(
        self, u, scale_factor=1.0, aspect_ratio=1.0, rotation_angle=0.0, position=gp_Pnt(0, 0, 0)
    ):
        """
        Create cross-section at parameter u with morphing

        Parameters:
        - u: parameter along curve (0.0 to 1.0)
        - scale_factor: overall size scaling
        - aspect_ratio: width/height ratio modification
        - rotation_angle: rotation around section center
        - position: 3D position of section center
        """

        if self.section_type == "rectangle":
            return self._create_morphing_rectangle(
                u, scale_factor, aspect_ratio, rotation_angle, position
            )
        elif self.section_type == "ellipse":
            return self._create_morphing_ellipse(
                u, scale_factor, aspect_ratio, rotation_angle, position
            )
        elif self.section_type == "I_beam":
            return self._create_morphing_i_beam(
                u, scale_factor, aspect_ratio, rotation_angle, position
            )
        elif self.section_type == "T_beam":
            return self._create_morphing_t_beam(
                u, scale_factor, aspect_ratio, rotation_angle, position
            )
        elif self.section_type == "hollow_rect":
            return self._create_morphing_hollow_rect(
                u, scale_factor, aspect_ratio, rotation_angle, position
            )
        else:
            # Default to rectangle
            return self._create_morphing_rectangle(
                u, scale_factor, aspect_ratio, rotation_angle, position
            )

    def _create_morphing_rectangle(
        self, u, scale_factor, aspect_ratio, rotation_angle, position
    ):
        """Create morphing rectangular cross-section with substantial thickness"""
        base_width = self.base_params.get("width", 40.0)  # Much larger base
        base_height = self.base_params.get("height", 25.0)  # Much larger base

        # Less aggressive morphing for visible thickness
        morph_factor = 0.7 + 0.3 * math.sin(math.pi * u)  # 0.7 to 1.0

        width = base_width * scale_factor * morph_factor
        height = base_height * scale_factor * morph_factor * aspect_ratio

        # Ensure minimum size
        width = max(width, 8.0)
        height = max(height, 5.0)

        # Create rectangle points
        pts = [
            gp_Pnt(-width / 2, -height / 2, 0),
            gp_Pnt(width / 2, -height / 2, 0),
            gp_Pnt(width / 2, height / 2, 0),
            gp_Pnt(-width / 2, height / 2, 0),
        ]

        return self._create_wire_from_points(pts, rotation_angle, position)

    def _create_morphing_ellipse(
        self, u, scale_factor, aspect_ratio, rotation_angle, position
    ):
        """Create morphing elliptical cross-section with substantial size"""
        base_radius_major = self.base_params.get("radius_major", 25.0)  # Larger
        base_radius_minor = self.base_params.get("radius_minor", 15.0)  # Larger

        # Less aggressive eccentricity change
        eccentricity_factor = 0.8 + 0.2 * math.cos(2 * math.pi * u)

        radius_major = base_radius_major * scale_factor * eccentricity_factor
        radius_minor = base_radius_minor * scale_factor * aspect_ratio
        
        # Ensure minimum size
        radius_major = max(radius_major, 6.0)
        radius_minor = max(radius_minor, 4.0)

        # Create ellipse using parametric approach
        n_points = 16  # Reduced for simpler geometry
        pts = []
        for i in range(n_points):
            theta = 2 * math.pi * i / n_points
            x = radius_major * math.cos(theta)
            y = radius_minor * math.sin(theta)
            pts.append(gp_Pnt(x, y, 0))

        return self._create_wire_from_points(pts, rotation_angle, position, closed=True)

    def _create_morphing_i_beam(
        self, u, scale_factor, aspect_ratio, rotation_angle, position
    ):
        """Create morphing I-beam cross-section"""
        base_width = self.base_params.get("flange_width", 30.0)
        base_height = self.base_params.get("height", 40.0)
        flange_thickness = self.base_params.get("flange_thickness", 6.0)
        web_thickness = self.base_params.get("web_thickness", 4.0)

        # Morphing: variable flange/web ratio for optimization
        optimization_factor = 0.6 + 0.4 * (1 - abs(2 * u - 1))  # Max at center

        width = base_width * scale_factor * optimization_factor
        height = base_height * scale_factor * aspect_ratio
        f_thick = flange_thickness * scale_factor
        w_thick = web_thickness * scale_factor * optimization_factor

        # I-beam outline points
        pts = [
            # Bottom flange
            gp_Pnt(-width / 2, -height / 2, 0),
            gp_Pnt(width / 2, -height / 2, 0),
            gp_Pnt(width / 2, -height / 2 + f_thick, 0),
            gp_Pnt(w_thick / 2, -height / 2 + f_thick, 0),
            # Web
            gp_Pnt(w_thick / 2, height / 2 - f_thick, 0),
            gp_Pnt(width / 2, height / 2 - f_thick, 0),
            # Top flange
            gp_Pnt(width / 2, height / 2, 0),
            gp_Pnt(-width / 2, height / 2, 0),
            gp_Pnt(-width / 2, height / 2 - f_thick, 0),
            gp_Pnt(-w_thick / 2, height / 2 - f_thick, 0),
            # Web (other side)
            gp_Pnt(-w_thick / 2, -height / 2 + f_thick, 0),
            gp_Pnt(-width / 2, -height / 2 + f_thick, 0),
        ]

        return self._create_wire_from_points(pts, rotation_angle, position, closed=True)

    def _create_morphing_t_beam(
        self, u, scale_factor, aspect_ratio, rotation_angle, position
    ):
        """Create morphing T-beam cross-section"""
        base_width = self.base_params.get("flange_width", 25.0)
        base_height = self.base_params.get("height", 30.0)
        flange_thickness = self.base_params.get("flange_thickness", 5.0)
        web_thickness = self.base_params.get("web_thickness", 4.0)

        # Morphing for cantilever optimization (thick root, thin tip)
        root_factor = 1.5 - u  # 1.5 at root (u=0), 0.5 at tip (u=1)

        width = base_width * scale_factor * root_factor
        height = base_height * scale_factor * aspect_ratio
        f_thick = flange_thickness * scale_factor
        w_thick = web_thickness * scale_factor * root_factor

        # T-beam outline points
        pts = [
            # Top flange
            gp_Pnt(-width / 2, height / 2, 0),
            gp_Pnt(width / 2, height / 2, 0),
            gp_Pnt(width / 2, height / 2 - f_thick, 0),
            gp_Pnt(w_thick / 2, height / 2 - f_thick, 0),
            # Web
            gp_Pnt(w_thick / 2, -height / 2, 0),
            gp_Pnt(-w_thick / 2, -height / 2, 0),
            gp_Pnt(-w_thick / 2, height / 2 - f_thick, 0),
            gp_Pnt(-width / 2, height / 2 - f_thick, 0),
        ]

        return self._create_wire_from_points(pts, rotation_angle, position, closed=True)

    def _create_morphing_hollow_rect(
        self, u, scale_factor, aspect_ratio, rotation_angle, position
    ):
        """Create morphing hollow rectangular cross-section"""
        outer_width = self.base_params.get("outer_width", 25.0)
        outer_height = self.base_params.get("outer_height", 15.0)
        wall_thickness = self.base_params.get("wall_thickness", 3.0)

        # Morphing: variable wall thickness for weight optimization
        thickness_factor = 0.7 + 0.3 * math.sin(math.pi * u)

        o_width = outer_width * scale_factor
        o_height = outer_height * scale_factor * aspect_ratio
        thickness = wall_thickness * scale_factor * thickness_factor

        i_width = o_width - 2 * thickness
        i_height = o_height - 2 * thickness

        # Ensure reasonable inner dimensions
        if i_width <= 0 or i_height <= 0:
            return self._create_morphing_rectangle(
                u, scale_factor, aspect_ratio, rotation_angle, position
            )

        # Outer rectangle
        outer_pts = [
            gp_Pnt(-o_width / 2, -o_height / 2, 0),
            gp_Pnt(o_width / 2, -o_height / 2, 0),
            gp_Pnt(o_width / 2, o_height / 2, 0),
            gp_Pnt(-o_width / 2, o_height / 2, 0),
        ]

        # Inner rectangle (hole)
        inner_pts = [
            gp_Pnt(-i_width / 2, -i_height / 2, 0),
            gp_Pnt(-i_width / 2, i_height / 2, 0),
            gp_Pnt(i_width / 2, i_height / 2, 0),
            gp_Pnt(i_width / 2, -i_height / 2, 0),
        ]

        # Create outer wire
        outer_wire = self._create_wire_from_points(
            outer_pts, rotation_angle, position, closed=True
        )

        # For simplicity, return only outer wire (inner hole would require BRepAlgoAPI_Cut)
        return outer_wire

    def _create_wire_from_points(self, points, rotation_angle, position, closed=True):
        """Create wire from list of points with transformation"""

        # Apply rotation if specified
        if rotation_angle != 0.0:
            transform = gp_Trsf()
            axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
            transform.SetRotation(axis, rotation_angle)

            rotated_points = []
            for pt in points:
                transformed_pt = pt.Transformed(transform)
                rotated_points.append(transformed_pt)
            points = rotated_points

        # Translate to position
        if position.Distance(gp_Pnt(0, 0, 0)) > 1e-6:
            translation = gp_Vec(gp_Pnt(0, 0, 0), position)
            translated_points = []
            for pt in points:
                translated_pt = pt.Translated(translation)
                translated_points.append(translated_pt)
            points = translated_points

        # Create edges and wire
        edges = []
        for i in range(len(points)):
            if closed:
                next_i = (i + 1) % len(points)
            else:
                next_i = i + 1
                if next_i >= len(points):
                    break

            edge = BRepBuilderAPI_MakeEdge(points[i], points[next_i]).Edge()
            edges.append(edge)

        # Create wire
        wire_builder = BRepBuilderAPI_MakeWire()
        for edge in edges:
            wire_builder.Add(edge)

        if wire_builder.IsDone():
            return wire_builder.Wire()
        else:
            print("Warning: Failed to create wire")
            return None


class AdvancedFairCurveMorphing:
    """Advanced FairCurve with morphing cross-sections"""

    def __init__(self, length=150.0, material="steel"):
        """Initialize advanced morphing system"""
        self.length = length
        self.material = material

        # Material properties (simplified)
        materials = {
            "steel": {"E": 200000.0, "density": 7850.0},
            "aluminum": {"E": 70000.0, "density": 2700.0},
            "titanium": {"E": 110000.0, "density": 4500.0},
            "carbon_fiber": {"E": 230000.0, "density": 1600.0},
        }

        props = materials.get(material, materials["steel"])
        self.young_modulus = props["E"]  # MPa
        self.density = props["density"]  # kg/m³

    def calculate_optimized_fair_curve(self, optimization_type="cantilever_beam"):
        """
        Calculate FairCurve based on structural optimization principles

        Parameters:
        - optimization_type: "cantilever_beam", "simply_supported", "arch_bridge", "turbine_blade"
        """
        pt1 = gp_Pnt2d(0.0, 0.0)
        pt2 = gp_Pnt2d(self.length, 0.0)

        # Optimization-specific parameters
        if optimization_type == "cantilever_beam":
            # Fixed end, free end - classic cantilever
            angle1 = math.radians(0)  # Fixed end - horizontal
            angle2 = math.radians(-15)  # Free end - deflected
            height = 15.0
            slope = 0.025

        elif optimization_type == "simply_supported":
            # Simply supported beam - symmetric
            angle1 = math.radians(5)
            angle2 = math.radians(-5)
            height = 12.0
            slope = 0.015

        elif optimization_type == "arch_bridge":
            # Arch structure - compression optimized
            angle1 = math.radians(30)
            angle2 = math.radians(-30)
            height = 20.0
            slope = 0.040

        elif optimization_type == "turbine_blade":
            # Aerodynamic optimization
            angle1 = math.radians(-5)
            angle2 = math.radians(25)
            height = 10.0
            slope = 0.020

        else:
            # Default
            angle1 = math.radians(0)
            angle2 = math.radians(0)
            height = 10.0
            slope = 0.010

        # Create FairCurve
        fc = FairCurve_MinimalVariation(pt1, pt2, height, slope)
        fc.SetConstraintOrder1(2)
        fc.SetConstraintOrder2(2)
        fc.SetAngle1(angle1)
        fc.SetAngle2(angle2)
        fc.SetFreeSliding(True)

        # Curvature based on optimization type
        if optimization_type == "cantilever_beam":
            fc.SetCurvature1(0.0)  # Fixed end
            fc.SetCurvature2(slope / 20)  # Free end
        elif optimization_type == "arch_bridge":
            fc.SetCurvature1(-slope / 30)  # Compression curvature
            fc.SetCurvature2(-slope / 30)
        else:
            fc.SetCurvature1(slope / 40)
            fc.SetCurvature2(-slope / 40)

        status = fc.Compute()
        curve = fc.Curve()

        print(f"Optimization type: {optimization_type}")
        print(f"Angles: {math.degrees(angle1):.1f}° to {math.degrees(angle2):.1f}°")
        print(f"FairCurve status: {status}")

        return curve

    def create_morphing_sections_along_curve(
        self, curve_2d, section_config, num_sections=25
    ):
        """
        Create morphing cross-sections along the FairCurve with proper orientation

        Parameters:
        - curve_2d: 2D FairCurve
        - section_config: dict with section type and morphing parameters
        - num_sections: number of sections to create
        """
        if curve_2d is None:
            return []

        # Extract section configuration
        section_type = section_config.get("type", "rectangle")
        base_params = section_config.get("params", {})
        morphing_mode = section_config.get("morphing_mode", "structural_optimization")

        # Create morphing cross-section generator
        cross_section = MorphingCrossSection(section_type, base_params)

        sections = []
        u_start = curve_2d.FirstParameter()
        u_end = curve_2d.LastParameter()

        for i in range(num_sections):
            # Parameter along curve
            u_curve = u_start + (u_end - u_start) * i / (num_sections - 1)
            u_normalized = i / (num_sections - 1)  # 0.0 to 1.0

            # Get point and tangent on curve
            pt_2d = curve_2d.Value(u_curve)
            tangent_2d = gp_Vec2d()
            curve_2d.D1(u_curve, pt_2d, tangent_2d)

            # Convert to 3D with proper positioning
            curve_x = pt_2d.X()
            curve_z = pt_2d.Y()  # 2D curve Y becomes 3D Z
            
            # Calculate normal vector (perpendicular to curve tangent in XZ plane)
            if tangent_2d.Magnitude() > 1e-6:
                # Normalize tangent
                tang_x = tangent_2d.X() / tangent_2d.Magnitude()
                tang_z = tangent_2d.Y() / tangent_2d.Magnitude()
                
                # Normal vector perpendicular to tangent in XZ plane
                normal_x = -tang_z  # Rotate 90 degrees
                normal_z = tang_x
                
                # Create local coordinate system at curve point
                curve_point = gp_Pnt(curve_x, 0.0, curve_z)
                
                # Direction vectors for section orientation
                z_dir = gp_Dir(normal_x, 0.0, normal_z)  # Normal to curve
                y_dir = gp_Dir(0.0, 1.0, 0.0)           # Always up
                x_dir = y_dir.Crossed(z_dir)             # Complete right-handed system
                
                # Create transformation for section orientation
                section_axis = gp_Ax2(curve_point, z_dir, x_dir)
            else:
                # Fallback for degenerate tangent
                section_axis = gp_Ax2(gp_Pnt(curve_x, 0.0, curve_z), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))

            # Calculate morphing parameters based on mode
            if morphing_mode == "structural_optimization":
                # Optimize for bending moment distribution
                moment_factor = 1.0 - abs(2 * u_normalized - 1)  # Max at center
                scale_factor = 0.9 + 0.4 * moment_factor
                aspect_ratio = 1.0 + 0.2 * moment_factor

            elif morphing_mode == "cantilever_optimization":
                # Cantilever beam optimization - thick at root, thin at tip
                scale_factor = 1.1 - 0.4 * u_normalized
                aspect_ratio = 1.05 - 0.2 * u_normalized

            elif morphing_mode == "aerodynamic_optimization":
                # Aerodynamic profile optimization
                scale_factor = 0.95 + 0.2 * math.sin(math.pi * u_normalized)
                aspect_ratio = 0.8 + 0.4 * u_normalized

            elif morphing_mode == "thermal_adaptation":
                # Thermal expansion compensation
                thermal_factor = math.cos(math.pi * u_normalized)
                scale_factor = 1.0 + 0.1 * thermal_factor
                aspect_ratio = 1.0 - 0.05 * thermal_factor

            else:
                # Default linear taper
                scale_factor = 1.0 - 0.15 * u_normalized
                aspect_ratio = 1.0

            # Create morphing section with proper orientation
            section_wire = cross_section.create_section_at_parameter_with_axis(
                u_normalized, scale_factor, aspect_ratio, section_axis
            )

            if section_wire is not None:
                sections.append(section_wire)

        print(f"Created {len(sections)} morphing sections with {morphing_mode}")
        return sections

    def create_morphing_solid(self, sections):
        """Create solid through morphing sections using ThruSections with better parameters"""
        if len(sections) < 2:
            print("Need at least 2 sections for ThruSections")
            return None

        try:
            # Create solid through sections with improved settings
            thru_sections = BRepOffsetAPI_ThruSections(True, False)  # solid=True, ruled=False for smoother surfaces
            
            # Set parameters for better quality
            thru_sections.SetSmoothing(True)
            thru_sections.SetParType(1)  # Better parameterization
            thru_sections.SetContinuity(1)  # G1 continuity
            thru_sections.SetMaxDegree(8)  # Higher degree for smoother surface
            
            for section in sections:
                thru_sections.AddWire(section)

            thru_sections.CheckCompatibility(False)  # Allow incompatible sections
            thru_sections.Build()

            if thru_sections.IsDone():
                return thru_sections.Shape()
            else:
                print("ThruSections failed, trying simpler approach")
                # Fallback to simpler ruled surface
                thru_sections_simple = BRepOffsetAPI_ThruSections(True, True)  # solid=True, ruled=True
                for section in sections:
                    thru_sections_simple.AddWire(section)
                thru_sections_simple.Build()
                
                if thru_sections_simple.IsDone():
                    return thru_sections_simple.Shape()
                else:
                    print("Both ThruSections approaches failed")
                    return None
                    
        except Exception as e:
            print(f"ThruSections error: {e}")
            return None


def demo_cantilever_optimization(event=None):
    """Demo: Cantilever beam with I-beam optimization"""

    print("=== Cantilever Beam I-Beam Optimization ===")

    morphing = AdvancedFairCurveMorphing(length=120.0, material="aluminum")

    # Calculate optimized fair curve for cantilever
    curve_2d = morphing.calculate_optimized_fair_curve("cantilever_beam")

    if curve_2d:
        # I-beam section configuration with better dimensions
        section_config = {
            "type": "I_beam",
            "params": {
                "flange_width": 35.0,
                "height": 40.0,
                "flange_thickness": 6.0,
                "web_thickness": 4.0,
            },
            "morphing_mode": "cantilever_optimization",
        }

        # Create morphing sections
        sections = morphing.create_morphing_sections_along_curve(
            curve_2d, section_config, 12
        )

        # Create solid
        solid = morphing.create_morphing_solid(sections)

        if solid:
            display.DisplayShape(solid, transparency=0.2)

            # Display key sections
            for i in [0, len(sections) // 3, 2 * len(sections) // 3, -1]:
                if i < len(sections):
                    display.DisplayShape(sections[i], color="RED")

        # Display the curve
        pl = Geom_Plane(gp_Pln(gp_Pnt(0, -40, 0), gp_Dir(0, 0, 1)))
        curve_edge = BRepBuilderAPI_MakeEdge(curve_2d, pl).Edge()
        display.DisplayShape(curve_edge, color="BLUE1")

    display.FitAll()


def demo_arch_bridge_optimization(event=None):
    """Demo: Arch bridge with hollow rectangular optimization"""

    print("=== Arch Bridge Rectangular Optimization ===")

    morphing = AdvancedFairCurveMorphing(length=160.0, material="steel")

    # Calculate arch bridge curve
    curve_2d = morphing.calculate_optimized_fair_curve("arch_bridge")

    if curve_2d:
        # Rectangular section with much larger dimensions
        section_config = {
            "type": "rectangle",
            "params": {"width": 50.0, "height": 35.0},  # Much larger
            "morphing_mode": "structural_optimization",
        }

        sections = morphing.create_morphing_sections_along_curve(
            curve_2d, section_config, 6
        )
        solid = morphing.create_morphing_solid(sections)

        if solid:
            display.DisplayShape(solid, transparency=0.2)

            # Show sections at key points
            for i in [
                0,
                len(sections) // 4,
                len(sections) // 2,
                3 * len(sections) // 4,
                -1,
            ]:
                if i < len(sections):
                    display.DisplayShape(sections[i], color="YELLOW")

        # Display curve
        pl = Geom_Plane(gp_Pln(gp_Pnt(0, -30, 0), gp_Dir(0, 0, 1)))
        curve_edge = BRepBuilderAPI_MakeEdge(curve_2d, pl).Edge()
        display.DisplayShape(curve_edge, color="BLACK")

    display.FitAll()


def demo_turbine_blade_optimization(event=None):
    """Demo: Turbine blade with elliptical aerodynamic optimization"""
    print("=== Turbine Blade Aerodynamic Optimization ===")

    morphing = AdvancedFairCurveMorphing(length=100.0, material="titanium")

    # Calculate turbine blade curve
    curve_2d = morphing.calculate_optimized_fair_curve("turbine_blade")

    if curve_2d:
        # Elliptical section for aerodynamics with much larger dimensions
        section_config = {
            "type": "ellipse",
            "params": {"radius_major": 40.0, "radius_minor": 20.0},  # Much larger
            "morphing_mode": "aerodynamic_optimization",
        }

        sections = morphing.create_morphing_sections_along_curve(
            curve_2d, section_config, 5
        )
        solid = morphing.create_morphing_solid(sections)

        if solid:
            display.DisplayShape(solid, transparency=0.1)

            # Show key sections
            for i in range(0, len(sections), 4):
                if i < len(sections):
                    display.DisplayShape(sections[i])

        # Display curve
        pl = Geom_Plane(gp_Pln(gp_Pnt(0, -20, 0), gp_Dir(0, 0, 1)))
        curve_edge = BRepBuilderAPI_MakeEdge(curve_2d, pl).Edge()
        display.DisplayShape(curve_edge)

    display.FitAll()


def demo_multi_section_comparison(event=None):
    """Demo: Compare different section types on same curve"""

    print("=== Multi-Section Type Comparison ===")

    morphing = AdvancedFairCurveMorphing(length=100.0, material="carbon_fiber")

    # Base curve
    curve_2d = morphing.calculate_optimized_fair_curve("simply_supported")

    if curve_2d:
        section_types = [
            ("rectangle", {"width": 25.0, "height": 15.0}, "ORANGE"),
            ("ellipse", {"radius_major": 18.0, "radius_minor": 9.0}, "BLUE"),
            (
                "T_beam",
                {
                    "flange_width": 22.0,
                    "height": 18.0,
                    "flange_thickness": 3.5,
                    "web_thickness": 2.5,
                },
                "GREEN",
            ),
        ]

        for i, (section_type, params, color) in enumerate(section_types):
            section_config = {
                "type": section_type,
                "params": params,
                "morphing_mode": "structural_optimization",
            }

            sections = morphing.create_morphing_sections_along_curve(
                curve_2d, section_config, 8
            )
            solid = morphing.create_morphing_solid(sections)

            if solid:
                # Offset each type with larger spacing
                transform = gp_Trsf()
                transform.SetTranslation(gp_Vec(0, i * 80, 0))
                transformed = BRepBuilderAPI_Transform(solid, transform).Shape()

                display.DisplayShape(transformed, color=color, transparency=0.3)

                # Show end sections
                if len(sections) > 2:
                    for j in [0, len(sections) // 2, -1]:
                        if j < len(sections):
                            sect_transform = BRepBuilderAPI_Transform(
                                sections[j], transform
                            ).Shape()
                            display.DisplayShape(sect_transform, color=color)

        # Display base curve
        pl = Geom_Plane(gp_Pln(gp_Pnt(0, -20, 0), gp_Dir(0, 0, 1)))
        curve_edge = BRepBuilderAPI_MakeEdge(curve_2d, pl).Edge()
        display.DisplayShape(curve_edge, color="BLACK")

    display.FitAll()


def demo_thermal_adaptation(event=None):
    """Demo: Thermal expansion adaptive morphing"""
    print("=== Thermal Expansion Adaptive Morphing ===")

    morphing = AdvancedFairCurveMorphing(length=80.0, material="steel")

    # Create curves at different "temperatures"
    temperature_conditions = [
        ("20°C", "simply_supported", "BLUE"),
        ("200°C", "cantilever_beam", "ORANGE"),
        ("500°C", "arch_bridge", "RED"),
    ]

    for i, (temp, opt_type, color) in enumerate(temperature_conditions):
        curve_2d = morphing.calculate_optimized_fair_curve(opt_type)

        if curve_2d:
            section_config = {
                "type": "rectangle",
                "params": {
                    "width": 30.0 + i * 8,   # Much larger thermal expansion
                    "height": 20.0 + i * 6,
                },
                "morphing_mode": "thermal_adaptation",
            }

            sections = morphing.create_morphing_sections_along_curve(
                curve_2d, section_config, 5
            )
            solid = morphing.create_morphing_solid(sections)

            if solid:
                transform = gp_Trsf()
                transform.SetTranslation(gp_Vec(0, 0, i * 60))
                transformed = BRepBuilderAPI_Transform(solid, transform).Shape()

                display.DisplayShape(transformed, color=color, transparency=0.3)

                # Show key sections
                if len(sections) > 4:
                    for j in [0, len(sections) // 2, -1]:
                        sect_transform = BRepBuilderAPI_Transform(
                            sections[j], transform
                        ).Shape()
                        display.DisplayShape(sect_transform, color=color)

                print(f"Generated thermal condition: {temp}")

    display.FitAll()


def demo_simple_clear_display(event=None):    
    print("\n=== FairCurve Beam: Original vs Morphed Comparison ===")
    morphing = AdvancedFairCurveMorphing(length=100.0, material="steel")
    
    # 1. Original uniform beam (reference)
    original_box = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 100.0, 20.0, 10.0).Shape()
    display.DisplayShape(original_box, transparency=0.3)
    print("📦 Original uniform beam (100×20×10)")
    
    # 2. FairCurve optimized beam
    curve_2d = morphing.calculate_optimized_fair_curve("cantilever_beam")
    
    if curve_2d:
        section_config = {
            "type": "rectangle",
            "params": {"width": 40.0, "height": 25.0},  # Much larger
            "morphing_mode": "cantilever_optimization",
        }

        sections = morphing.create_morphing_sections_along_curve(curve_2d, section_config, 5)
        solid = morphing.create_morphing_solid(sections)

        if solid:
            # Offset morphed beam to avoid overlap
            transform = gp_Trsf()
            transform.SetTranslation(gp_Vec(0, 40.0, 0))
            morphed_beam = BRepBuilderAPI_Transform(solid, transform).Shape()
            
            display.DisplayShape(morphed_beam, transparency=0.2)
            print("🔄 FairCurve morphed beam (optimized)")
            
            # Show key cross-sections
            for i, section in enumerate(sections):
                if i in [0, len(sections)//2, -1]:  # Start, middle, end
                    sect_transform = BRepBuilderAPI_Transform(section, transform).Shape()
                    display.DisplayShape(sect_transform, color="RED")

        # Display the FairCurve path
        pl = Geom_Plane(gp_Pln(gp_Pnt(0, 40.0, -15.0), gp_Dir(0, 0, 1)))
        curve_edge = BRepBuilderAPI_MakeEdge(curve_2d, pl).Edge()
        display.DisplayShape(curve_edge, color="BLUE1")
        print("📈 FairCurve optimization path (blue)")

    print("✅ Comparison: Gray=Original, Orange=Optimized")
    display.FitAll()


def exit_demo(event=None):
    """Exit the demo"""
    sys.exit(0)


if __name__ == "__main__":
    add_menu("Advanced FairCurve Morphing")
    demo_arch_bridge_optimization()
    demo_cantilever_optimization()
    demo_multi_section_comparison()
    demo_simple_clear_display()
    demo_thermal_adaptation()
    demo_turbine_blade_optimization()
    start_display()
