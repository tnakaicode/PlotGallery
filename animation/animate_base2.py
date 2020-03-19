"""
base from animete_decay.py
"""
import numpy as np
import matplotlib.pyplot as plt
import sys
import time
import os
from matplotlib.animation import FuncAnimation, MovieWriterRegistry, Animation
from matplotlib import cbook, rcParams, rcParamsDefault, rc_context
from optparse import OptionParser

writers = MovieWriterRegistry()


class Aniamte2D (FuncAnimation):
    """
    func : callable
       The function to call at each frame.  The first argument will
       be the next value in *frames*.   Any additional positional
       arguments can be supplied via the *fargs* parameter.

       The required signature is::

          def func(frame, *fargs) -> iterable_of_artists

       If ``blit == True``, *func* must return an iterable of all artists
       that were modified or created. 
       This information is used by the blitting algorithm to determine 
       which parts of the figure have to be updated.
       The return value is unused 
       if ``blit == False`` and may be omitted in that case.
    """

    def __init__(self):
        self.fig, self.axs = plt.subplots()
        self.axs.grid()
        self.axs.set_ylim(-1.1, 1.1)
        self.axs.set_xlim(0, 10)

        self.init()
        FuncAnimation.__init__(self, self.fig, self.run, frames=self.data_gen,
                               blit=False, interval=0.1, repeat=False, init_func=self.init)

    def data_gen(self, t=0):
        cnt = 0
        while cnt < 1000:
            cnt += 1
            if cnt % 100 == 0:
                print(cnt)
            t += 0.05
            yield t, np.sin(2 * np.pi * t) * np.exp(-t / 10.)

    def run(self, data):
        # update the data
        t, y = data
        self.xdata.append(t)
        self.ydata.append(y)
        self.zdata.append(y / 2)
        self.line0.set_data(self.xdata, self.ydata)
        self.line1.set_data(self.xdata, self.zdata)
        return

    def init(self):
        self.xdata = []
        self.ydata = []
        self.zdata = []
        self.line0, = self.axs.plot(self.xdata, self.ydata, lw=2)
        self.line1, = self.axs.plot(self.xdata, self.zdata, lw=2)
        return

    def savegif(self, filename, writer=None, fps=None, dpi=None, codec=None,
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
            all_anim.extend(anim
                            for anim
                            in extra_anim if anim._fig is self._fig)

        # If we have the name of a writer, instantiate an instance of the
        # registered class.
        if isinstance(writer, str):
            if writer in writers.avail:
                writer = writers[writer](fps, codec, bitrate,
                                         extra_args=extra_args,
                                         metadata=metadata)
            else:
                if writers.list():
                    alt_writer = writers[writers.list()[0]]
                    writer = alt_writer(
                        fps, codec, bitrate,
                        extra_args=extra_args, metadata=metadata)
                else:
                    raise ValueError("Cannot save animation: no writers are "
                                     "available. Please install ffmpeg to "
                                     "save animations.")

        if 'bbox_inches' in savefig_kwargs:
            savefig_kwargs.pop('bbox_inches')

        # Create a new sequence of frames for saved data. This is different
        # from new_frame_seq() to give the ability to save 'live' generated
        # frame information to be saved later.
        # TODO: Right now, after closing the figure, saving a movie won't work
        # since GUI widgets are gone. Either need to remove extra code to
        # allow for this non-existent use case or find a way to make it work.
        with rc_context():
            if rcParams['savefig.bbox'] == 'tight':
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


if __name__ == '__main__':
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--dir", dest="dir", default=None)
    opt, argc = parser.parse_args(argvs)
    print(opt, argc)

    obj = Aniamte2D()
    obj.savegif("./animate_base.gif", writer='pillow')
    plt.show()
