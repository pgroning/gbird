from PyQt4 import QtGui, QtCore

class EgvDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("EGV settings")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.8*xpos, 0.9*ypos, 500, 200))

        # Table
        self.table = QtGui.QTableWidget(0, 2)
        #self.table = QtGui.QTableWidget(1, 2)

        self.table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("Zone"))
        self.table.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("File"))

        verticalheader = self.table.verticalHeader()
        verticalheader.setResizeMode(QtGui.QHeaderView.Fixed)
        verticalheader.setDefaultSectionSize(25)

        # Left menu
        self.version_cbox = QtGui.QComboBox()
        self.version_list = ["2.3.0", "3.2.1"]
        self.version_cbox.addItems(QtCore.QStringList(self.version_list))

        self.reactor_cbox = QtGui.QComboBox()
        self.reactor_list = ["R1", "F1", "F2", "F3"]
        self.reactor_cbox.addItems(QtCore.QStringList(self.reactor_list))

        flo = QtGui.QFormLayout()
        flo.addRow("Version:", self.version_cbox)
        flo.addRow("Reactor:", self.reactor_cbox)

        gbox = QtGui.QGroupBox()
        gbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        gbox.setLayout(flo)

        grid = QtGui.QGridLayout()
        grid.addWidget(gbox, 0, 0)
        grid.addWidget(self.table, 0, 1)

        self.set_table_rows()
        
        hbox = QtGui.QHBoxLayout()
        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")
        hbox.addStretch()
        hbox.addWidget(self.ok_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), 
                     self.ok_action)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def ok_action(self):
        self.close()
        
    def set_table_rows(self):
        """set table rows"""
        
        for i in range(3):
            self.table.insertRow(i)
            zone_cbox = QtGui.QComboBox()
            zone_cbox.addItem("None")
            zone_cbox.addItem("Lower end")
            zone_cbox.addItem("Lower active")
            zone_cbox.addItem("Upper active")
            zone_cbox.addItem("Upper end")
            self.table.setCellWidget(i, 0, zone_cbox)

