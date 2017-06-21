import matplotlib.patches as mpatches
import numpy as np

def at11(self):
    
    # Draw water channel
    f = 0.88
    p_fancy = mpatches.FancyBboxPatch((0.417, 0.414), 0.177, 0.177,
                                          boxstyle="round,pad=0.02",
                                          fc=(0.8,0.898,1), ec=(0.3, 0.3, 0.3))
    p_fancy.set_linewidth(2.0)

    # List of pin coordinates
    self.xlist = ('1','2','3','4','5','6','7','8','9','10','11')
    self.ylist  = ('A','B','C','D','E','F','G','H','I','J','K')
    
    # Draw pin circles
    case_num = int(self.ui.case_cbox.currentIndex())
    npst = self.bunlist[0].segments[case_num].data.npst
    LFU = self.bunlist[0].segments[case_num].data.LFU
    
    pin_radius = 0.02806
    pin_delta = 0.07425
    
    k = 0
    for i in range(LFU.shape[0]):
        for j in range(LFU.shape[1]):
            x = 0.133 + j * pin_delta
            y = 0.875 - i * pin_delta
            if LFU[i,j] > 0:
                self.pinobjects[case_num][k].set_circle(x,y,pin_radius,(1,1,1))
                self.pinobjects[case_num][k].coord = (self.ylist[i]
                                                      + self.xlist[j])
                self.pinobjects[case_num][k].set_text()
                self.ui.axes.add_patch(self.pinobjects[case_num][k].rectangle)
                self.ui.axes.add_patch(self.pinobjects[case_num][k].circle)
                k += 1
    
    # Add water channel patch
    self.ui.axes.add_patch(p_fancy)
                
    # Draw pin coordinates x-axis
    for i in range(11):
        self.ui.axes.text(0.13 + i * pin_delta, 0.015, self.xlist[i],
                       ha='center',va='center',fontsize=9)
    
    # Draw pin coordinates y-axis
    for i in range(11):
        self.ui.axes.text(0.99, 0.875 - i*pin_delta, self.ylist[i],
                       ha='center',va='center',fontsize=9)

