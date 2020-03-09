"""
base from animete_decay.py
"""
import numpy as np
import matplotlib.pyplot as plt
import sys
import time
import os
from matplotlib.animation import FuncAnimation
from optparse import OptionParser


class Aniamte2D (object):
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
        self.ani = FuncAnimation(self.fig, self.run, frames=self.data_gen,
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


if __name__ == '__main__':
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--dir", dest="dir", default=None)
    opt, argc = parser.parse_args(argvs)
    print(opt, argc)

    obj = Aniamte2D()
    obj.ani.save("./animate_base.gif", writer='pillow')
    plt.show()
