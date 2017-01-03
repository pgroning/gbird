import matplotlib.patches as mpatches
from main_gui import cpin
#from main_gui import Circle
import numpy as np

def a10xm(self):
    
    # Draw water channel
    p_fancy = mpatches.FancyBboxPatch((0.45, 0.365),
                                          0.19, 0.19,
                                          boxstyle="round,pad=0.02",
                                          #fc=(0.85,1,1),
                                          fc=(0.8,0.898,1),
                                          ec=(0.3, 0.3, 0.3))
    p_fancy.set_linewidth(2.0)
    self.axes.add_patch(p_fancy)

    # Draw enrichment levels
    case_num = int(self.case_cbox.currentIndex())
    FUE = self.dataobj.cases[case_num].data.FUE
    enr_levels  = FUE[:,2]
    enr_ba = FUE[:,4]
    #print enr_levels, enr_ba
 
    #cmap = ["#6666FF","#B266FF","#66FFFF","#00CC00","#66FF66","#FFFF66","#FFB266","#FF9999","#FF3333","#FF3399"]
    #cmap = [[0,0,1], [0,1,1], [0,1,0], [0.604,0.804,0.196], [1,1,0], [0.933,0.867,0.51], [1,0.549,0], [1,1,1], [1,0,0]]
    #enr_steps = [0.71, 2.5, 3.2, 3.4, 4.0, 4.2, 4.6, 4.9, 0]
    #enr_ba = [3.4, 5.0]

    nc = enr_levels.size
    #nc1 = np.round(nc/2)
    #b1 = np.linspace(1,0.2,nc1)
    #b2 = np.linspace(0,0,nc-nc1)
    #b = np.concatenate((b1,b2),axis=0)
    #b = np.linspace(1,0,nc)

    #r1 = np.linspace(0,0,nc1)
    #r2 = np.linspace(0.2,1,nc-nc1)
    #r = np.concatenate((r1,r2),axis=0)
    #r = np.linspace(0,1,nc)

    #g1 = np.linspace(0,0.8,np.round(nc/2))
    #g2 = np.linspace(1,0,nc-np.round(nc/2))
    #g = np.concatenate((g1,g2),axis=0)
    #cmap = np.array([r,g,b]).transpose().tolist()

    cvec = ["#FF00FF","#CC00FF","#AA00FF","#0000FF","#0066FF","#00AAFF","#00CCFF","#00FFFF","#00FFCC","#00FFAA",
             "#00FF66","#00FF00","#AAFF00","#CCFF00","#FFFF00","#FFCC00","#FFAA00","#FF9900","#FF5500","#FF0000"]
    ic = np.linspace(0,len(cvec)-1,nc).astype(int).tolist()
    cmap = [cvec[i] for i in ic]

    pin_radius = 0.028*0.9
    pin_delta = 0.083*0.85
    
    # Draw enrichment level circles
    self.enrpinlist = []
    x = 1.06
    for i in range(enr_levels.size):
        y = 0.95-i*pin_delta
        enrobj = cpin(self.axes)
        enrobj.set_circle(x,y,0.028,cmap[i])
        enrobj.set_text(str(i+1))
        #circobj = Circle(self.axes,x,y,cmap[i],str(i+1),pin_radius)
        self.axes.add_patch(enrobj.circle)
        self.axes.text(x+0.05,y,"%.2f" % enr_levels[i],fontsize=8)
        enrobj.ENR = enr_levels[i]
        enrobj.BA = enr_ba[i]
        if not np.isnan(enr_ba[i]):
            enrobj.text.remove()
            enrobj.set_text('Ba')
            self.axes.text(x+0.05,y-0.03,"%.2f" % enr_ba[i],fontsize=8)
            
        self.enrpinlist.append(enrobj)

    # Print average enrichment
    ave_enr = self.dataobj.cases[case_num].data.ave_enr
    self.axes.text(1.02,0.05,"%.3f %%U-235" % ave_enr,fontsize=8)

    # List of pin coordinates
    self.xlist = ('1','2','3','4','5','6','7','8','9','10')
    self.ylist  = ('A','B','C','D','E','F','G','H','I','J')
    
    # Draw pin circles
    npst = self.dataobj.cases[case_num].data.npst
    LFU = self.dataobj.cases[case_num].data.LFU

    pin_radius = 0.028*1.1
    pin_delta = 0.083

    #self.circlelist = []
    k = 0
    for i in range(LFU.shape[0]):
        for j in range(LFU.shape[1]):
            x = 0.13+j*pin_delta
            y = 0.875-i*pin_delta
            if LFU[i,j] > 0:
                self.pinobjects[case_num][k].set_circle(x,y,pin_radius,(1,1,1))
                self.pinobjects[case_num][k].coord = self.ylist[i] + self.xlist[j]
                self.pinobjects[case_num][k].set_text()
                self.axes.add_patch(self.pinobjects[case_num][k].circle)
                k += 1
                #circobj = Circle(self.axes,x,y,(1,1,1),'',pin_radius)
                #circobj.coord = self.ylist[i] + self.xlist[j]
                #self.circlelist.append(circobj)

    # Draw pin coordinates                
    # x-axis
    for i in range(10):
        self.axes.text(0.13+i*pin_delta,0.015,self.xlist[i],ha='center',va='center',fontsize=9)
    #for i in range(5,10):
    #    self.axes.text(0.17+i*pin_delta,0.015,self.xlist[i],ha='center',va='center',fontsize=9)
        
    # y-axis
    for i in range(10):
        self.axes.text(0.99,0.875-i*pin_delta,self.ylist[i],ha='center',va='center',fontsize=9)
    #for i in range(5,10):
    #    self.axes.text(0.99,0.83-i*pin_delta,self.ylist[i],ha='center',va='center',fontsize=9)
        
        #self.canvas.draw()
        #Tracer()()
