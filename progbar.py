from IPython.core.debugger import Tracer

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ProgressBar(QDialog):
#class ProgressBar(QWidget):
    def __init__(self, parent=None, total=100):
        super(ProgressBar, self).__init__(parent)
        self.progressbar = QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(total)
        self.button = QPushButton('Cancel')
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        spacerItemH = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        vbox.addWidget(self.progressbar)
        hbox.addItem(spacerItemH)
        hbox.addWidget(self.button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        #main_layout = QGridLayout()
        #main_layout.addWidget(self.progressbar, 0, 0)
        #main_layout.addWidget(self.button, 1, 0)
        #self.setLayout(main_layout)
        self.setWindowTitle('Reading data...')
        self.resize(300,50)
        self.setMaximumHeight(50)
        self.move(500,500)
        self.setModal(True)
        #Tracer()()

    def update(self,val):
        self.progressbar.setValue(val)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    bar = ProgressBar()
    bar.show()
    sys.exit(app.exec_())

