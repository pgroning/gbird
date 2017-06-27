from IPython.core.debugger import Tracer

import sys
from PyQt4 import QtGui, QtCore


class ProgressBar(QtGui.QDialog):
    def __init__(self, parent=None, total=100, button=True):
        super(ProgressBar, self).__init__(parent)
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(total)
        self.progressbar.setTextVisible(False)
        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        spacerItemH = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, 
                                        QtGui.QSizePolicy.Minimum)
        vbox.addWidget(self.progressbar)
        hbox.addItem(spacerItemH)
        if button:
            self.button = QtGui.QPushButton('Cancel')
            hbox.addWidget(self.button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
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

