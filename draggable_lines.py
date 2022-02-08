import matplotlib.pyplot as plt
import matplotlib.lines as lines
from observable import *


class draggable_line:
    def __init__(self, ax, kind, XorY):
        self.ax = ax
        self.c = ax.get_figure().canvas
        self.o = kind
        self.XorY = XorY
        self.updater = Observable()

        if kind == "h":
            y = [XorY, XorY]
            self.line = self.ax.axhline(
                y=y[0], color="r", lw=2, linestyle="-", picker=5
            )

        elif kind == "v":
            x = [XorY, XorY]
            self.line = self.ax.axvline(
                x=x[0], color="r", lw=2, linestyle="-", picker=5
            )

        self.c.draw_idle()
        self.sid = self.c.mpl_connect("pick_event", self.clickonline)
        print(self.sid)

    def clickonline(self, event):
        if event.artist == self.line:
            print("line selected ", event.artist)
            self.follower = self.c.mpl_connect("motion_notify_event", self.followmouse)
            self.releaser = self.c.mpl_connect(
                "button_press_event", self.releaseonclick
            )

    def followmouse(self, event):
        if self.o == "h":
            self.line.set_ydata([event.ydata, event.ydata])
        else:
            self.line.set_xdata([event.xdata, event.xdata])

        self.c.draw_idle()

    def releaseonclick(self, event):
        if self.o == "h":
            self.XorY = self.line.get_ydata()[0]
        else:
            self.XorY = self.line.get_xdata()[0]

        print(self.XorY)
        self.updater.set(self)

        self.c.mpl_disconnect(self.releaser)
        self.c.mpl_disconnect(self.follower)
