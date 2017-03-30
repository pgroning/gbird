from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt

from PyQt4 import QtGui, QtCore

import matplotlib.patches as mpatches
try:  # patheffects not available for older versions of matplotlib
    import matplotlib.patheffects as path_effects
except:
    pass


#class cpin(object):
class FuePin(object):
    def __init__(self, axes):
        self.axes = axes

    def set_circle(self, x, y, r, c=None):
        self.x = x
        self.y = y
        if c is None:
            c = self.facecolor
        self.circle = mpatches.Circle((x, y), r, fc=c, ec=(0.1, 0.1, 0.1))
        self.circle.set_linestyle('solid')
        self.circle.set_linewidth(2.0)
        try:
            self.circle.set_path_effects([path_effects.
                                          withSimplePatchShadow()])
        except:
            pass

        # Set background rectangle
        d = 2*r + 0.019
        self.rectangle = mpatches.Rectangle((x - d/2, y - d/2), d, d,
                                            fc=(1, 1, 0), alpha=1.0,
                                            ec=(1, 1, 1))
        self.rectangle.set_fill(True)
        self.rectangle.set_linewidth(0.0)
        
    def set_text(self, string='', fsize=8):
        # if hasattr(self,'text'):
        #    self.text.remove()
        self.text = self.axes.text(self.x, self.y, string, ha='center',
                                   va='center', fontsize=fsize)

    def is_clicked(self, xc, yc):
        r2 = (xc - self.x)**2 + (yc - self.y)**2
        # Mouse click is within pin radius ?
        if r2 < self.circle.get_radius()**2:
            return True
        else:
            return False
