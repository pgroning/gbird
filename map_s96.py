from pyqt_trace import pyqt_trace as qtrace

import matplotlib.patches as mpatches
import numpy as np

from gbird import cpin


def s96o2(self):
    
    # Draw water cross
    # West
    y0 = 0.004
    pp = [[0.088, y0+0.515], [0.1, y0+0.503], [0.13, y0+0.503],
          [0.15, y0+0.515], [0.32, y0+0.515], [0.34, y0+0.503],
          [0.38, y0+0.503], [0.38, y0+0.497], [0.34, y0+0.497],
          [0.32, y0+0.485], [0.15, y0+0.485], [0.13, y0+0.497],
          [0.1, y0+0.497], [0.088, y0+0.485]]
    poly = mpatches.Polygon(pp)
    poly.set_facecolor((0.8,0.898,1))
    poly.set_linewidth(1.5)
    poly.set_closed(False)
    self.axes.add_patch(poly)
    # East
    pp = [[0.922, y0+0.515], [0.91, y0+0.503], [0.88, y0+0.503],
          [0.86, y0+0.515], [0.69, y0+0.515], [0.67, y0+0.503],
          [0.63, y0+0.503], [0.63, y0+0.497], [0.67, y0+0.497],
          [0.69, y0+0.485], [0.86, y0+0.485], [0.88, y0+0.497],
          [0.91, y0+0.497], [0.922, y0+0.485]]
    poly = mpatches.Polygon(pp)
    poly.set_facecolor((0.8, 0.898, 1))
    poly.set_linewidth(1.5)
    poly.set_closed(False)
    self.axes.add_patch(poly)
    # South
    pp = [[0.485, 0.088], [0.497, 0.1], [0.497, 0.13], [0.485, 0.15],
          [0.485, 0.32], [0.497, 0.34], [0.497, 0.38], [0.503, 0.38],
          [0.503, 0.34], [0.515, 0.32], [0.515, 0.15],[0.503, 0.13],
          [0.503, 0.1],[0.515, 0.088]]
    poly = mpatches.Polygon(pp)
    poly.set_facecolor((0.8, 0.898, 1))
    poly.set_linewidth(1.5)
    poly.set_closed(False)
    self.axes.add_patch(poly)
    # North
    pp = [[0.485, 0.922], [0.497, 0.91], [0.497, 0.88], [0.485, 0.86],
          [0.485, 0.69], [0.497, 0.67], [0.497, 0.63], [0.503, 0.63],
          [0.503,0.67], [0.515, 0.69], [0.515, 0.86], [0.503,0.88],
          [0.503, 0.91], [0.515, 0.922]]
    poly = mpatches.Polygon(pp)
    poly.set_facecolor((0.8, 0.898, 1))
    poly.set_linewidth(1.5)
    poly.set_closed(False)
    self.axes.add_patch(poly)

    # Draw water channel
    # Rectangle center at origo
    y0 = 0.003
    rect = mpatches.Rectangle((-0.095+y0, -0.095+y0), 0.19, 0.19,
                              fc=(0.8, 0.898, 1), ec=(0.3, 0.3, 0.3))
    rect.set_linewidth(2.0)
    # 1. Translate rectangle along x-axis a distance 1/sqrt(2).
    # 2. Rotate 45 degrees
    rot45 = mpatches.transforms.Affine2D().rotate_deg(45) + self.axes.transData
    transrot = mpatches.transforms.Affine2D().translate(0.70711, 0.0) + rot45
    rect.set_transform(transrot)
    self.axes.add_patch(rect)

    # Draw enrichment levels
    case_num = int(self.case_cbox.currentIndex())
    state_num = -1
    
    #pin_radius = 0.028
    #pin_delta = 0.078
    
    pin_radius = 0.02268
    pin_delta = 0.063495

    # Draw enrichment level circles
    x = 1.06  # horizontal position of the circles
    num_levels = len(self.enrpinlist[case_num])
    y0 = 0.5 + (num_levels-1)/2 * pin_delta
    for i in range(num_levels):
        y = y0 - i*pin_delta  # vertical positions
        #y = 0.95 - i*pin_delta  # vertical positions
        self.enrpinlist[case_num][i].set_circle(x, y, pin_radius)
        enr = self.enrpinlist[case_num][i].ENR
        self.axes.text(x + 0.05, y, "%.2f" % enr, fontsize=8)
        ba = self.enrpinlist[case_num][i].BA
        if np.isnan(ba) or ba < 0.00001:  # no BA pin
            self.enrpinlist[case_num][i].set_text(str(i+1))
        else:
            self.enrpinlist[case_num][i].set_text('Ba')
            self.axes.text(x + 0.05, y - 0.025, "%.2f" % ba, fontsize=8)
        self.axes.add_patch(self.enrpinlist[case_num][i].circle)
    
    # Print average enrichment
    #ave_enr = self.bundle.cases[case_num].states[state_num].ave_enr
    #self.axes.text(1.02,0.05,"%.3f %%U-235" % ave_enr,fontsize=8)

    # List of pin coordinates
    self.xlist = ('1','2','3','4','5','6','7','8','9','10')
    self.ylist  = ('A','B','C','D','E','F','G','H','I','J')
    
    # Draw pin circles
    npst = self.bundle.states[0].segments[case_num].data.npst
    #npst = self.bundle.cases[case_num].states[0].npst
    LFU = self.bundle.states[0].segments[case_num].data.LFU
    #LFU = self.bundle.cases[case_num].states[state_num].LFU
    # Remove water cross rows and columns
    LFU = np.delete(LFU, (5), axis=0) # Delete row 6
    LFU = np.delete(LFU, (5), axis=1) # Delete col 6

    pin_radius = 0.028
    pin_delta = 0.078

    k = 0
    for i in range(LFU.shape[0]):
        for j in range(LFU.shape[1]):
            x = 0.13+j*pin_delta
            y = 0.875-i*pin_delta
            if j > 4: x += 0.04
            if i > 4: y -= 0.04
            if LFU[i,j] > 0:
                self.pinobjects[case_num][k].set_circle(x, y, pin_radius,
                                                        (1,1,1))
                self.pinobjects[case_num][k].coord = (self.ylist[i]
                                                      + self.xlist[j])
                self.pinobjects[case_num][k].set_text()
                self.axes.add_patch(self.pinobjects[case_num][k].rectangle)
                self.axes.add_patch(self.pinobjects[case_num][k].circle)
                k += 1
    
    # Draw pin coordinates x-axis
    for i in range(5):
        self.axes.text(0.13 + i*pin_delta, 0.015, self.xlist[i],
                       ha='center',va='center',fontsize=9)
    for i in range(5,10):
        self.axes.text(0.17 + i*pin_delta, 0.015, self.xlist[i],
                       ha='center',va='center',fontsize=9)
        
    # Draw pin coordinates y-axis
    for i in range(5):
        self.axes.text(0.99,0.87-i*pin_delta,self.ylist[i],
                       ha='center',va='center',fontsize=9)
    for i in range(5,10):
        self.axes.text(0.99,0.83-i*pin_delta,self.ylist[i],
                       ha='center',va='center',fontsize=9)
    
