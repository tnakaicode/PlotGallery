import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import sys
import time
import os
import glob
import shutil
import datetime
import string
import requests
from optparse import OptionParser
from io import StringIO
from matplotlib import cm


def create_tempdir(flag=1):
    print(datetime.date.today())
    datenm = "{0:%Y%m%d}".format(datetime.date.today())
    dirnum = len(glob.glob("./temp_" + datenm + "*/"))
    if flag == -1 or dirnum == 0:
        tmpdir = "./temp_{}{:03}/".format(datenm, dirnum)
        os.makedirs(tmpdir)
        fp = open(tmpdir + "not_ignore.txt", "w")
        fp.close()
    else:
        tmpdir = "./temp_{}{:03}/".format(datenm, dirnum - 1)
    print(tmpdir)
    return tmpdir


if __name__ == '__main__':
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--flag", dest="flag", default=1, type="int")
    opt, argc = parser.parse_args(argvs)
    print(opt, argc)
    tmpdir = create_tempdir(opt.flag)

    """
    Makes an animation by repeatedly calling a function *func*.

    Parameters
    ----------
    fig : `~matplotlib.figure.Figure`
       The figure object that is used to get draw, resize, and any
       other needed events.

    func : callable
       The function to call at each frame.  The first argument will
       be the next value in *frames*.   Any additional positional
       arguments can be supplied via the *fargs* parameter.

       The required signature is::

          def func(frame, *fargs) -> iterable_of_artists

       If ``blit == True``, *func* must return an iterable of all artists
       that were modified or created. This information is used by the blitting
       algorithm to determine which parts of the figure have to be updated.
       The return value is unused if ``blit == False`` and may be omitted in
       that case.

    frames : iterable, int, generator function, or None, optional
        Source of data to pass *func* and each frame of the animation

        - If an iterable, then simply use the values provided.  If the
          iterable has a length, it will override the *save_count* kwarg.

        - If an integer, then equivalent to passing ``range(frames)``

        - If a generator function, then must have the signature::

             def gen_function() -> obj

        - If *None*, then equivalent to passing ``itertools.count``.

        In all of these cases, the values in *frames* is simply passed through
        to the user-supplied *func* and thus can be of any type.

    init_func : callable, optional
       A function used to draw a clear frame. If not given, the
       results of drawing from the first item in the frames sequence
       will be used. This function will be called once before the
       first frame.

       The required signature is::

          def init_func() -> iterable_of_artists

       If ``blit == True``, *init_func* must return an iterable of artists
       to be re-drawn. This information is used by the blitting
       algorithm to determine which parts of the figure have to be updated.
       The return value is unused if ``blit == False`` and may be omitted in
       that case.

    fargs : tuple or None, optional
       Additional arguments to pass to each call to *func*.

    save_count : int, optional
       The number of values from *frames* to cache.

    interval : number, optional
       Delay between frames in milliseconds.  Defaults to 200.

    repeat_delay : number, optional
       If the animation in repeated, adds a delay in milliseconds
       before repeating the animation.  Defaults to *None*.

    repeat : bool, optional
       Controls whether the animation should repeat when the sequence
       of frames is completed.  Defaults to *True*.

    blit : bool, optional
       Controls whether blitting is used to optimize drawing. Note: when using
       blitting any animated artists will be drawn according to their zorder.
       However, they will be drawn on top of any previous artists, regardless
       of their zorder.  Defaults to *False*.

    cache_frame_data : bool, optional
       Controls whether frame data is cached. Defaults to *True*.
       Disabling cache might be helpful when frames contain large objects.
    
    def __init__(self, fig, func, frames=None, init_func=None, fargs=None,
                 save_count=None, *, cache_frame_data=True, **kwargs):
    """
