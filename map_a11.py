from pyqt_trace import pyqt_trace as qtrace
import matplotlib.patches as mpatches
import numpy as np


def at11(self):
    
    # Draw water channel
    f = 0.88
    p_fancy = mpatches.FancyBboxPatch((0.417, 0.414), 0.177, 0.177,
                                          boxstyle="round,pad=0.02",
                                          fc=(0.8,0.898,1), ec=(0.3, 0.3, 0.3))
    p_fancy.set_linewidth(2.0)
    #self.ui.axes.add_patch(p_fancy)

    # Draw enrichment levels
    case_num = int(self.ui.case_cbox.currentIndex())
    state_num = -1

    pin_radius = 0.0252*0.9
    pin_delta = 0.07055*0.9
    
    # Draw enrichment level circles
    x = 1.06  # horizontal position of the circles
    num_levels = len(self.enrpinlist[case_num])
    y0 = 0.5 + (num_levels-1)/2 * pin_delta
    for i in range(num_levels):
        y = y0 - i*pin_delta  # vertical positions
        #y = 0.95 - i*pin_delta  # vertical positions
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
                
    # Print average enrichment
    #ave_enr = self.bundle.cases[case_num].states[state_num].ave_enr
    #self.ui.axes.text(1.02,0.05,"%.3f %%U-235" % ave_enr,fontsize=8)

    # List of pin coordinates
    self.xlist = ('1','2','3','4','5','6','7','8','9','10','11')
    self.ylist  = ('A','B','C','D','E','F','G','H','I','J','K')
    
    # Draw pin circles
    npst = self.bunlist[0].segments[case_num].data.npst
    #npst = self.bundle.cases[case_num].states[0].npst
    LFU = self.bunlist[0].segments[case_num].data.LFU
    #LFU = self.bundle.cases[case_num].states[state_num].LFU
    
    pin_radius = 0.03 * 0.47000/0.5025
    pin_delta = 0.0825 * 0.9
    
    k = 0
    for i in range(LFU.shape[0]):
        for j in range(LFU.shape[1]):
            x = 0.133 + j*pin_delta
            #y = 0.879 - i*pin_delta
            y = 0.875-i*pin_delta
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
        self.ui.axes.text(0.13 + i*pin_delta, 0.015, self.xlist[i],
                       ha='center',va='center',fontsize=9)
    
    # Draw pin coordinates y-axis
    for i in range(11):
        self.ui.axes.text(0.99,0.875-i*pin_delta,self.ylist[i],
                       ha='center',va='center',fontsize=9)

