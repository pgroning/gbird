import numpy as np

import matplotlib.patches as mpatches
try:  # patheffects not available for older versions of matplotlib
    import matplotlib.patheffects as path_effects
except:
    pass


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
                                            fc=(1, 1, 1), alpha=1.0,
                                            ec=(1, 1, 1))
        self.rectangle.set_fill(True)
        self.rectangle.set_linewidth(0.0)
        
    def set_text(self, string='', fsize=8):
        self.text = self.axes.text(self.x, self.y, string, ha='center',
                                   va='center', fontsize=fsize)

    def is_clicked(self, xc, yc):
        """Check if click is within pin radius"""

        r2 = (xc - self.x)**2 + (yc - self.y)**2
        if r2 < self.circle.get_radius()**2:
            return True
        else:
            return False

    def set_clickpatch(self, edge_color=None):
        r = self.circle.get_radius() * 1.2
        x = self.x
        y = self.y
        
        if edge_color is None:
            alpha = self.rectangle.get_alpha()        
            if alpha > 0.0:
                fc = self.rectangle.get_fc()
                edge_color = (1 - np.array(fc)).tolist()  # complement color
            else:
                edge_color = (0, 0, 0)
        self.clickpatch = mpatches.Circle((x, y), r, fc=(1, 1, 1), alpha=1.0,
                                          ec=edge_color)
        self.clickpatch.set_linestyle('solid')
        self.clickpatch.set_fill(False)
        self.clickpatch.set_linewidth(3.0)
        self.axes.add_patch(self.clickpatch)

    def set_maxpin_patch(self, edge_color=(1, 0, 0)):
        d = self.circle.get_radius() * 2 * 1.25
        x = self.x - d / 2
        y = self.y - d / 2
        self.maxpin_patch = mpatches.Rectangle((x, y), d, d, fc=(1, 1, 1), 
                                               alpha=1.0, ec=edge_color)
        self.maxpin_patch.set_linestyle('solid')
        self.maxpin_patch.set_fill(False)
        self.maxpin_patch.set_linewidth(3.0)
        self.axes.add_patch(self.maxpin_patch)
