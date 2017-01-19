import matplotlib.patches as mpatches
import numpy as np

from gbird import cpin


def a10xm(self):
    
    # Draw water channel
    p_fancy = mpatches.FancyBboxPatch((0.45, 0.365), 0.19, 0.19,
                                          boxstyle="round,pad=0.02",
                                          fc=(0.8,0.898,1), ec=(0.3, 0.3, 0.3))
    p_fancy.set_linewidth(2.0)
    self.axes.add_patch(p_fancy)

    # Draw enrichment levels
    case_num = int(self.case_cbox.currentIndex())
    state_num = -1

    pin_radius = 0.028*0.9
    pin_delta = 0.083*0.85
    
    # Draw enrichment level circles
    x = 1.06  # horizontal position of the circles
    num_levels = len(self.enrpinlist[case_num])
    for i in range(num_levels):
        y = 0.95 - i*pin_delta  # vertical positions
        self.enrpinlist[case_num][i].set_circle(x, y, pin_radius)
        enr = self.enrpinlist[case_num][i].ENR
        self.axes.text(x + 0.05, y, "%.2f" % enr, fontsize=8)
        ba = self.enrpinlist[case_num][i].BA
        if np.isnan(ba) or ba < 0.00001:  # no BA pin
            self.enrpinlist[case_num][i].set_text(str(i+1))
        else:
            self.enrpinlist[case_num][i].set_text('Ba')
            self.axes.text(x + 0.05, y - 0.03, "%.2f" % ba, fontsize=8)
        self.axes.add_patch(self.enrpinlist[case_num][i].circle)
                
    # Print average enrichment
    ave_enr = self.bundle.cases[case_num].states[state_num].ave_enr
    self.axes.text(1.02,0.05,"%.3f %%U-235" % ave_enr,fontsize=8)

    # List of pin coordinates
    self.xlist = ('1','2','3','4','5','6','7','8','9','10')
    self.ylist  = ('A','B','C','D','E','F','G','H','I','J')
    
    # Draw pin circles
    npst = self.bundle.cases[case_num].states[0].npst
    LFU = self.bundle.cases[case_num].states[state_num].LFU
    
    pin_radius = 0.028*1.1
    pin_delta = 0.083

    k = 0
    for i in range(LFU.shape[0]):
        for j in range(LFU.shape[1]):
            x = 0.13+j*pin_delta
            y = 0.875-i*pin_delta
            if LFU[i,j] > 0:
                self.pinobjects[case_num][k].set_circle(x,y,pin_radius,(1,1,1))
                self.pinobjects[case_num][k].coord = (self.ylist[i]
                                                      + self.xlist[j])
                self.pinobjects[case_num][k].set_text()
                self.axes.add_patch(self.pinobjects[case_num][k].circle)
                k += 1

    # Draw pin coordinates x-axis
    for i in range(10):
        self.axes.text(0.13 + i*pin_delta, 0.015, self.xlist[i],
                       ha='center',va='center',fontsize=9)
    
    # Draw pin coordinates y-axis
    for i in range(10):
        self.axes.text(0.99,0.875-i*pin_delta,self.ylist[i],
                       ha='center',va='center',fontsize=9)
