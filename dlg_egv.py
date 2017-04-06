from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
import os
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
        self.setGeometry(QtCore.QRect(0.8*xpos, 0.9*ypos, 500, 210))

        # Table
        self.table = QtGui.QTableWidget(0, 2)

        self.table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("Zone"))
        self.table.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("File"))

        verticalheader = self.table.verticalHeader()
        verticalheader.setResizeMode(QtGui.QHeaderView.Fixed)
        verticalheader.setDefaultSectionSize(25)

        horizontalheader = self.table.horizontalHeader()
        horizontalheader.setResizeMode(1, QtGui.QHeaderView.Stretch)

        # Group box
        self.version_cbox = QtGui.QComboBox()
        self.version_list = ["2.3.0", "3.2.1"]
        self.version_cbox.addItems(QtCore.QStringList(self.version_list))

        self.reactor_cbox = QtGui.QComboBox()
        self.reactor_list = ["F1", "F2", "F3", "R1"]
        self.reactor_cbox.addItems(QtCore.QStringList(self.reactor_list))

        # EGV fue: ATRIUM10B, ATRIUM10XM, SVEA96OPTIMA3

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

        self.insert_table_rows()
        self.table.resizeColumnsToContents()
        #self.table.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

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
        params  = self.parent.params
        params.egv_version = str(self.version_cbox.currentText())
        params.egv_reactor = str(self.reactor_cbox.currentText())
        nrows = self.table.rowCount()
        params.egv_zones = []
        params.egv_files = []
        for i in range(nrows):
            zone_cbox = self.table.cellWidget(i, 0)
            if str(zone_cbox.currentText()) == "None":
                params.egv_zones.append(None)
            else:
                params.egv_zones.append(str(zone_cbox.currentText()))
            item = self.table.item(i, 1)
            params.egv_files.append(str(item.text()))
        params.egv_zones.reverse()
        params.egv_files.reverse()

    def insert_table_rows(self):
        """Fill table rows in reverse order"""
        
        if hasattr(self.parent, "bunlist"):
            bundle = self.parent.bunlist[0]
            caxfiles = bundle.data.caxfiles[::-1]
            zone_list = ["None", "Lower End", "Lower Active", "Upper Active", "Upper End"]
            if hasattr(self.parent.params, "egv_zones"):
                zones = self.parent.params.egv_zones[::-1]
            else:
                zones = None
                
            nrows = len(caxfiles)
            for i in range(nrows):
                self.table.insertRow(i)
                vheader = QtGui.QTableWidgetItem(str(nrows - i))
                self.table.setVerticalHeaderItem(i, vheader)
                zone_cbox = QtGui.QComboBox()
                zone_cbox.addItems(QtCore.QStringList(zone_list))

                if zones is not None:
                    if zones[i]:
                        j = zone_list.index(zones[i])
                    else:
                        j = zone_list.index("None")
                    zone_cbox.setCurrentIndex(j)

                self.table.setCellWidget(i, 0, zone_cbox)
                fname = caxfiles[i].split(os.sep)[-1]
                item = QtGui.QTableWidgetItem(fname)
                self.table.setItem(i, 1, item)
