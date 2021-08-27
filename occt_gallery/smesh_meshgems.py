# This file is part of pyOCCT which provides Python bindings to the OpenCASCADE
# geometry kernel.
#
# Copyright (C) 2016-2018  Laughlin Research, LLC (info@laughlinresearch.com)
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

import time

from OCCT.SMESH import SMESH_Gen, SMESH_Mesh

from OCCT.TDataStd import TDataStd_Name, TDataStd_AsciiString
from OCCT.TDocStd import TDocStd_Document
from OCCT.TNaming import TNaming_NamedShape
from OCCT.XCAFApp import XCAFApp_Application
from OCCT.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_Color
from OCCT.XmlXCAFDrivers import XmlXCAFDrivers
from OCCT.STEPCAFControl import STEPCAFControl_Reader
from OCCT.STEPCAFControl import STEPCAFControl_Writer
from OCCT.STEPConstruct import STEPConstruct

from OCCT.Exchange import ExchangeBasic
try:
    from OCCT.Visualization.WxViewer import ShapeViewerWx
    from OCCT.Visualization.QtViewer import ShapeViewerQt
except:
    from OCCT.Visualization.WxViewer import ViewerWx as ShapeViewerWx
    from OCCT.Visualization.QtViewer import ViewerQt as ShapeViewerQt

# fn = './models/lhs_wing.brep'
# fn = './models/wingbox.brep'
# fn = './models/fuselage_structure.brep'
fn = './models/wing_body.brep'

shape = ExchangeBasic.read_brep(fn)

gen = SMESH_Gen()

mesh = gen.CreateMesh(0, True)

assert isinstance(mesh, SMESH_Mesh)

mesh.ShapeToMesh(shape)

#mg_hyp = BLSURFPlugin_Hypothesis(0, 0, gen, True)
#mg_alg = BLSURFPlugin_BLSURF(1, 0, gen, True)
#mg_hyp.SetPhySize(4)
#mg_hyp.SetQuadAllowed(True)

mesh.AddHypothesis(mesh.GetShapeToMesh(), 0)
mesh.AddHypothesis(mesh.GetShapeToMesh(), 1)

stp = STEPCAFControl_Writer()
stp.SetNameMode(True)

print('Computing mesh...')
start = time.time()
done = gen.Compute(mesh, mesh.GetShapeToMesh())
print('done in ', time.time() - start, ' seconds.')

v = ShapeViewerQt()
v.add(mesh)
v.start()
