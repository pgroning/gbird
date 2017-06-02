from IPython.core.debugger import Tracer  # Set tracepoint (used for debugging)
from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
from PyQt4 import QtGui, QtCore

from bundle import Bundle



class importThread(QtCore.QThread):
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
            
