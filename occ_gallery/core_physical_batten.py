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

from OCC.Core.gp import (
    gp_Pnt2d,
    gp_Pnt,
    gp_Vec,
    gp_Dir,
    gp_Ax2,
    gp_Pln,
    gp_Trsf,
    gp_GTrsf,
)
from OCC.Core.Geom import Geom_Plane, Geom_BSplineCurve
from OCC.Core.Geom2d import Geom2d_BSplineCurve
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.FairCurve import FairCurve_MinimalVariation
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform,
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_HArray1OfPnt
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


class PhysicalBatten:
    """Physical batten simulation class"""

    def __init__(self, length=120.0, width=20.0, thickness=2.0, material="steel"):
        """
        Initialize physical batten parameters

        Parameters:
        - length: batten length (mm)
        - width: batten width (mm)
        - thickness: batten thickness (mm)
        - material: material type ("steel", "aluminum", "wood", "carbon_fiber")
        """
        self.length = length
        self.width = width
        self.thickness = thickness
        self.material = material

        # Physical material properties
        self.young_modulus, self.density = self.get_material_properties(material)
        self.poisson_ratio = 0.3

        # Physical geometry properties
        self.moment_inertia = self.calculate_moment_inertia()
        self.bending_rigidity = self.young_modulus * self.moment_inertia
        self.mass_per_length = self.density * self.width * self.thickness / 1e9  # kg/mm

        # FairCurve parameters
        self.fair_height = self.calculate_fair_height()

    def get_material_properties(self, material):
        """Get material properties (Young's modulus in MPa, density in kg/m³)"""
        materials = {
            "steel": (200000.0, 7850.0),
            "aluminum": (70000.0, 2700.0),
            "wood": (12000.0, 600.0),
            "carbon_fiber": (230000.0, 1600.0),
            "brass": (100000.0, 8500.0),
            "titanium": (110000.0, 4500.0),
        }
        return materials.get(material, materials["steel"])

    def calculate_moment_inertia(self):
        """Calculate moment of inertia for rectangular cross-section"""
        return (self.width * self.thickness**3) / 12.0

    def calculate_fair_height(self):
        """
        Convert physical thickness to FairCurve height parameter
        Based on bending rigidity: EI = E * I
        """
        # Normalize to FairCurve scale (empirical scaling)
        fair_height = math.sqrt(self.bending_rigidity / 1000000.0)
        return max(fair_height, 10.0)  # Minimum value for stability

    def calculate_physical_slope(self, load_type="gravity", applied_load=None):
        """
        Calculate physical slope parameter based on loading conditions
        Uses realistic load scaling and proper physics instead of arbitrary limits

        Parameters:
        - load_type: "gravity", "point_load", "distributed_load", "thermal"
        - applied_load: applied load magnitude (N or N/mm)

        Returns:
        - slope: FairCurve slope parameter
        """
        if load_type == "gravity":
            # Self-weight deflection
            weight_per_length = self.mass_per_length * 9.81  # N/mm
            # Maximum deflection for simply supported beam under uniform load
            max_deflection = (5 * weight_per_length * self.length**4) / (
                384 * self.bending_rigidity
            )
            slope = max_deflection / self.length

        elif load_type == "point_load" and applied_load:
            # Scale load based on beam capacity to avoid unrealistic deformation
            # Critical load for large deflection: Pcrit = π²EI/(4L²)
            critical_load = (math.pi**2 * self.bending_rigidity) / (4 * self.length**2)
            load_ratio = applied_load / critical_load

            if load_ratio < 0.1:  # Linear regime
                max_deflection = (applied_load * self.length**3) / (
                    48 * self.bending_rigidity
                )
            else:  # Nonlinear regime - use modified formula
                linear_deflection = (applied_load * self.length**3) / (
                    48 * self.bending_rigidity
                )
                # Apply nonlinear correction factor
                nonlinear_factor = 1.0 + 0.5 * load_ratio + 0.1 * load_ratio**2
                max_deflection = linear_deflection * nonlinear_factor

            slope = max_deflection / self.length
            print(
                f"  Load ratio: {load_ratio:.3f}, Critical load: {critical_load:.1f}N"
            )

        elif load_type == "distributed_load" and applied_load:
            # Similar approach for distributed load
            critical_load_distributed = (math.pi**4 * self.bending_rigidity) / (
                5 * self.length**4
            )
            load_ratio = applied_load / critical_load_distributed

            if load_ratio < 0.1:  # Linear regime
                max_deflection = (5 * applied_load * self.length**4) / (
                    384 * self.bending_rigidity
                )
            else:  # Nonlinear regime
                linear_deflection = (5 * applied_load * self.length**4) / (
                    384 * self.bending_rigidity
                )
                nonlinear_factor = 1.0 + 0.3 * load_ratio + 0.05 * load_ratio**2
                max_deflection = linear_deflection * nonlinear_factor

            slope = max_deflection / self.length
            print(
                f"  Load ratio: {load_ratio:.3f}, Critical distributed load: {critical_load_distributed:.4f}N/mm"
            )

        elif load_type == "thermal" and applied_load:
            # Thermal expansion/contraction - this is always manageable
            thermal_expansion = 12e-6  # Steel thermal expansion coefficient
            thermal_strain = thermal_expansion * applied_load
            slope = thermal_strain * self.length / 1000.0

        else:
            # Default minimal slope
            slope = 0.001

        # Convert to FairCurve scale with proper physics-based scaling
        # Use deflection-to-span ratio (common engineering metric)
        deflection_span_ratio = slope

        # FairCurve slope should represent curvature, not deflection ratio
        # Use a physics-based conversion: slope ≈ √(deflection_ratio)
        fair_slope = math.sqrt(abs(deflection_span_ratio)) * 0.5  # 0.5 for stability

        return max(fair_slope, 0.001)  # Only minimum limit for numerical stability

    def calculate_natural_frequency(self):
        """Calculate first natural frequency of the batten (Hz)"""
        # First mode natural frequency for simply supported beam
        freq = (math.pi**2 / (2 * self.length**2)) * math.sqrt(
            self.bending_rigidity / self.mass_per_length
        )
        return freq

    def create_original_batten(self):
        """Create the original straight batten as a Box"""
        box = BRepPrimAPI_MakeBox(
            gp_Pnt(0, -self.width / 2, -self.thickness / 2),
            self.length,
            self.width,
            self.thickness,
        ).Shape()
        return box

    def calculate_fair_curve(
        self, angle1=0.0, angle2=0.0, slope=None, load_type="gravity", applied_load=None
    ):
        """
        Calculate FairCurve based on end constraints and physical loading

        Parameters:
        - angle1: angle at start point (radians)
        - angle2: angle at end point (radians)
        - slope: manual slope override, if None uses physical calculation
        - load_type: type of loading for slope calculation
        - applied_load: magnitude of applied load
        """
        pt1 = gp_Pnt2d(0.0, 0.0)
        pt2 = gp_Pnt2d(self.length, 0.0)

        # Calculate physical slope if not provided
        if slope is None:
            slope = self.calculate_physical_slope(load_type, applied_load)

        # Adapt FairCurve height based on deformation regime
        adapted_height = self.fair_height

        # For large deformations, increase height (stiffness) to help convergence
        if slope > 0.1:
            # Large deformation - use nonlinear height scaling
            scale_factor = 1.0 + 2.0 * slope  # Increase stiffness with deformation
            adapted_height = self.fair_height * scale_factor
            print(
                f"  Large deformation detected: height scaled to {adapted_height:.2f}"
            )

        # Create FairCurve with adapted parameters
        fc = FairCurve_MinimalVariation(pt1, pt2, adapted_height, slope)

        # Use adaptive constraint orders based on deformation level
        if slope > 0.05:  # Moderate to large deformation
            fc.SetConstraintOrder1(1)  # Position + Tangent (more flexible)
            fc.SetConstraintOrder2(1)
            constraint_info = "reduced constraints (1st order)"
        else:  # Small deformation
            fc.SetConstraintOrder1(2)  # Position + Tangent + Curvature
            fc.SetConstraintOrder2(2)
            constraint_info = "full constraints (2nd order)"

        fc.SetAngle1(angle1)
        fc.SetAngle2(angle2)
        fc.SetFreeSliding(True)

        # 端点での曲率設定（物理的に意味のある値）
        curvature1 = slope / (self.length * 0.25)  # 入力端曲率
        curvature2 = -slope / (self.length * 0.25)  # 出力端曲率（反対方向）
        fc.SetCurvature1(curvature1)
        fc.SetCurvature2(curvature2)

        # 物理比率設定（材料の柔軟性を表現）
        # 高い値 = より剛い, 低い値 = より柔らかい
        # SetPhysicalRatioは厳しい範囲制限があるため、より安全な範囲を使用
        physical_ratio = self.bending_rigidity / 10000000.0  # より小さなスケール
        physical_ratio = max(0.01, min(physical_ratio, 1.0))  # 安全な範囲に制限

        fc.SetPhysicalRatio(physical_ratio)

        # 滑動係数設定（変形の滑らかさ）
        sliding_factor = 1.0 + slope  # 変形量に応じて調整
        sliding_factor = max(0.5, min(sliding_factor, 3.0))  # 範囲制限
        fc.SetSlidingFactor(sliding_factor)

        # Compute the curve
        status = fc.Compute()
        print(f"Material: {self.material}, Load: {load_type}")
        print(f"Physical slope: {slope:.4f}, Adapted height: {adapted_height:.2f}")
        print(f"Constraints: {constraint_info}")
        print(f"Curvatures: C1={curvature1:.6f}, C2={curvature2:.6f}")
        print(f"Physical ratio: {physical_ratio:.3f} (剛性比)")
        print(f"Sliding factor: {sliding_factor:.3f} (滑らかさ)")
        print(f"Angles: θ1={math.degrees(angle1):.1f}°, θ2={math.degrees(angle2):.1f}°")
        print(f"FairCurve status: {status}")

        return fc.Curve()

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
                u = spine_curve.FirstParameter() + (
                    spine_curve.LastParameter() - spine_curve.FirstParameter()
                ) * i / (num_sections - 1)

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
                width_vec = gp_Vec(y_dir).Multiplied(self.width / 2)
                thickness_vec = gp_Vec(z_dir).Multiplied(self.thickness / 2)

                corner1 = gp_Pnt(
                    pt.X() - width_vec.X() - thickness_vec.X(),
                    pt.Y() - width_vec.Y() - thickness_vec.Y(),
                    pt.Z() - width_vec.Z() - thickness_vec.Z(),
                )
                corner2 = gp_Pnt(
                    pt.X() + width_vec.X() - thickness_vec.X(),
                    pt.Y() + width_vec.Y() - thickness_vec.Y(),
                    pt.Z() + width_vec.Z() - thickness_vec.Z(),
                )
                corner3 = gp_Pnt(
                    pt.X() + width_vec.X() + thickness_vec.X(),
                    pt.Y() + width_vec.Y() + thickness_vec.Y(),
                    pt.Z() + width_vec.Z() + thickness_vec.Z(),
                )
                corner4 = gp_Pnt(
                    pt.X() - width_vec.X() + thickness_vec.X(),
                    pt.Y() - width_vec.Y() + thickness_vec.Y(),
                    pt.Z() - width_vec.Z() + thickness_vec.Z(),
                )

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
        thru_sections = BRepOffsetAPI_ThruSections(
            True, False
        )  # solid=True, ruled=False

        for section in sections:
            thru_sections.AddWire(section)

        thru_sections.Build()

        if thru_sections.IsDone():
            return thru_sections.Shape()
        else:
            print("ThroughSections failed")
            return self.create_original_batten()


