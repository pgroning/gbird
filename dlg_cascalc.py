from IPython.core.debugger import Tracer  # Set tracepoint with Tracer()()
# Set a tracepoint that works with Qt
from pyqt_trace import pyqt_trace as qtrace # Set tracepoint with qtrace()

import os
import re
from PyQt4 import QtGui, QtCore

#from casinp import Casinp


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
        #pert_gbox = self.pert_group()
        cas_gbox = self.cas_group()
        #self.grid.addWidget(pert_gbox, 0, 0)
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
        #vbox.addLayout(flo)
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

        #self.parent.pert_model = str(self.model_cbox.currentText())
        #if self.depmax_cbox.currentText() == "undef":
        #    self.parent.pert_depmax = None
        #else:
        #    self.parent.pert_depmax = float(self.depmax_cbox.currentText())
        #if self.depthres_cbox.currentText() == "undef":
        #    self.parent.pert_depthres = None
        #else:
        #    self.parent.pert_depthres = float(self.depthres_cbox.currentText())
        #if self.void_cbox.currentText() == "undef":
        #    self.parent.pert_voi = None
        #else:
        #    self.parent.pert_voi = float(self.void_cbox.currentText())
        #if hasattr(self.parent, "biascalc"):
        #    del self.parent.biascalc  # bias calc must be updated

    def cas_group(self):
        flo = QtGui.QFormLayout()

        version_list = self.get_versions()
        self.version_cbox = QtGui.QComboBox()
        self.version_cbox.addItems(QtCore.QStringList(version_list))
        if hasattr(self.parent.params, "cas_version"):
            i = version_list.index(self.parent.params.cas_version)
            self.version_cbox.setCurrentIndex(i)
        else:
            self.version_cbox.setCurrentIndex(3)  # set default version

        neulib_list = self.get_neulibs()
        self.neulib_cbox = QtGui.QComboBox()
        self.neulib_cbox.addItems(QtCore.QStringList(neulib_list))
        if hasattr(self.parent.params, "cas_neulib"):
            i = neulib_list.index(self.parent.params.cas_neulib)
            self.neulib_cbox.setCurrentIndex(i)
        else:
            self.neulib_cbox.setCurrentIndex(8)

        gamlib_list = self.get_gamlibs()
        self.gamlib_cbox = QtGui.QComboBox()
        self.gamlib_cbox.addItems(QtCore.QStringList(gamlib_list))
        if hasattr(self.parent.params, "cas_gamlib"):
            i = gamlib_list.index(self.parent.params.cas_gamlib)
            self.gamlib_cbox.setCurrentIndex(i)
        else:
            self.gamlib_cbox.setCurrentIndex(0)

        cpu_list = ["local", "grid"]
        self.cpu_cbox = QtGui.QComboBox()
        self.cpu_cbox.addItems(QtCore.QStringList(cpu_list))
        if hasattr(self.parent.params, "cas_cpu"):
            i = cpu_list.index(self.parent.params.cas_cpu)
            self.cpu_cbox.setCurrentIndex(i)
        else:
            self.cpu_cbox.setCurrentIndex(0)

        self.file_chbox = QtGui.QCheckBox()
        if hasattr(self.parent.params, "cas_keepfiles"):
            if self.parent.params.cas_keepfiles:
                self.file_chbox.setChecked(True)

        #self.owrite_chbox = QtGui.QCheckBox()
        
        flo.addRow("Version:", self.version_cbox)
        flo.addRow("Neutron library:", self.neulib_cbox)
        flo.addRow("Gamma library:", self.gamlib_cbox)
        flo.addRow("CPU:", self.cpu_cbox)
        flo.addRow("Keep files:", self.file_chbox)
        #flo.addRow("Overwrite orig. inp. file:", self.owrite_chbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("CASMO-4E")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        return groupbox
        
    def pert_group(self):
        flo = QtGui.QFormLayout()
        self.model_cbox = QtGui.QComboBox()
        self.model_cbox.addItems(QtCore.QStringList(["C3", "C4E"]))

        self.depmax_cbox = QtGui.QComboBox()
        self.depmax_cbox.addItems(QtCore.QStringList(["undef", "10", "15",
                                                      "20", "30", "40"]))

        self.depthres_cbox = QtGui.QComboBox()
        self.depthres_cbox.addItems(QtCore.QStringList(["undef", "10", "15",
                                                      "20", "30", "40"]))

        self.void_cbox = QtGui.QComboBox()
        self.void_cbox.addItems(QtCore.QStringList(["undef", "0", "40",
                                                      "50", "60", "80"]))

        flo.addRow("Model:", self.model_cbox)
        flo.addRow("Maximum depletion:", self.depmax_cbox)
        flo.addRow("Depletion threshold:", self.depthres_cbox)
        flo.addRow("Void:", self.void_cbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("Perturbation")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        return groupbox
        
    def get_versions(self):
        """Get list of available C4E versions"""

        path = "/home/prog/prod/CMSCODES/C4E"
        if os.path.isdir(path):
            ver_list = os.listdir(path)
            ver_list = [v.lstrip("v") for v in ver_list]
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
        """Get list of available gamlibs"""

        path = "/home/prog/prod/CMSCODES/CasLib/library"
        if os.path.isdir(path):
            files = os.listdir(path)
            rec = re.compile("^gal")
            gamlib_list = [f for f in files if rec.match(f)]
        else:
            gamlib_list = []
        return gamlib_list


class CasRunDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Run CASMO-4E")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.8*xpos, 0.9*ypos, 150, 120))

        flo = QtGui.QFormLayout()
        #self.cpu_cbox = QtGui.QComboBox()
        #self.cpu_cbox.addItems(QtCore.QStringList(["local", "grid"]))
        #flo.addRow("CPU:", self.cpu_cbox)

        self.replace_chbox = QtGui.QCheckBox("")
        flo.addRow("Replace original:", self.replace_chbox)
        
        self.owrite_chbox = QtGui.QCheckBox("")
        flo.addRow("Overwrite orig. inp. file:", self.owrite_chbox)

        hbox = QtGui.QHBoxLayout()
        self.run_button = QtGui.QPushButton("Run")
        self.cancel_button = QtGui.QPushButton("Cancel")
        hbox.addWidget(self.run_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.run_button, QtCore.SIGNAL('clicked()'), 
                     self.run_action)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(flo)
        #vbox.addWidget(self.owrite_chbox)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def run_action(self):
        """Create .inp files and""" 
        self.close()
        self.parent.create_inpfiles()
        self.parent.complete_calc()

        ##self.parent.quick_calc()
    
#    def complete_calc(self):
#        """run complete cas calcs"""
#        print "running complete Cas calcs"
#        
#        ibundle = self.parent.ibundle
#        bundle = self.parent.bunlist[ibundle]
#        segment = bundle.segments[0]
#        inpfile = "test/topol/AT-B/00g00nb/e26AT-B-071-00g00nb-cas.T.inp"
#        #segment.runc4(file_base_name)
#        segment.complete_calc(inpfile, neulib="j20200")

#    def create_inp(self):
#        """Create Cas inp files"""
#        print "Creating inp files..."
#        
#        ibundle = self.parent.ibundle
#        bundle = self.parent.bunlist[ibundle]
#        cinp = Casinp(bundle.segments, verbose=True)
#        
#        cinp.existfiles(verbose=True)
#        cinp.createinp(verbose=True)
#
