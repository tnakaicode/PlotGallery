# -*- coding: utf-8 -*-
# Copyright 2016 Thomas Paviot (tpaviot@gmail.com)
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

from OCC.Display.SimpleGui import init_display
from OCC.Core.Addons import text_to_brep, register_font, Font_FA_Regular, Font_FA_Undefined

display, start_display, add_menu, add_function_to_menu = init_display()

# resgister font
register_font("./assets/fonts/Respective.ttf")
register_font("./assets/fonts/METROLOX.ttf")

text = """
Japan
"""

# create a basic string
arialbold_brep_string1 = text_to_brep(
    text, "Respective", Font_FA_Regular, 10., True)

arialbold_brep_string2 = text_to_brep(
    text, "METOLOX", Font_FA_Regular, 10., True)

# Then display the string
display.DisplayShape(arialbold_brep_string1)
display.DisplayShape(arialbold_brep_string2)
display.FitAll()

start_display()