# This file is part of AFEM which provides an engineering toolkit for airframe
# finite element modeling during conceptual design.
#
# Copyright (C) 2016-2018 Laughlin Research, LLC
# Copyright (C) 2019-2020 Trevor Laughlin
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
try:
    from OCCT.BLSURFPlugin import BLSURFPlugin_BLSURF, BLSURFPlugin_Hypothesis

    has_mg = True
except ImportError:
    BLSURFPlugin_BLSURF, BLSURFPlugin_Hypothesis = None, None
    has_mg = False

from OCCT.NETGENPlugin import (NETGENPlugin_Hypothesis_2D,
                               NETGENPlugin_NETGEN_2D,
                               NETGENPlugin_NETGEN_2D_ONLY,
                               NETGENPlugin_SimpleHypothesis_2D,
                               NETGENPlugin_Hypothesis,
                               NETGENPlugin_NETGEN_3D,
                               NETGENPlugin_NETGEN_2D3D)
from OCCT.SMESH import SMESH_Algo, SMESH_Hypothesis
from OCCT.StdMeshers import (StdMeshers_Adaptive1D,
                             StdMeshers_Deflection1D, StdMeshers_LocalLength,
                             StdMeshers_MaxLength,
                             StdMeshers_NumberOfSegments,
                             StdMeshers_QuadrangleParams,
                             StdMeshers_Quadrangle_2D, StdMeshers_Regular_1D,
                             StdMeshers_CompositeSegment_1D,
                             StdMeshers_QuadType)

#from afem.geometry.check import CheckGeom
#from afem.smesh.entities import FaceSide, Node

__all__ = ["Hypothesis", "Algorithm", "Regular1D", "CompositeSide1D",
           "MaxLength1D", "LocalLength1D", "NumberOfSegments1D", "Adaptive1D",
           "Deflection1D",
           "QuadrangleAlgo2D", "QuadrangleHypo2D",
           "NetgenHypothesis", "NetgenAlgo2D", "NetgenAlgoOnly2D",
           "NetgenHypo2D", "NetgenSimple2D", "NetgenAlgo3D", "NetgenAlgo2D3D",
           "MeshGemsAlgo2D", "MeshGemsHypo2D"]