def demo_physical_batten(event=None):
    """Demo function showing physical batten bending simulation with different loadings"""
    display.EraseAll()

    # Create batten instance with specific material
    batten = PhysicalBatten(length=120.0, width=15.0, thickness=3.0, material="steel")

    print(f"Batten properties:")
    print(f"  Material: {batten.material}")
    print(f"  Dimensions: {batten.length} x {batten.width} x {batten.thickness} mm")
    print(f"  Young's modulus: {batten.young_modulus} MPa")
    print(f"  Bending rigidity: {batten.bending_rigidity:.2e} N⋅mm²")
    print(f"  Mass per length: {batten.mass_per_length:.6f} kg/mm")
    print(f"  Natural frequency: {batten.calculate_natural_frequency():.2f} Hz")
    print(f"  Fair height: {batten.fair_height:.2f}")

    # Show original straight batten
    original = batten.create_original_batten()
    display.DisplayShape(original, color="BLUE1", transparency=0.8)

    # Test different loading conditions
    loading_scenarios = [
        ("gravity", None, "Self-weight deflection"),
        ("thermal", 100.0, "100°C temperature rise"),
        ("point_load", 50.0, "50N point load at center"),
        ("distributed_load", 0.5, "0.5 N/mm distributed load"),
    ]

    angle1 = math.radians(10)
    angle2 = math.radians(10)

    colors = ["RED", "GREEN", "YELLOW", "BLACK"]

    for i, (load_type, load_value, description) in enumerate(loading_scenarios):
        print(f"\n--- {description} ---")

        # Calculate fair curve with physical loading
        fair_curve = batten.calculate_fair_curve(
            angle1=angle1, angle2=angle2, load_type=load_type, applied_load=load_value
        )

        if fair_curve:
            # Create deformed batten
            deformed = batten.create_deformed_batten(fair_curve)

            # Offset each scenario for comparison
            transform = gp_Trsf()
            transform.SetTranslation(gp_Vec(0, 0, i * 30))
            transformed = BRepBuilderAPI_Transform(deformed, transform).Shape()

            display.DisplayShape(transformed, color=colors[i], transparency=0.4)

            # Display 2D curve for reference
            pl = Geom_Plane(gp_Pln(gp_Pnt(0, -10, i * 30), gp_Dir(0, 0, 1)))
            curve_edge = BRepBuilderAPI_MakeEdge(fair_curve, pl).Edge()
            display.DisplayShape(curve_edge, color=colors[i])

    display.FitAll()
    print("\nPhysical batten simulation completed!")


