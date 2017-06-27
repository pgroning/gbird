from IPython.core.debugger import Tracer  # Set tracepoint with Tracer()()
# Set a tracepoint that works with Qt
from pyqt_trace import pyqt_trace as qtrace # Set tracepoint with qtrace()

import os
import re
from PyQt4 import QtGui, QtCore


class CasDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("CASMO")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.8*xpos, 0.9*ypos, 150, 120))
        
        self.grid = QtGui.QGridLayout()
        cas_gbox = self.cas_group()
        self.grid.addWidget(cas_gbox, 0, 0)
        
        hbox = QtGui.QHBoxLayout()
        self.run_button = QtGui.QPushButton("Run")
        self.cancel_button = QtGui.QPushButton("Cancel")
        hbox.addStretch()
        hbox.addWidget(self.run_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.run_button, QtCore.SIGNAL('clicked()'), 
                     self.run_action)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.grid)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def run_action(self):
        self.close()
        self.parent.params.cas_version = str(self.version_cbox.currentText())
        self.parent.params.cas_neulib = str(self.neulib_cbox.currentText()) 
        self.parent.params.cas_gamlib = str(self.gamlib_cbox.currentText())
        self.parent.params.cas_cpu = str(self.cpu_cbox.currentText())
        self.parent.params.cas_keepfiles = self.file_chbox.isChecked()
        self.parent.cas_calc()

    def cas_group(self):
        flo = QtGui.QFormLayout()
        
        version_list = self.get_versions()
        self.version_cbox = QtGui.QComboBox()
        self.version_cbox.addItems(QtCore.QStringList(version_list))
        if hasattr(self.parent.params, "cas_version"):
            i = version_list.index(self.parent.params.cas_version)
            self.version_cbox.setCurrentIndex(i)
        else:  # set default version
            default_version = self.parent.config.default_version
            i = version_list.index(default_version)
            self.version_cbox.setCurrentIndex(i)

        neulib_list = self.get_neulibs()
        self.neulib_cbox = QtGui.QComboBox()
        self.neulib_cbox.addItems(QtCore.QStringList(neulib_list))
        if hasattr(self.parent.params, "cas_neulib"):
            i = neulib_list.index(self.parent.params.cas_neulib)
            self.neulib_cbox.setCurrentIndex(i)
        else:  # set default lib version
            default_neulib = self.parent.config.default_neulib
            i = neulib_list.index(default_neulib)
            self.neulib_cbox.setCurrentIndex(i)

        gamlib_list = self.get_gamlibs()
        self.gamlib_cbox = QtGui.QComboBox()
        self.gamlib_cbox.addItems(QtCore.QStringList(gamlib_list))
        if hasattr(self.parent.params, "cas_gamlib"):
            i = gamlib_list.index(self.parent.params.cas_gamlib)
            self.gamlib_cbox.setCurrentIndex(i)
        else:
            default_gamlib = self.parent.config.default_gamlib
            i = gamlib_list.index(default_gamlib)
            self.gamlib_cbox.setCurrentIndex(i)

        cpu_list = ["local", "grid"]
        self.cpu_cbox = QtGui.QComboBox()
        self.cpu_cbox.addItems(QtCore.QStringList(cpu_list))
        if hasattr(self.parent.params, "cas_cpu"):
            i = cpu_list.index(self.parent.params.cas_cpu)
            self.cpu_cbox.setCurrentIndex(i)
        else:
            default_cpu = self.parent.config.default_cpu
            i = cpu_list.index(default_cpu)
            self.cpu_cbox.setCurrentIndex(i)

        self.file_chbox = QtGui.QCheckBox()
        if hasattr(self.parent.params, "cas_keepfiles"):
            if self.parent.params.cas_keepfiles:
                self.file_chbox.setChecked(True)
        
        flo.addRow("Version:", self.version_cbox)
        flo.addRow("Neutron library:", self.neulib_cbox)
        flo.addRow("Gamma library:", self.gamlib_cbox)
        flo.addRow("CPU:", self.cpu_cbox)
        flo.addRow("Keep files:", self.file_chbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("CASMO-4E")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        return groupbox
                
    def get_versions(self):
        """Get list of available C4E versions"""

        path = self.parent.config.casdir
        if os.path.isdir(path):
            ver_list = os.listdir(path)
            ver_list = [v.lstrip("v") for v in ver_list]
        else:
            ver_list = []
        return ver_list

    def get_neulibs(self):
        """List available neulibs"""

        path = self.parent.config.libdir
        if os.path.isdir(path):
            files = os.listdir(path)
            rec = re.compile("^e4|^j2")
            neulib_list = [f for f in files if rec.match(f)]
        else:
            neulib_list = []
        return neulib_list

    def get_gamlibs(self):
        """Get list of available gamlibs"""

        path = self.parent.config.libdir
        if os.path.isdir(path):
            files = os.listdir(path)
            rec = re.compile("^gal")
            gamlib_list = [f for f in files if rec.match(f)]
        else:
            gamlib_list = []
        return gamlib_list
