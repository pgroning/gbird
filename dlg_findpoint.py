from PyQt4 import QtGui, QtCore

class FindDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Find state point")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(xpos, ypos, 150, 120))

        flo = QtGui.QFormLayout()
        
        voi_list = map(str, self.parent.bunlist[-1].segments[0].data.voilist)
        self.voi_cbox = QtGui.QComboBox()
        self.voi_cbox.addItems(QtCore.QStringList(voi_list))

        self.vhi_cbox = QtGui.QComboBox()
        self.vhi_cbox.addItems(QtCore.QStringList(voi_list))

        tfu_list = ["undef", "551", "771"]
        self.tfu_cbox = QtGui.QComboBox()
        self.tfu_cbox.addItems(QtCore.QStringList(tfu_list))

        tmo_list = ["undef", "551", "771"]
        self.tmo_cbox = QtGui.QComboBox()
        self.tmo_cbox.addItems(QtCore.QStringList(tmo_list))

        exp_list = ["undef", "0", "0.001", "0.1", "1", "10", "20"]
        self.exp_cbox = QtGui.QComboBox()
        self.exp_cbox.addItems(QtCore.QStringList(exp_list))

        flo.addRow("VOI:", self.voi_cbox)
        flo.addRow("VHI:", self.vhi_cbox)
        flo.addRow("TFU:", self.tfu_cbox)
        flo.addRow("TMO:", self.tmo_cbox)
        flo.addRow("EXP:", self.exp_cbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("Parameters")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        grid = QtGui.QGridLayout()
        grid.addWidget(groupbox, 0, 0)
        
        hbox = QtGui.QHBoxLayout()
        self.find_button = QtGui.QPushButton("Find")
        self.close_button = QtGui.QPushButton("Close")
        hbox.addWidget(self.find_button)
        hbox.addWidget(self.close_button)
        self.connect(self.close_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.find_button, QtCore.SIGNAL('clicked()'), 
                     self.find_action)

        vbox = QtGui.QVBoxLayout()
        #vbox.addLayout(flo)
        vbox.addLayout(grid)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def find_action(self):
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
