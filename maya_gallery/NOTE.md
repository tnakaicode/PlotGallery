# Mayavi

```bash
conda install mayavi
pip install mayavi traits traitsui
pip install etsdemo

qt.qpa.plugin: Could not load the Qt platform plugin "windows" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: direct2d, minimal, offscreen, windows.
```

```python
import os
import PyQt5

qt_path= os.path.dirname(PyQt5.__file__)
os.environ['QT_PLUGIN_PATH'] = os.path.join(qt_path, "Qt/plugins")
```
