#!/usr/bin/env python

# Copyright 2009-2016 Thomas Paviot (tpaviot@gmail.com)
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

import logging
import os
import sys
from PyQt5 import QtCore, QtGui, QtOpenGL, QtWidgets
log = logging.getLogger(__name__)

from OCC import VERSION
from OCC.Display.backend import load_backend, get_qt_modules
from OCC.Display.OCCViewer import OffscreenRenderer


def check_callable(_callable):
    if not callable(_callable):
        raise AssertionError("The function supplied is not callable")


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, backend_str=None, *args):
        used_backend = load_backend(backend_str)
        log.info("GUI backend set to: %s", used_backend)
        from OCC.Display.qtDisplay import qtViewer3d

        # following couple of lines is a tweak to enable ipython --gui='qt'
        # checks if QApplication already exists
        self.app = QtWidgets.QApplication.instance()
        if not self.app:  # create QApplication if it doesnt exist
            self.app = QtWidgets.QApplication(sys.argv)

        QtWidgets.QMainWindow.__init__(self, *args)
        self.canva = qtViewer3d(self)
        self.setWindowTitle(
            "pythonOCC-%s 3d viewer ('%s' backend)" % (VERSION, used_backend))
        self.setCentralWidget(self.canva)
        if sys.platform != 'darwin':
            self.menu_bar = self.menuBar()
        else:
            # create a parentless menubar
            # see: http://stackoverflow.com/questions/11375176/qmenubar-and-qmenu-doesnt-show-in-mac-os-x?lq=1
            # noticeable is that the menu ( alas ) is created in the
            # topleft of the screen, just
            # next to the apple icon
            # still does ugly things like showing the "Python" menu in
            # bold
            self.menu_bar = QtWidgets.QMenuBar()
        self._menus = {}
        self._menu_methods = {}
        # place the window in the center of the screen, at half the
        # screen size
        self.centerOnScreen()

    def centerOnScreen(self):
        '''Centers the window on the screen.'''
        resolution = QtWidgets.QApplication.desktop().screenGeometry()
        x = (resolution.width() - self.frameSize().width()) / 2
        y = (resolution.height() - self.frameSize().height()) / 2
        self.move(x, y)

    def _add_menu(self, menu_name):
        _menu = self.menu_bar.addMenu("&" + menu_name)
        self._menus[menu_name] = _menu

    def _add_function_to_menu(self, menu_name, _callable):
        check_callable(_callable)
        try:
            _action = QtWidgets.QAction(
                _callable.__name__.replace('_', ' ').lower(), self)
            # if not, the "exit" action is now shown...
            _action.setMenuRole(QtWidgets.QAction.NoRole)
            _action.triggered.connect(_callable)
            self._menus[menu_name].addAction(_action)
        except KeyError:
            raise ValueError('the menu item %s does not exist' % menu_name)


class InitDisplay (MainWindow):

    def __init__(self,
                 backend_str=None,
                 size=(1024, 768),
                 display_triedron=True,
                 background_gradient_color1=[206, 215, 222],
                 background_gradient_color2=[128, 128, 128]):
        MainWindow.__init__(self, backend_str)

        self.resize(size[0] - 1, size[1] - 1)
        self.show()
        self.centerOnScreen()
        self.canva.InitDriver()
        self.resize(size[0], size[1])
        self.canva.qApp = self.app
        self.display = self.canva._display

        if display_triedron:
            self.display.display_triedron()

        if background_gradient_color1 and background_gradient_color2:
            # background gradient
            self.display.set_bg_gradient_color(
                background_gradient_color1, background_gradient_color2)

    def add_menu(self, *args, **kwargs):
        self._add_menu(*args, **kwargs)

    def add_menu_shortcut(self, menu_name):
        _menu = self.menu_bar.addMenu("&" + menu_name)
        self._menus[menu_name] = _menu

    def add_function_to_menu(self, *args, **kwargs):
        self._add_function_to_menu(*args, **kwargs)

    def start_display(self):
        self.raise_()  # make the application float to the top
        self.app.exec_()


if __name__ == '__main__':
    qtGui = InitDisplay("qt-pyqt5")
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox

    def sphere(event=None):
        qtGui.display.DisplayShape(
            BRepPrimAPI_MakeSphere(100).Shape(), update=True)

    def cube(event=None):
        qtGui.display.DisplayShape(
            BRepPrimAPI_MakeBox(1, 1, 1).Shape(), update=True)

    def quit(event=None):
        sys.exit()

    qtGui.add_menu('primitives')
    qtGui.add_function_to_menu('primitives', sphere)
    qtGui.add_function_to_menu('primitives', cube)
    qtGui.add_function_to_menu('primitives', quit)
    qtGui.add_menu('primitives-1')
    qtGui.add_function_to_menu('primitives-1', sphere)
    qtGui.add_function_to_menu('primitives-1', cube)
    qtGui.add_function_to_menu('primitives-1', quit)
    qtGui.start_display()
