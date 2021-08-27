# This file is part of pySMESH which provides Python bindings to SMESH.
#
# Copyright (C) 2016-2018 Laughlin Research, LLC
# Copyright (C) 2019-2021 Trevor Laughlin and the pySMESH contributors
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

from OCCT.Exchange import ExchangeBasic
try:
    from OCCT.Visualization.WxViewer import ShapeViewerWx
    from OCCT.Visualization.QtViewer import ShapeViewerQt
except:
    from OCCT.Visualization.WxViewer import ViewerWx as ShapeViewerWx
    from OCCT.Visualization.QtViewer import ViewerQt as ShapeViewerQt

#from OCCT.SMESH import NETGENPlugin_SimpleHypothesis_2D, NETGENPlugin_NETGEN_2D
from OCCT.SMESH import SMESH_Gen, SMESH_Mesh
#from OCCT.SMESH import MeshViewerWx

fn = './models/wingbox.brep'
shape = ExchangeBasic.read_brep(fn)

v = ShapeViewerQt()
v.add(shape)
v.start()

gen = SMESH_Gen()
mesh = gen.CreateMesh(0, True)
assert isinstance(mesh, SMESH_Mesh)

#hyp2d = NETGENPlugin_SimpleHypothesis_2D(0, 0, gen)
#hyp2d.SetAllowQuadrangles(True)
#hyp2d.SetLocalLength(4.0)
#
#alg2d = NETGENPlugin_NETGEN_2D(1, 0, gen)

mesh.ShapeToMesh(shape)
mesh.AddHypothesis(shape, 0)
mesh.AddHypothesis(shape, 1)

print('Computing mesh...')
done = gen.Compute(mesh, mesh.GetShapeToMesh())
assert done
print('done.')

v.add(mesh)
v.start()
