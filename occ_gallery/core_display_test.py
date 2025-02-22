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

from lib2to3.pygram import python_grammar_no_print_statement
import logging
import os
import sys
from typing import Any, Callable, List, Optional, Tuple
from unittest import installHandler

from OCC import VERSION
from OCC.Display.backend import load_backend, get_qt_modules
from OCC.Display.OCCViewer import OffscreenRenderer

log = logging.getLogger(__name__)


def check_callable(_callable: Callable) -> None:
    if not callable(_callable):
        raise AssertionError("The function supplied is not callable")


def init_display(
    backend_str: Optional[str] = None,
    size: Optional[Tuple[int, int]] = (1024, 768),
    display_triedron: Optional[bool] = True,
    background_gradient_color1: Optional[List[int]] = [206, 215, 222],
    background_gradient_color2: Optional[List[int]] = [128, 128, 128],
):
    """This function loads and initialize a GUI using either wx, pyq4, pyqt5 or pyside.
    If ever the environment variable PYTHONOCC_OFFSCREEN_RENDERER, then the GUI is simply
    ignored and an offscreen renderer is returned.
    init_display returns 4 objects :
    * display : an instance of Viewer3d ;
    * start_display : a function (the GUI mainloop) ;
    * add_menu : a function that creates a menu in the GUI
    * add_function_to_menu : adds a menu option

    In case an offscreen renderer is returned, start_display and add_menu are ignored, i.e.
    an empty function is returned (named do_nothing). add_function_to_menu just execute the
    function taken as a parameter.

    Note : the offscreen renderer is used on the travis side.
    """
    if size is None:  # prevent size to being None (mypy)
        raise AssertionError("window size cannot be None")

    if os.getenv("PYTHONOCC_OFFSCREEN_RENDERER") == "1":
        # create the offscreen renderer
        offscreen_renderer = OffscreenRenderer()

        def do_nothing(*kargs: Any, **kwargs: Any) -> None:
            """takes as many parameters as you want, and does nothing
            """
            return None

        def call_function(s, func: Callable) -> None:
            """A function that calls another function.
            Helpful to bypass add_function_to_menu. s should be a string
            """
            check_callable(func)
            log.info("Execute %s :: %s menu function" % (s, func.__name__))
            func()
            log.info("done")

        # returns empty classes and functions
        return offscreen_renderer, do_nothing, do_nothing, call_function
    used_backend = load_backend(backend_str)
    # wxPython based simple GUI
    if used_backend == "wx":
        import wx
        from OCC.Display.wxDisplay import wxViewer3d

        print("wxPython backend - ", wx.version())

        class AppFrame(wx.Frame):
            def __init__(self, parent):
                wx.Frame.__init__(
                    self,
                    parent,
                    -1,
                    "pythonOCC-%s 3d viewer ('wx' backend)" % VERSION,
                    style=wx.DEFAULT_FRAME_STYLE,
                    size=size,
                )
                self.canva = wxViewer3d(self)
                self.menuBar = wx.MenuBar()
                self._menus = {}
                self._menu_methods = {}

            def add_menu(self, menu_name: str) -> None:
                _menu = wx.Menu()
                self.menuBar.Append(_menu, "&" + menu_name)
                self.SetMenuBar(self.menuBar)
                self._menus[menu_name] = _menu

            def add_function_to_menu(self, menu_name: str, _callable: Callable) -> None:
                # point on curve
                _id = wx.NewId()
                check_callable(_callable)
                try:
                    self._menus[menu_name].Append(
                        _id, _callable.__name__.replace("_", " ").lower()
                    )
                except KeyError:
                    raise ValueError(
                        "the menu item %s does not exist" % menu_name)
                self.Bind(wx.EVT_MENU, _callable, id=_id)

        app = wx.App(False)
        win = AppFrame(None)
        win.Show(True)
        wx.SafeYield()
        win.canva.InitDriver()
        app.SetTopWindow(win)
        display = win.canva._display

        def add_menu(*args, **kwargs) -> None:
            win.add_menu(*args, **kwargs)

        def add_function_to_menu(*args, **kwargs) -> None:
            win.add_function_to_menu(*args, **kwargs)

        def start_display() -> None:
            app.MainLoop()

    # Qt based simple GUI
    elif "qt" in used_backend:
        from OCC.Display.qtDisplay import qtViewer3d

        QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()
        # check Qt version
        qt_version = None
        if hasattr(QtCore, "QT_VERSION_STR"):  # PyQt5
            qt_version = QtCore.QT_VERSION_STR
        elif hasattr(QtCore, "__version__"):  # PySide2
            qt_version = QtCore.__version__
        print("%s backend - Qt version %s" % (used_backend, qt_version))

        class MainWindow(QtWidgets.QMainWindow):
            def __init__(self, *args: Any) -> None:
                QtWidgets.QMainWindow.__init__(self, *args)
                self.canva = qtViewer3d(self)
                self.setWindowTitle(
                    "pythonOCC-%s 3d viewer ('%s' backend)" % (VERSION,
                                                               used_backend)
                )
                self.setCentralWidget(self.canva)
                if sys.platform != "darwin":
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

            def centerOnScreen(self) -> None:
                """Centers the window on the screen."""
                resolution = QtWidgets.QApplication.desktop().screenGeometry()
                x = (resolution.width() - self.frameSize().width()) // 2
                y = (resolution.height() - self.frameSize().height()) // 2
                self.move(x, y)

            def add_menu(self, menu_name: str) -> None:
                _menu = self.menu_bar.addMenu("&" + menu_name)
                self._menus[menu_name] = _menu

            def add_function_to_menu(self, menu_name: str, _callable: Callable) -> None:
                check_callable(_callable)
                try:
                    _action = QtWidgets.QAction(
                        _callable.__name__.replace("_", " ").lower(), self
                    )
                    # if not, the "exit" action is now shown...
                    _action.setMenuRole(QtWidgets.QAction.NoRole)
                    _action.triggered.connect(_callable)

                    self._menus[menu_name].addAction(_action)
                except KeyError:
                    raise ValueError(
                        "the menu item %s does not exist" % menu_name)

        # following couple of lines is a tweak to enable ipython --gui='qt'
        # checks if QApplication already exists
        app = QtWidgets.QApplication.instance()
        if not app:  # create QApplication if it doesn't exist
            app = QtWidgets.QApplication(sys.argv)
        win = MainWindow()
        win.resize(size[0] - 1, size[1] - 1)
        print(win.canva.winId(), int(win.canva.winId()),
              type(int(win.canva.winId())))
        win.show()
        win.centerOnScreen()
        win.canva.InitDriver()
        win.resize(size[0], size[1])
        win.canva.qApp = app
        display = win.canva._display

        def add_menu(*args, **kwargs) -> None:
            win.add_menu(*args, **kwargs)

        def add_function_to_menu(*args, **kwargs) -> None:
            win.add_function_to_menu(*args, **kwargs)

        def start_display() -> None:
            win.raise_()  # make the application float to the top
            app.exec_()

    if display_triedron:
        display.display_triedron()

    if background_gradient_color1 and background_gradient_color2:
        # background gradient
        display.set_bg_gradient_color(
            background_gradient_color1, background_gradient_color2
        )

    return display, start_display, add_menu, add_function_to_menu, win


