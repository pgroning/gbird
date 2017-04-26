from PyQt4 import QtGui, QtCore

class PertDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Perturbation")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(xpos-100, ypos-50, 150, 120))

        flo = QtGui.QFormLayout()
        
        model_list = ["C3"]
        self.model_cbox = QtGui.QComboBox()
        self.model_cbox.addItems(QtCore.QStringList(model_list))
        if hasattr(self.parent.params, "pert_model"):
            i = model_list.index(self.parent.params.pert_model)
            self.model_cbox.setCurrentIndex(i)

        depmax_list = ["undef", "10", "15", "20", "30", "40"]
        self.depmax_cbox = QtGui.QComboBox()
        self.depmax_cbox.addItems(QtCore.QStringList(depmax_list))
        if hasattr(self.parent.params, "pert_depmax"):
            if type(self.parent.params.pert_depmax) == float:
                depmax_str = str(int(self.parent.params.pert_depmax))
                i = depmax_list.index(depmax_str)
            else:
                i = depmax_list.index("undef")
            self.depmax_cbox.setCurrentIndex(i)

        depthres_list = ["undef", "10", "15", "20", "30", "40"]
        self.depthres_cbox = QtGui.QComboBox()
        self.depthres_cbox.addItems(QtCore.QStringList(depthres_list))
        if hasattr(self.parent.params, "pert_depthres"):
            if type(self.parent.params.pert_depthres) == float:
                depthres_str = str(int(self.parent.params.pert_depthres))
                i = depthres_list.index(depthres_str)
            else:
                i = depthres_list.index("undef")
            self.depthres_cbox.setCurrentIndex(i)

        voi_list = ["undef", "0", "40", "50", "60", "80"]
        self.voi_cbox = QtGui.QComboBox()
        self.voi_cbox.addItems(QtCore.QStringList(voi_list))
        if hasattr(self.parent.params, "pert_voi"):
            if type(self.parent.params.pert_voi) == float:
                voi_str = str(int(self.parent.params.pert_voi))
                i = voi_list.index(voi_str)
            else:
                i = voi_list.index("undef")
            self.voi_cbox.setCurrentIndex(i)

        flo.addRow("Model:", self.model_cbox)
        flo.addRow("Maximum depletion:", self.depmax_cbox)
        flo.addRow("Depletion threshold:", self.depthres_cbox)
        flo.addRow("Void:", self.voi_cbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("Settings")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        grid = QtGui.QGridLayout()
        grid.addWidget(groupbox, 0, 0)
        
        hbox = QtGui.QHBoxLayout()
        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")
        hbox.addWidget(self.ok_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), 
                     self.ok_action)

        vbox = QtGui.QVBoxLayout()
        #vbox.addLayout(flo)
        vbox.addLayout(grid)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def ok_action(self):
        self.close()
        params = self.parent.params
        params.pert_model = str(self.model_cbox.currentText())
        if self.depmax_cbox.currentText() == "undef":
            params.pert_depmax = None
        else:
            params.pert_depmax = float(self.depmax_cbox.currentText())
        if self.depthres_cbox.currentText() == "undef":
            params.pert_depthres = None
        else:
            params.pert_depthres = float(self.depthres_cbox.currentText())
        if self.voi_cbox.currentText() == "undef":
            params.pert_voi = None
        else:
            params.pert_voi = float(self.voi_cbox.currentText())
        if hasattr(self.parent, "biascalc"):
            del self.parent.biascalc  # bias calc should be updated
