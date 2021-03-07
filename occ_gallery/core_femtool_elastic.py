#!/usr/bin/env python

# Copyright 2009-2015 Jelle Feringa (jelleferinga@gmail.com)
##
# This file is part of pythonOCC.
##
# pythonOCC is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# pythonOCC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.


import os
import math
import time
import sys

sys.path.append(os.path.join("../"))
from base_occ import dispocc

from OCC.Core.gp import gp_Pnt2d, gp_Pln
from OCC.Core.Geom import Geom_Plane
from OCC.Core.FairCurve import FairCurve_MinimalVariation, FairCurve_Energy, FairCurve_Newton, FairCurve_DistributionOfEnergy
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Display.SimpleGui import init_display


class ElasticCurve (dispocc):

    def __init__(self, touch=True):
        dispocc.__init__(self, touch=touch)

        self.pt1 = gp_Pnt2d(0., 0.)
        self.pt2 = gp_Pnt2d(0., 120.)
        self.height = 100.

    def error_code(self, n):
        errors = {0: "FairCurve_OK",
                  1: "FairCurve_NotConverged",
                  2: "FairCurve_InfiniteSliding",
                  3: "FairCurve_NullHeight",
                  }
        return errors[n]

    def batten_curve(self, slope, angle1, angle2):
        """
        Computes a 2D curve using an algorithm which minimizes tension, sagging, and jerk energy. 
        As in FairCurve_Batten, two reference points are used. 
        
        Unlike that class, FairCurve_MinimalVariation requires curvature settings at the first and second reference points. 
        These are defined by the rays of curvature desired at each point.
        
        Constructs the two contact points P1 and P2 and the geometrical characteristics of the batten (elastic beam). 
        These include the real number values for height of deformation Height, slope value Slope, and kind of energy PhysicalRatio. 
        
        The kinds of energy include:
            Jerk (0)
            Sagging (1). 
            FreeSliding = False
            ConstraintOrder1 = 1
            ConstraintOrder2 = 1
            Angle1 = 0
            Angle2 = 0
            Curvature1 = 0
            Curvature2 = 0
            SlidingFactor = 1 
        
        Note that the default setting for Physical Ration is in FairCurve_Batten Other parameters are initialized as follow :
        Warning If PhysicalRatio equals 1, you cannot impose constraints on curvature. 
        Exceptions NegativeValue if Height is less than or equal to 0. 
        NullValue if the distance between P1 and P2 is less than or equal to the tolerance value for distance in Precision::Confusion: P1.IsEqual(P2, Precision::Confusion()). 
        The function gp_Pnt2d::IsEqual tests to see if this is the case. Definition of the geometricals constraints
        """
        fc = FairCurve_MinimalVariation(self.pt1, self.pt2, self.height, slope)
        fc.SetConstraintOrder1(2)
        fc.SetConstraintOrder2(2)
        fc.SetAngle1(angle1)
        fc.SetAngle2(angle2)
        fc.SetHeight(self.height)
        fc.SetSlope(slope)
        fc.SetFreeSliding(True)
        print(fc.DumpToString())
        status = fc.Compute()
        print(self.error_code(status[0]), self.error_code(status[1]))
        return fc.Curve()

    def faircurve(self, event=None):

        pl = Geom_Plane(gp_Pln())
        for i in range(0, 40):
            # TODO: the parameter slope needs to be visualized
            slope = i / 100.
            bc = self.batten_curve(slope,
                                   math.radians(i), math.radians(-i))
            self.display.EraseAll()
            edge = BRepBuilderAPI_MakeEdge(bc, pl).Edge()
            self.display.DisplayShape(edge, update=True)
            time.sleep(0.21)


def exit(event=None):
    sys.exit(0)


if __name__ == "__main__":
    obj = ElasticCurve()
    obj.add_menu('fair curve')
    obj.add_function('fair curve', obj.faircurve)
    obj.add_function('fair curve', exit)
    obj.start_display()
