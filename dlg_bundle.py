from PyQt4 import QtGui, QtCore

class BundleDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Edit bundle")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(xpos, ypos, 150, 120))

        flo = QtGui.QFormLayout()
        self.fuetype_cbox = QtGui.QComboBox()
        fue_list = ["OPT2", "OPT3", "A10B", "A10XM", "AT11"]
        self.fuetype_cbox.addItems(QtCore.QStringList(fue_list))

        self.files_cbox = QtGui.QComboBox()
        self.files_cbox.addItems(QtCore.QStringList([]))

        self.nodes_cbox = QtGui.QComboBox()
        self.nodes_cbox.addItems(QtCore.QStringList([]))

        flo.addRow("Fuel type:", self.fuetype_cbox)
        flo.addRow("Files:", self.files_cbox)
        flo.addRow("Nodes:", self.nodes_cbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("Bundle settings")
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
