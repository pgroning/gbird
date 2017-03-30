from PyQt4 import QtGui, QtCore

class PertDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Perturbation model")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(xpos, ypos, 150, 120))

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
        if self.void_cbox.currentText() == "undef":
            params.pert_voi = None
        else:
            params.pert_voi = float(self.void_cbox.currentText())
        if hasattr(self.parent, "biascalc"):
            del self.parent.biascalc  # bias calc should be updated
