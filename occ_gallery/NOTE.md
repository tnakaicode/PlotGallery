# OCC

## GTransform

<https://www.opencascade.com/doc/occt-7.4.0/refman/html/classgp___g_trsf.html>

Defines a non-persistent transformation in 3D space.
This transformation is a general transformation.
It can be a Trsf from gp, an affinity, or you can define your own transformation giving the matrix of transformation.

With a Gtrsf you can transform only a triplet of coordinates XYZ.
It is not possible to transform other geometric objects because
these transformations can change the nature of non-elementary geometric objects.
The transformation GTrsf can be represented as follow :

V1 V2 V3 T XYZ XYZ | a11 a12 a13 a14 | | x | | x'| | a21 a22 a23 a24 | | y | | y'| | a31 a32 a33 a34 | | z | = | z'| | 0 0 0 1 | | 1 | | 1 |

where {V1, V2, V3} define the vectorial part of the transformation and T defines the translation part of the transformation.
Warning A GTrsf transformation is only applicable to coordinates.
Be careful if you apply such a transformation to all points of a geometric object,
as this can change the nature of the object and thus render it incoherent!
Typically, a circle is transformed into an ellipse by an affinity transformation.
To avoid modifying the nature of an object, use a gp_Trsf transformation instead, as objects of this class respect the nature of geometric objects.

## SimpleGUI

```Python
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
        self.canvas.InitDriver()
        self.resize(size[0], size[1])
        self.canvas.qApp = self.app
        self.display = self.canvas._display

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, backend_str=None, *args):
        used_backend = load_backend(backend_str)
        log.info("GUI backend set to: %s", used_backend)
        from OCC.Display.qtDisplay import qtViewer3d, qtBaseViewer

        # following couple of lines is a tweak to enable ipython --gui='qt'
        # checks if QApplication already exists
        self.app = QtWidgets.QApplication.instance()
        if not self.app:  # create QApplication if it doesnt exist
            self.app = QtWidgets.QApplication(sys.argv)

        QtWidgets.QMainWindow.__init__(self, *args)
        self.canvas = qtViewer3d(self)
        self.setWindowTitle(
            "pythonOCC-%s 3d viewer ('%s' backend)" % (VERSION, used_backend))
        self.setCentralWidget(self.canvas)

class qtBaseViewer(QtOpenGL.QGLWidget):
    ''' The base Qt Widget for an OCC viewer
    '''
    def __init__(self, parent=None):
        super(qtBaseViewer, self).__init__(parent)
        self._display = None
        self._inited = False

class qtViewer3d(qtBaseViewer):
    # emit signal when selection is changed
    # is a list of TopoDS_*
    if HAVE_PYQT_SIGNAL:
        sig_topods_selected = QtCore.pyqtSignal(list)

    def __init__(self, *kargs):
        qtBaseViewer.__init__(self, *kargs)

        self.setObjectName("qt_viewer_3d")

```

## OCC Save PNG

## plt Save GIF

Animation.save

```Python
    def save(self, filename, writer="Pillow", fps=None, dpi=None, codec=None,
             bitrate=None, extra_args=None, metadata=None, extra_anim=None,
             savefig_kwargs=None, *, progress_callback=None):
        # If the writer is None, use the rc param to find the name of the one
        # to use
        if writer is None:
            writer = rcParams['animation.writer']
        elif (not isinstance(writer, str) and
              any(arg is not None
                  for arg in (fps, codec, bitrate, extra_args, metadata))):
            raise RuntimeError('Passing in values for arguments '
                               'fps, codec, bitrate, extra_args, or metadata '
                               'is not supported when writer is an existing '
                               'MovieWriter instance. These should instead be '
                               'passed as arguments when creating the '
                               'MovieWriter instance.')

        if savefig_kwargs is None:
            savefig_kwargs = {}

        # Need to disconnect the first draw callback, since we'll be doing
        # draws. Otherwise, we'll end up starting the animation.
        if self._first_draw_id is not None:
            self._fig.canvas.mpl_disconnect(self._first_draw_id)
            reconnect_first_draw = True
        else:
            reconnect_first_draw = False

        if fps is None and hasattr(self, '_interval'):
            # Convert interval in ms to frames per second
            fps = 1000. / self._interval

        # Re-use the savefig DPI for ours if none is given
        if dpi is None:
            dpi = rcParams['savefig.dpi']
        if dpi == 'figure':
            dpi = self._fig.dpi

        if codec is None:
            codec = rcParams['animation.codec']

        if bitrate is None:
            bitrate = rcParams['animation.bitrate']

        all_anim = [self]
        if extra_anim is not None:
            all_anim.extend(anim for anim in extra_anim if anim._fig is self._fig)

        # If we have the name of a writer,
        # instantiate an instance of the registered class.
        if isinstance(writer, str):
            if writer in writers.avail:
                writer = writers[writer](fps, codec, bitrate, extra_args=extra_args, metadata=metadata)
            else:
                if writers.list():
                    alt_writer = writers[writers.list()[0]]
                    _log.warning("MovieWriter %s unavailable; trying to use "
                                 "%s instead.", writer, alt_writer)
                    writer = alt_writer(
                        fps, codec, bitrate,
                        extra_args=extra_args, metadata=metadata)
                else:
                    raise ValueError("Cannot save animation: no writers are "
                                     "available. Please install ffmpeg to "
                                     "save animations.")
        _log.info('Animation.save using %s', type(writer))

        if 'bbox_inches' in savefig_kwargs:
            _log.warning("Warning: discarding the 'bbox_inches' argument in "
                         "'savefig_kwargs' as it may cause frame size "
                         "to vary, which is inappropriate for animation.")
            savefig_kwargs.pop('bbox_inches')

        # Create a new sequence of frames for saved data.
        # This is different from new_frame_seq() to give the ability
        # to save 'live' generated frame information to be saved later.
        #
        # TODO: Right now, after closing the figure,
        # saving a movie won't work since GUI widgets are gone.
        # Either need to remove extra code to allow for this non-existent use case or find a way to make it work.
        with rc_context():
            if rcParams['savefig.bbox'] == 'tight':
                _log.info("Disabling savefig.bbox = 'tight', as it may cause "
                          "frame size to vary, which is inappropriate for "
                          "animation.")
                rcParams['savefig.bbox'] = None
            with writer.saving(self._fig, filename, dpi):
                for anim in all_anim:
                    # Clear the initial frame
                    anim._init_draw()
                frame_number = 0
                # TODO: Currently only FuncAnimation has a save_count
                #       attribute. Can we generalize this to all Animations?
                save_count_list = [getattr(a, 'save_count', None)
                                   for a in all_anim]
                if None in save_count_list:
                    total_frames = None
                else:
                    total_frames = sum(save_count_list)
                for data in zip(*[a.new_saved_frame_seq() for a in all_anim]):
                    for anim, d in zip(all_anim, data):
                        # TODO: See if turning off blit is really necessary
                        anim._draw_next_frame(d, blit=False)
                        if progress_callback is not None:
                            progress_callback(frame_number, total_frames)
                            frame_number += 1
                    writer.grab_frame(**savefig_kwargs)

        # Reconnect signal for first draw if necessary
        if reconnect_first_draw:
            self._first_draw_id = self._fig.canvas.mpl_connect('draw_event',
                                                               self._start)

```
