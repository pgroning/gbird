import os
import re
from PyQt4 import QtGui, QtCore

class CasDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent

        self.setWindowTitle("CASMO")
        xpos = parent.pos().x() + parent.size().width() / 2
        ypos = parent.pos().y() + parent.size().height() / 2
        self.setGeometry(QtCore.QRect(xpos, ypos, 150, 120))

        flo = QtGui.QFormLayout()

        self.version_cbox = QtGui.QComboBox()
        ver_list = self.get_versions()
        self.version_cbox.addItems(QtCore.QStringList(ver_list))
        self.version_cbox.setCurrentIndex(3)  # set default version

        self.neulib_cbox = QtGui.QComboBox()
        neulib_list = self.get_neulibs()
        self.neulib_cbox.addItems(QtCore.QStringList(neulib_list))
        self.neulib_cbox.setCurrentIndex(3)

        self.gamlib_cbox = QtGui.QComboBox()
        gamlib_list = self.get_gamlibs()
        self.gamlib_cbox.addItems(QtCore.QStringList(gamlib_list))
        self.gamlib_cbox.setCurrentIndex(0)

        self.cpu_cbox = QtGui.QComboBox()
        self.cpu_cbox.addItems(QtCore.QStringList(["local", "grid"]))

        flo.addRow("Version:", self.version_cbox)
        flo.addRow("Neutron library:", self.neulib_cbox)
        flo.addRow("Gamma library:", self.gamlib_cbox)
        flo.addRow("CPU:", self.cpu_cbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("CASMO-4E settings")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        grid = QtGui.QGridLayout()
        grid.addWidget(groupbox, 0, 0)
        
        hbox = QtGui.QHBoxLayout()
        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")
        hbox.addStretch()
        hbox.addWidget(self.ok_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), self.action)

        vbox = QtGui.QVBoxLayout()
        #vbox.addLayout(flo)
        vbox.addLayout(grid)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def action(self):
        self.close()

    def get_versions(self):
        """List available C4E versions"""

        path = "/home/prog/prod/CMSCODES/C4E"
        if os.path.isdir(path):
            ver_list = os.listdir(path)
        else:
            ver_list = []
        return ver_list

    def get_neulibs(self):
        """List available neulibs"""

        path = "/home/prog/prod/CMSCODES/CasLib/library"
        if os.path.isdir(path):
            files = os.listdir(path)
            rec = re.compile("^e4|^j2")
            neulib_list = [f for f in files if rec.match(f)]
        else:
            neulib_list = []
        return neulib_list

    def get_gamlibs(self):
        """List available gamlibs"""

        path = "/home/prog/prod/CMSCODES/CasLib/library"
        if os.path.isdir(path):
            files = os.listdir(path)
            rec = re.compile("^gal")
            gamlib_list = [f for f in files if rec.match(f)]
        else:
            gamlib_list = []
        return gamlib_list
