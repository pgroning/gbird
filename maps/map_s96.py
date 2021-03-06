from pyqt_trace import pyqt_trace as qtrace
import matplotlib.patches as mpatches
import numpy as np

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
    self.ui.axes.add_patch(poly)
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
    self.ui.axes.add_patch(poly)
    # South
    x0 = 0.004
    pp = [[x0+0.485, 0.088], [x0+0.497, 0.1], [x0+0.497, 0.13], [x0+0.485, 0.15],
          [x0+0.485, 0.32], [x0+0.497, 0.34], [x0+0.497, 0.38], [x0+0.503, 0.38],
          [x0+0.503, 0.34], [x0+0.515, 0.32], [x0+0.515, 0.15],[x0+0.503, 0.13],
          [x0+0.503, 0.1],[x0+0.515, 0.088]]
    poly = mpatches.Polygon(pp)
    poly.set_facecolor((0.8, 0.898, 1))
    poly.set_linewidth(1.5)
    poly.set_closed(False)
    self.ui.axes.add_patch(poly)
    # North
    pp = [[x0+0.485, 0.922], [x0+0.497, 0.91], [x0+0.497, 0.88], [x0+0.485, 0.86],
          [x0+0.485, 0.69], [x0+0.497, 0.67], [x0+0.497, 0.63], [x0+0.503, 0.63],
          [x0+0.503,0.67], [x0+0.515, 0.69], [x0+0.515, 0.86], [x0+0.503,0.88],
          [x0+0.503, 0.91], [x0+0.515, 0.922]]
    poly = mpatches.Polygon(pp)
    poly.set_facecolor((0.8, 0.898, 1))
    poly.set_linewidth(1.5)
    poly.set_closed(False)
    self.ui.axes.add_patch(poly)

    # Draw water channel
    # Rectangle center at origo
    d = 0.19
    rect = mpatches.Rectangle((-d/2, -d/2), d, d,
                              fc=(0.8, 0.898, 1), ec=(0.3, 0.3, 0.3))
    rect.set_linewidth(2.0)
    # 1. Translate rectangle along x-axis.
    # 2. Rotate 45 degrees
    rot45 = (mpatches.transforms.Affine2D().rotate_deg(45) 
             + self.ui.axes.transData)
    x0 = 0.71261  # 1/sqrt(2) + 0.0055
    transrot = mpatches.transforms.Affine2D().translate(x0, 0.0) + rot45
    rect.set_transform(transrot)

    # List of pin coordinates
    case_num = int(self.ui.case_cbox.currentIndex())
    npst = self.bunlist[0].segments[case_num].data.npst
    xc = [str(i) for i in range(1, npst + 1)]
    yc = [chr(i) for i in range(ord("A"), ord("A") + npst)]
    
    # Draw pin circles
    LFU = self.bunlist[0].segments[case_num].data.LFU
    # Remove water cross rows and columns
    LFU = np.delete(LFU, (5), axis=0) # Delete row 6
    LFU = np.delete(LFU, (5), axis=1) # Delete col 6

    pin_radius = 0.028
    pin_delta = 0.078

    k = 0
    for i in range(LFU.shape[0]):
        for j in range(LFU.shape[1]):
            x = 0.133 + j * pin_delta
            y = 0.875 - i * pin_delta
            if j > 4: x += 0.04
            if i > 4: y -= 0.04
            if LFU[i,j] > 0:
                self.pinobjects[case_num][k].set_circle(x, y, pin_radius,
                                                        (1, 1, 1))
                self.pinobjects[case_num][k].coord = (yc[i] + xc[j])
                self.pinobjects[case_num][k].set_text()
                self.ui.axes.add_patch(self.pinobjects[case_num][k].rectangle)
                self.ui.axes.add_patch(self.pinobjects[case_num][k].circle)
                k += 1

    # Add water channel patch
    self.ui.axes.add_patch(rect)
                
    # Draw pin coordinates x-axis
    for i in range(5):
        self.ui.axes.text(0.13 + i * pin_delta, 0.015, xc[i],
                       ha='center',va='center',fontsize=9)
    for i in range(5,10):
        self.ui.axes.text(0.17 + i * pin_delta, 0.015, xc[i],
                       ha='center',va='center',fontsize=9)
    
    # Draw pin coordinates y-axis
    for i in range(5):
        self.ui.axes.text(0.99, 0.87 - i * pin_delta, yc[i],
                       ha='center', va='center', fontsize=9)
    for i in range(5,10):
        self.ui.axes.text(0.99, 0.83 - i * pin_delta, yc[i],
                       ha='center', va='center', fontsize=9)
    
