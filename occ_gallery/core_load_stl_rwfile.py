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

from OCC.Core.RWStl import rwstl_ReadFile

from OCC.Display.SimpleGui import init_display

stl_filename = os.path.join("..", "assets", "models", "fan.stl")

a_stl_mesh = rwstl_ReadFile(stl_filename)

display, start_display, add_menu, add_function_to_menu = init_display()

display.Context.Display(a_stl_mesh, True)
display.FitAll()
start_display()
