from IPython.core.debugger import Tracer

import sys
from PyQt4 import QtGui, QtCore


class ProgressBar(QtGui.QDialog):
    def __init__(self, parent=None, total=100):
        super(ProgressBar, self).__init__(parent)
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(total)
        self.button = QtGui.QPushButton('Cancel')
        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        spacerItemH = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, 
                                        QtGui.QSizePolicy.Minimum)
        vbox.addWidget(self.progressbar)
        hbox.addItem(spacerItemH)
        hbox.addWidget(self.button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        #main_layout = QGridLayout()
        #main_layout.addWidget(self.progressbar, 0, 0)
        #main_layout.addWidget(self.button, 1, 0)
        #self.setLayout(main_layout)
        self.setWindowTitle("Importing data...")
        self.resize(300, 50)
        self.setMaximumHeight(50)
        self.move(500, 500)
        self.setModal(True)

    def update(self,val):
        self.progressbar.setValue(val)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    bar = ProgressBar()
    bar.show()
    sys.exit(app.exec_())