display, start_display, add_menu, add_function_to_menu, win = init_display()
win.close()

for i in range(50):
    print(i)
    print()
    display, start_display, add_menu, add_function_to_menu, win = init_display()
    win.close()

# Exception has occurred: OverflowError
# in method 'Display3d_Init', argument 2 of type 'long'

#
# INFO:OCC.Display.backend:The qt-pyqt5 backend is already loaded...``load_backend`` can only be called once per session
# qt-pyqt5 backend - Qt version 5.12.9
# ####### 3D rendering pipe initialisation #####
# Display3d class initialization starting ...
# Aspect_DisplayConnection created.
# OpenGl_GraphicDriver created.
# V3d_Viewer created.
# AIS_InteractiveContext created.
# V3d_View created
# <sip.voidptr object at 0x000001FE8684B270> 18446744071814910284 <class 'int'>

#
# 9223372036854775807  : long int
# 18446744073709551615 : unsigned long int
# 18446744071814910284

#
# OCC > Display > qtDisplay.py > qtViewer3d > InitDriver
# self._display.Create(window_handle=int(self.winId()), parent=self)
# ->
# self._display.Create(window_handle=None, parent=self)

# init_displayのInitDriverが落ちてしまう
# 
# init_displayを少し書き換えて、win=MainWindowを返すようにして使っています。(https://github.com/tnakaicode/PlotGallery/blob/master/occ_gallery/core_display_test.py)
# start_displayをしなければ、全体の処理を止めずにいられるからです。
# 
# win.close()とinit_displayを1つの処理内で、複数回起動していると以下のようなエラーが出て停止することがあります。
# 
# ```bash
# Exception has occurred: OverflowError
# in method 'Display3d_Init', argument 2 of type 'long'
# ```
# 
# 原因を調べると、init_display中の、win.canva.InitDriver()を実行する際に、self._display.Create(window_handle=int(self.winId()))でエラーが出てるようです。
# エラーの原因は、引数のwindow_handle=int(self.winId())の部分で、引数の型が"""long int"""であるのに対して、Pythonのintは""""unsigned long int"""であるため、何度もMainWindow(QtWidgets.QMainWindow)を起動するうちに、winId()が"""long int"""の範囲を超えてしまうためだと考えられます。
# 
# 取り敢えずの対処で、OCC > Display > qtDisplay.py > qtViewer3d > InitDriverの最初の行を以下のように書き換えて、処理が停止しないようにしています。
# 
# ```bash
# self._display.Create(window_handle=None, parent=self)
# ```
# 
# 実行に問題はありませんが、他所で問題が発生しないかどうかの検証が出来ていません。
# 上記のエラーの解決策でより良い方法はないでしょうか？
# 
# InitDriver in init_display is down.
# 
# I am using a slightly rewritten init_display to return win(=MainWindow). (https://github.com/tnakaicode/PlotGallery/blob/master/occ_gallery/core_display_test.py)
# I often use not to do start_display because then I can keep the whole process uninterrupted.
# 
# If I invoke """win.close()""" and """init_display""" multiple times within one process, I may get the following error and stop.
# 
# ```bash
# Exception has occurred: OverflowError
# in method 'Display3d_Init', argument 2 of type 'long
# ```
# 
# When I checked the cause of the error, it seems that the error occurs in """self._display.Create(window_handle=int(self.winId()))""" when executing """win.canva.InitDriver()""" in """init_display""".
# 
# ```bash
#     def InitDriver(self):
#         self._display.Create(window_handle=int(self.winId()), parent=self)
#         ...
# ```
# 
# The error is caused by the argument """window_handle=int(self.winId())""", where the type of the argument is required """long int""", while Python's int is """"unsigned long int""", so it repeatedly calls MainWindow( QMainWindow) in multipul times, """winId()""" exceeds the range of """long int""".
# 
# To deal with this for now, rewrite the first line of OCC > Display > qtDisplay.py > qtViewer3d > InitDriver as follows to prevent the process from stopping.
# 
# ```bash
# self._display.Create(window_handle=None, parent=self)
# ```
# 
# There is no problem with execution, but I have not been able to verify that the problem does not occur elsewhere.
# Is there a better solution to the above error?
# 