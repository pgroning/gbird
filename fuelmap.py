from pyqt_trace import pyqt_trace as qtrace
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from map_s96 import s96o2
from map_a10 import a10xm
from map_a11 import at11



class FuelMap(object):
    """Draw fuel map"""

    def __init__(self, parent=None):  # parent = self.ui
        self.parent = parent
        
    def draw(self):
        self.ui = self.parent.ui
        self.bunlist = self.parent.bunlist
        self.pinobjects = self.parent.pinobjects
        self.enrpinlist = self.parent.enrpinlist

        # Background color
        self.ui.fig.set_facecolor("#CFEECF")  # Tea green
        
        # Draw outer rectangle
        rect = mpatches.Rectangle((0.035, 0.035), 0.935, 0.935,
                                  fc=(0.8, 0.898, 1), ec=(0.3, 0.3, 0.3))
        self.ui.axes.add_patch(rect)
        
        # Draw control rods
        rodrect_v = mpatches.Rectangle((0.011, 0.13), 0.045, 0.77,
                                       ec=(0.3, 0.3, 0.3))
        rodrect_v.set_fill(False)
        self.ui.axes.add_patch(rodrect_v)
        pp = [[0.011, 0.17], [0.056, 0.17]]
        poly = mpatches.Polygon(pp)
        poly.set_closed(False)
        self.ui.axes.add_patch(poly)
        pp = [[0.011, 0.86], [0.056, 0.86]]
        poly = mpatches.Polygon(pp)
        poly.set_closed(False)
        self.ui.axes.add_patch(poly)

        rodrect_h = mpatches.Rectangle((0.1, 0.95), 0.77, 0.045,
                                       ec=(0.3, 0.3, 0.3))
        rodrect_h.set_fill(False)
        self.ui.axes.add_patch(rodrect_h)
        pp = [[0.14, 0.95], [0.14, 0.995]]
        poly = mpatches.Polygon(pp)
        poly.set_closed(False)
        self.ui.axes.add_patch(poly)
        pp = [[0.83, 0.95], [0.83, 0.995]]
        poly = mpatches.Polygon(pp)
        poly.set_closed(False)
        self.ui.axes.add_patch(poly)

        # a fancy box with round corners (pad).
        p_fancy = mpatches.FancyBboxPatch((0.12, 0.12), 0.77, 0.77,
                                          boxstyle="round,pad=0.04",
                                          fc=(1, 1, 1),
                                          ec=(0.3, 0.3, 0.3))
        p_fancy.set_linewidth(4.0)
        self.ui.axes.add_patch(p_fancy)
        
        # Draw diagonal symmetry line
        pp = [[0.035, 0.970], [0.970, 0.035]]
        poly = mpatches.Polygon(pp)
        poly.set_linewidth(0.5)
        poly.set_closed(False)
        self.ui.axes.add_patch(poly)

        if self.bunlist[0].data.fuetype == 'OPT2':
            s96o2(self)
        elif self.bunlist[0].data.fuetype == 'OPT3':
            s96o2(self)
        elif self.bunlist[0].data.fuetype == 'A10XM':
            a10xm(self)
        elif self.bunlist[0].data.fuetype == 'A10B':
            a10xm(self)
        elif self.bunlist[0].data.fuetype == 'AT11':
            at11(self)

    def get_colormap(self, npins, colormap="rainbow"):
        if colormap == "rainbow":
            cm = plt.cm.gist_rainbow_r(np.linspace(0, 1, npins))[:,:3]
            cmap = cm.tolist()
        elif colormap == "jet":
            #cm = plt.cm.RdBu_r(np.linspace(0, 1, npins))[:,:3]
            cm = plt.cm.jet(np.linspace(0, 1, npins))[:,:3]
            #cm = plt.cm.Spectral_r(np.linspace(0, 1, npins))[:,:3]
            cmap = cm.tolist()
        elif colormap == "bmr":
            n = npins + 1
            v00 = np.zeros(n)
            v11 = np.ones(n)
            v01 = np.linspace(0, 1, n)
            v10 = v01[::-1]  # revert array
            # blue -> magenta
            cm_bm = np.vstack((v01, v00, v11)).transpose()[:-1]
            # magenta -> red
            cm_mr = np.vstack((v11, v00, v10)).transpose()
            cm = np.vstack((cm_bm, cm_mr))
            ic = np.linspace(0, len(cm) - 1, npins).astype(int).tolist()
            cmap = [cm[i] for i in ic]
        return cmap
