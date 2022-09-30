# Copyright 2021 Thomas Paviot (tpaviot@gmail.com)
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

from OCC.Core.MeshDS import MeshDS_DataSource
from OCC.Core.RWStl import rwstl_ReadFile
from OCC.Core.MeshVS import MeshVS_Mesh, MeshVS_MeshPrsBuilder, MeshVS_NodalColorPrsBuilder
from OCC.Core.Poly import Poly_Triangulation
from OCC.Extend.DataExchange import read_step_file

from OCC.Display.SimpleGui import init_display

stl_filename = os.path.join("..", "assets", "models", "fan.stl")

a_stl_mesh = rwstl_ReadFile(stl_filename)
a_stp_mesh = read_step_file("./assets/models/as1-oc-214.stp")

a_data_source = MeshDS_DataSource(a_stl_mesh)
# TypeError: Wrong number or type of arguments for overloaded function 'new_MeshDS_DataSource'.
# Possible C/C++ prototypes are:
#    MeshDS_DataSource::MeshDS_DataSource(std::vector< gp_Pnt,std::allocator< gp_Pnt > >,std::vector< std::vector< int,std::allocator< int > >,std::allocator< std::vector< int,std::allocator< int > > > >)
#    MeshDS_DataSource::MeshDS_DataSource(double *,int,int,int *,int,int)
#    MeshDS_DataSource::MeshDS_DataSource(opencascade::handle< Poly_Triangulation > const &)

a_mesh_prs = MeshVS_Mesh()
a_mesh_prs.SetDataSource(a_data_source)
a_builder = MeshVS_MeshPrsBuilder(a_mesh_prs)

a_mesh_prs.AddBuilder(a_builder, True)

# assign nodal builder to the mesh
# Parent  : MeshVS_Mesh
# Flags   : int,optional
# 	default value is MeshVS_DMF_NodalColorDataPrs
# DS      : MeshVS_DataSource,optional
# 	default value is 0
# Id      : int,optional
# 	default value is -1
# Priority: int,optional
# 	default value is MeshVS_BP_NodalColor
a_builder = MeshVS_NodalColorPrsBuilder(a_mesh_prs)
a_builder.UseTexture(True)

display, start_display, add_menu, add_function_to_menu = init_display()

display.Context.Display(a_mesh_prs, True)
display.FitAll()
start_display()
