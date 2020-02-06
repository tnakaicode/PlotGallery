from matplotlib.pyplot import figure, show
import numpy
import types


class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None
        self.xzoom = True
        self.yzoom = True
        self.cidBP = None
        self.cidBR = None
        self.cidBM = None
        self.cidKeyP = None
        self.cidKeyR = None
        self.cidScroll = None

    def zoom_factory(self, ax, base_scale=2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            if(xdata is None):
                return()
            if(ydata is None):
                return()

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            if(self.xzoom):
                ax.set_xlim([xdata - new_width * (1 - relx),
                             xdata + new_width * (relx)])
            if(self.yzoom):
                ax.set_ylim([ydata - new_height * (1 - rely),
                             ydata + new_height * (rely)])
            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()

        def mousewheel_move(event):
            ax = event.inaxes
            ax._pan_start = types.SimpleNamespace(
                lim=ax.viewLim.frozen(),
                trans=ax.transData.frozen(),
                trans_inverse=ax.transData.inverted().frozen(),
                bbox=ax.bbox.frozen(),
                x=event.x,
                y=event.y)
            if event.button == 'up':
                ax.drag_pan(3, event.key, event.x + 10, event.y + 10)
            else:  # event.button == 'down':
                ax.drag_pan(3, event.key, event.x - 10, event.y - 10)
            fig = ax.get_figure()
            fig.canvas.draw_idle()

        def onKeyPress(event):
            if event.key == 'x':
                self.xzoom = True
                self.yzoom = False
            if event.key == 'y':
                self.xzoom = False
                self.yzoom = True

        def onKeyRelease(event):
            self.xzoom = True
            self.yzoom = True

        fig = ax.get_figure()  # get the figure of interest

        self.cidScroll = fig.canvas.mpl_connect(
            'scroll_event', mousewheel_move)
        self.cidKeyP = fig.canvas.mpl_connect('key_press_event', onKeyPress)
        self.cidKeyR = fig.canvas.mpl_connect(
            'key_release_event', onKeyRelease)

        return mousewheel_move

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax:
                return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None:
                return
            if event.inaxes != ax:
                return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()

        fig = ax.get_figure()  # get the figure of interest

        self.cidBP = fig.canvas.mpl_connect('button_press_event', onPress)
        self.cidBR = fig.canvas.mpl_connect('button_release_event', onRelease)
        self.cidBM = fig.canvas.mpl_connect('motion_notify_event', onMotion)
        # attach the call back

        # return the function
        return onMotion


fig = figure()

ax = fig.add_subplot(111, xlim=(0, 1), ylim=(0, 1), autoscale_on=False)

ax.set_title('Scroll to zoom')
x, y, s, c = numpy.random.rand(4, 200)
s *= 200

ax.scatter(x, y, s, c)
scale = 1.1
zp = ZoomPan()
figZoom = zp.zoom_factory(ax, base_scale=scale)
figPan = zp.pan_factory(ax)


show()
