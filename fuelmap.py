from pyqt_trace import pyqt_trace as qtrace
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from maps import s96o2, a10xm, at11


class FuelMap(object):
    """Draw fuel map"""

    def __init__(self, parent=None):
        self.parent = parent
        
    def draw(self):
        self.ui = self.parent.ui
        self.bunlist = self.parent.bunlist
        self.pinobjects = self.parent.pinobjects
        self.enrpinlist = self.parent.enrpinlist

        # Background color
        bg_color = self.parent.config.background_color
        self.ui.fig.set_facecolor(bg_color)
        
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

        # Draw enrichment level pins
        case_num = int(self.ui.case_cbox.currentIndex())
        
        pin_radius = 0.02268
        pin_delta = 0.063495

        x = 1.06  # horizontal position of the circles
        num_levels = len(self.enrpinlist[case_num])
        y0 = 0.5 + (num_levels-1)/2 * pin_delta
        for i in range(num_levels):
            y = y0 - i*pin_delta  # vertical positions
            self.enrpinlist[case_num][i].set_circle(x, y, pin_radius)
            enr = self.enrpinlist[case_num][i].ENR
            self.ui.axes.text(x + 0.05, y, "%.2f" % enr, fontsize=8)
            ba = self.enrpinlist[case_num][i].BA
            if np.isnan(ba) or ba < 0.00001:  # no BA pin
                self.enrpinlist[case_num][i].set_text(str(i+1))
            else:
                self.enrpinlist[case_num][i].set_text('Ba')
                self.ui.axes.text(x + 0.05, y - 0.025, "%.2f" % ba, fontsize=8)
            self.ui.axes.add_patch(self.enrpinlist[case_num][i].circle)
        
        # ----------------------
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
