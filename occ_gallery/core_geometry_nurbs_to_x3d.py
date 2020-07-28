# Copyright 2020 Thomas Paviot (tpaviot@gmail.com)
# and Andreas Plesch (gh id @andreasplesch)
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

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface

from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.GeomAbs import GeomAbs_BSplineSurface


# then export to x3d
X3D_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">
<X3D profile='Immersive' version='4.0' xmlns:xsd='http://www.w3.org/2001/XMLSchema-instance' xsd:noNamespaceSchemaLocation='http://www.web3d.org/specifications/x3d-4.0.xsd'>
<head>
    <meta name='generator' content='pythonocc-7.4.1-dev X3D exporter (www.pythonocc.org)'/>
    <meta name='creator' content='pythonocc-7.4.1-dev generator'/>
    <meta name='identifier' content='http://www.pythonocc.org'/>
    <meta name='description' content='pythonocc-7.4.1-dev x3dom based shape rendering'/>
</head>
    <Scene>
    %s
    </Scene>
</X3D>
"""

base_shape = BRepPrimAPI_MakeTorus(3, 1).Shape()

# conversion to a nurbs representation
nurbs_converter = BRepBuilderAPI_NurbsConvert(base_shape, True)
# nurbs_converter.Perform()
converted_shape = nurbs_converter.Shape()

# now, all edges should be BSpline curves and surfaces BSpline surfaces

# https://castle-engine.io/x3d_implementation_nurbs.php#section_homogeneous_coordinates
expl = TopologyExplorer(converted_shape)

nurbs_node_str = ""

face_idx = 1

for face in expl.faces():
    surf = BRepAdaptor_Surface(face, True)
    surf_type = surf.GetType()
    # check each of the is a BSpline surface
    # it should be, since we used the nurbs converter before
    if not surf_type == GeomAbs_BSplineSurface:
        raise AssertionError(
            "the face was not converted to a GeomAbs_BSplineSurface")
    # get the nurbs
    bsrf = surf.BSpline()
    # x3d does not have periodic nurbs
    bsrf.SetUNotPeriodic()
    bsrf.SetVNotPeriodic()
    # bspline surface properties
    # order = degree + 1
    u_order = bsrf.UDegree() + 1
    v_order = bsrf.VDegree() + 1

    nb_u_poles = bsrf.NbUPoles()
    nb_u_knots = bsrf.NbUKnots()

    nb_v_poles = bsrf.NbVPoles()
    nb_v_knots = bsrf.NbVKnots()

    # fill in the x3d template with nurbs information
    nurbs_node_str = "<Shape>"
    nurbs_node_str += "<Appearance>\n<Material diffuseColor='0.760784 0.843137 0.196078' shininess='0.25' specularColor='0.9 0.9 0.9'/></Appearance>\n"
    nurbs_node_str += "<NurbsPatchSurface DEF='nurbs_%i' solid='false' " % face_idx

    if bsrf.IsVClosed():
        nurbs_node_str += "vClosed='true' "
    else:
        nurbs_node_str += "vClosed='false' "
    if bsrf.IsUClosed():
        nurbs_node_str += "uClosed='true' "
    else:
        nurbs_node_str += "uClosed='false' "

    nurbs_node_str += "uDimension='%i' uOrder='%i' " % (nb_u_poles, u_order)
    nurbs_node_str += "vDimension='%i' vOrder='%i' " % (nb_v_poles, v_order)

    # knots vector
    nurbs_node_str += "uKnot='"

    for iu in range(nb_u_knots):
        mu = bsrf.UMultiplicity(iu + 1)  # repeat u knots as necessary
        nurbs_node_str += ("%g " % bsrf.UKnot(iu + 1)) * mu
    nurbs_node_str += "' "

    nurbs_node_str += "vKnot='"
    for iv in range(nb_v_knots):
        mv = bsrf.VMultiplicity(iv + 1)  # repeat v knots as necessary
        nurbs_node_str += ("%g " % bsrf.VKnot(iv + 1)) * mv
    nurbs_node_str += "' "

    # weights can be None
    if bsrf.Weights() is not None:
        nurbs_node_str += "weight='"
        for iw in range(nb_v_poles):
            for jw in range(nb_u_poles):
                nurbs_node_str += "%g " % bsrf.Weight(jw + 1, iw + 1)
        nurbs_node_str += "' "

    nurbs_node_str += "containerField='geometry'>\n"
    # the control points
    nurbs_node_str += "<Coordinate containerField='controlPoint' point='"
    # control points (aka poles), as a 2d array
    if bsrf.Poles() is not None:
        for ip in range(nb_v_poles):
            for jp in range(nb_u_poles):
                p = bsrf.Pole(jp + 1, ip + 1)
                # note: x3d need preweighted control points
                # see https://www.opencascade.com/doc/occt-7.4.0/refman/html/class_b_rep_builder_a_p_i___nurbs_convert.html#details
                w = bsrf.Weight(jp + 1, ip + 1)
                p_x = p.X() * w
                p_y = p.Y() * w
                p_z = p.Z() * w
                nurbs_node_str += "%g %g %g, " % (p_x, p_y, p_z)
        nurbs_node_str += "'/>"

    nurbs_node_str += "</NurbsPatchSurface></Shape>\n"

    face_idx += 1

# write x3d file
fp = open("./core_geometry_nurbs_to_x3d.x3d", "w")
fp.write(X3D_TEMPLATE % nurbs_node_str)
fp.close()