def demo_material_comparison(event=None):
    """Compare different materials under same loading"""
    display.EraseAll()

    materials = ["steel", "aluminum", "wood", "carbon_fiber"]
    colors = ["GRAY", "LIGHTBLUE", "BROWN", "BLACK"]

    angle = math.radians(15)
    load_type = "distributed_load"
    applied_load = 1.0  # N/mm

    print("Material comparison under 1.0 N/mm distributed load:")
    print("-" * 60)

    for i, material in enumerate(materials):
        batten = PhysicalBatten(
            length=120.0, width=15.0, thickness=3.0, material=material
        )

        print(f"\n{material.upper()}:")
        print(f"  Young's modulus: {batten.young_modulus} MPa")
        print(f"  Density: {batten.density} kg/m³")
        print(f"  Bending rigidity: {batten.bending_rigidity:.2e} N⋅mm²")
        print(f"  Natural frequency: {batten.calculate_natural_frequency():.2f} Hz")

        # Calculate bending with physical loading
        fair_curve = batten.calculate_fair_curve(
            angle1=angle,
            angle2=-angle * 0.7,
            load_type=load_type,
            applied_load=applied_load,
        )

        if fair_curve:
            deformed = batten.create_deformed_batten(fair_curve)

            # Offset each material vertically for comparison
            transform = gp_Trsf()
            transform.SetTranslation(gp_Vec(0, 0, i * 25))
            transformed = BRepBuilderAPI_Transform(deformed, transform).Shape()

            display.DisplayShape(transformed, color=colors[i], transparency=0.6)

    display.FitAll()
    print("\nMaterial comparison completed!")


