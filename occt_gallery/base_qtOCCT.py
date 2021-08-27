# This file is part of pyOCCT which provides Python bindings to the OpenCASCADE
# geometry kernel.
#
# Copyright (C) 2016-2018 Laughlin Research, LLC
# Copyright (C) 2019-2020 Trevor Laughlin and pyOCCT contributors
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

import logging
import os
import sys
from qtpy.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout
log = logging.getLogger(__name__)

from OCCT.Visualization import QtViewer

class init_QDisplay (QMainWindow):

    def __init__(self,
                 backend_str=None,
                 size=(1024, 768),
                 display_triedron=True,
                 background_gradient_color1=[206, 215, 222],
                 background_gradient_color2=[128, 128, 128]):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        QMainWindow.__init__(self, None)
        self.resize(size[0] - 1, size[1] - 1)
        self.show()
        
        self.canvas = QtViewer.QOpenCascadeWidget(self)
        #self.canvas.InitDriver()
        self.resize(size[0], size[1])
        self.canvas.qApp = self.app
        self.display = self

        #if display_triedron:
        #    self.display.display_triedron()

        if background_gradient_color2:
            # background gradient
            self.canvas.set_bg_color(*background_gradient_color2)

    def add_menu(self, *args, **kwargs):
        self._add_menu(*args, **kwargs)

    def add_menu_shortcut(self, menu_name):
        _menu = self.menu_bar.addMenu("&" + menu_name)
        self._menus[menu_name] = _menu

    def add_function(self, *args, **kwargs):
        self._add_function_to_menu(*args, **kwargs)

    def start_display(self):
        # make the application float to the top
        self.raise_()
        self.app.exec_()


if __name__ == '__main__':
    from OCCT.gp import gp_Pnt
    qtGui = init_QDisplay("qt-pyqt5")
    qtGui.canvas.display_
    qtGui.start_display()
