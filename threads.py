from IPython.core.debugger import Tracer  # Set tracepoint (used for debugging)
from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
from PyQt4 import QtGui, QtCore
import numpy as np

from bundle import Bundle



class ImportThread(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent
        self._kill = False
        
    def __del__(self):
        self.wait()

    def run(self):
        if not self._kill:
            bundle = self.parent.bunlist[0]
            # Importing data
            bundle.readcax(content=bundle.data.content)
            bundle.new_btf()

            self.parent.bunlist.pop()
            self.parent.bunlist.append(bundle)
            self.emit(QtCore.SIGNAL('import_data_finished()'))

            # Perform reference calculation
            print "Performing reference calculation..."
            biascalc = Bundle(parent=bundle)
            biascalc.new_calc(model="C3", dep_max=None,
                                   dep_thres=None, voi=None)
            self.parent.biascalc = biascalc
            

class RunC4Thread(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent
        self._kill = False
        
    def __del__(self):
        self.wait()

    def run(self):
        if not self._kill:
            # create new bundle
            self.bundle = Bundle(parent=self.parent.bunlist[0])            
            
            # update bundle attributes
            voi = None
            chanbow = self.parent.chanbow_sbox.value() / 10  # mm -> cm
            nsegs = len(self.bundle.segments)
            for iseg in xrange(nsegs):
                LFU = self.lfumap(iseg)
                FUE = self.fuemap(iseg)
                BA = self.bamap(iseg)
                self.bundle.segments[iseg].set_data(LFU, FUE, BA, voi, chanbow)
            
            # set calc. parameters
            model = "C4E"
            c4ver = self.parent.params.cas_version
            neulib = self.parent.params.cas_neulib
            gamlib = self.parent.params.cas_gamlib
            grid = True if self.parent.params.cas_cpu == "grid" else False
            keepfiles = self.parent.params.cas_keepfiles

            self.bundle.new_calc(model=model, c4ver=c4ver, neulib=neulib, 
                                 gamlib=gamlib, grid=grid, keepfiles=keepfiles)
            self.bundle.new_btf()
            self.parent.bunlist.append(self.bundle)

    def lfumap(self, iseg):
        """Creating FUE map from pinobjects"""

        LFU = getattr(self.bundle.segments[iseg].data, "LFU")
        LFU_new = np.zeros(LFU.shape).astype(int)
        k = 0
        for i in xrange(LFU.shape[0]):
            for j in xrange(LFU.shape[1]):
                if LFU[i, j] > 0:
                    LFU_new[i, j] = getattr(self.parent.pinobjects[iseg][k], 
                                          "LFU")
                    k += 1
        return LFU_new

    def fuemap(self, iseg):
        """Creating FUE map from enr level pins"""

        FUE = getattr(self.bundle.segments[iseg].data, "FUE")
        nfue = len(self.parent.enrpinlist[iseg])
        FUE_new = np.zeros((nfue, FUE.shape[1])).astype(float)
        for i in xrange(nfue):
            FUE_new[i, 0] = i + 1
            FUE_new[i, 1] = self.parent.enrpinlist[iseg][i].DENS
            FUE_new[i, 2] = self.parent.enrpinlist[iseg][i].ENR
            FUE_new[i, 3] = self.parent.enrpinlist[iseg][i].BAindex
            FUE_new[i, 4] = self.parent.enrpinlist[iseg][i].BA
        return FUE_new
        
    def bamap(self, iseg):
        """Creating BA map from pinobjects"""

        LFU = getattr(self.bundle.segments[iseg].data, "LFU")
        BA = np.zeros(LFU.shape).astype(float)
        k = 0
        for i in xrange(BA.shape[0]):
            for j in xrange(BA.shape[1]):
                if LFU[i, j] > 0:
                    BA[i, j] = getattr(self.parent.pinobjects[iseg][k], "BA")
                    k += 1
        return BA