def demo_load_analysis(event=None):
    """Analyze different load magnitudes"""
    display.EraseAll()

    batten = PhysicalBatten(
        length=120.0, width=15.0, thickness=2.0, material="aluminum"
    )

    # Test different load magnitudes
    loads = [0.1, 0.5, 1.0, 2.0, 5.0]  # N/mm
    colors = ["LIGHTGREEN", "YELLOW", "ORANGE", "RED", "DARKRED"]

    angle1 = math.radians(5)
    angle2 = math.radians(-5)

    print("Load analysis - Distributed load effect:")
    print("-" * 40)

    for i, load in enumerate(loads):
        print(f"\nLoad: {load} N/mm")

        fair_curve = batten.calculate_fair_curve(
            angle1=angle1,
            angle2=angle2,
            load_type="distributed_load",
            applied_load=load,
        )

        if fair_curve:
            deformed = batten.create_deformed_batten(fair_curve)

            # Offset along X-axis for comparison
            transform = gp_Trsf()
            transform.SetTranslation(gp_Vec(i * 140, 0, 0))
            transformed = BRepBuilderAPI_Transform(deformed, transform).Shape()

            display.DisplayShape(transformed, color=colors[i], transparency=0.5)

    display.FitAll()
    print("\nLoad analysis completed!")


def exit_demo(event=None):
    """Exit the demo"""
    sys.exit(0)


if __name__ == "__main__":
    add_menu("Physical Batten")
    add_function_to_menu("Physical Batten", demo_physical_batten)
    add_function_to_menu("Physical Batten", demo_material_comparison)
    add_function_to_menu("Physical Batten", demo_load_analysis)
    add_function_to_menu("Physical Batten", exit_demo)
    start_display()
