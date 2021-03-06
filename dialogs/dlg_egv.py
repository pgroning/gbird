# -*- coding: utf-8 -*-

from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
import os
import re
from PyQt4 import QtGui, QtCore
from multiprocessing import Pool

from egv import do_egv


class EgvDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("EGV settings")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.6*xpos, 0.9*ypos, 650, 210))

        # Table
        self.table = QtGui.QTableWidget(0, 2)

        self.table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("Zone"))
        self.table.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("File"))

        horizontalheader = self.table.horizontalHeader()
        horizontalheader.setResizeMode(1, QtGui.QHeaderView.Stretch)

        verticalheader = self.table.verticalHeader()
        verticalheader.setResizeMode(QtGui.QHeaderView.Fixed)
        verticalheader.setDefaultSectionSize(25)

        # Group box
        self.version_cbox = QtGui.QComboBox()
        self.version_list = self.get_versions()
        self.version_cbox.addItems(QtCore.QStringList(self.version_list))

        self.reactor_cbox = QtGui.QComboBox()
        self.reactor_list = ["F1", "F2", "F3", "R1"]
        self.reactor_cbox.addItems(QtCore.QStringList(self.reactor_list))

        self.file_chbox = QtGui.QCheckBox()
        
        flo = QtGui.QFormLayout()
        flo.addRow("Version:", self.version_cbox)
        flo.addRow("Reactor:", self.reactor_cbox)
        flo.addRow("Keep files:", self.file_chbox)

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
        
        hbox = QtGui.QHBoxLayout()
        self.run_button = QtGui.QPushButton("Run")
        self.cancel_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        hbox.addWidget(self.run_button)
        hbox.addStretch()
        hbox.addWidget(self.apply_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.run_button, QtCore.SIGNAL('clicked()'), 
                     self.run_action)
        self.connect(self.apply_button, QtCore.SIGNAL('clicked()'), 
                     self.apply_action)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def apply_action(self):
        params  = self.parent.params
        params.egv_version = str(self.version_cbox.currentText())
        params.egv_reactor = str(self.reactor_cbox.currentText())
        params.egv_keepfiles = self.file_chbox.isChecked()
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

    def run_action(self):
        self.close()
        self.apply_action()
        self.run_egv()

    def insert_table_rows(self):
        """Fill table rows in reverse order"""
        
        if hasattr(self.parent, "bunlist"):
            bundle = self.parent.bunlist[0]

            orgfiles = bundle.data.caxfiles[::-1]
            caxfiles = ["gb-" + os.path.split(f)[-1] for f in orgfiles]

            zone_list = ["None", "Upper End", "Upper Active", "Lower Active",
                         "Lower End"]
            
            if hasattr(self.parent.params, "egv_version"):
                version = self.parent.params.egv_version
                j = self.version_list.index(version)
                self.version_cbox.setCurrentIndex(j)

            if hasattr(self.parent.params, "egv_reactor"):
                reactor = self.parent.params.egv_reactor
                j = self.reactor_list.index(reactor)
                self.reactor_cbox.setCurrentIndex(j)

            if hasattr(self.parent.params, "egv_keepfiles"):
                if self.parent.params.egv_keepfiles:
                    self.file_chbox.setChecked(True)

            if hasattr(self.parent.params, "egv_zones"):
                zones = self.parent.params.egv_zones[::-1]
            else:
                zones = None

            if hasattr(self.parent.params, "egv_files"):
                files = self.parent.params.egv_files[::-1]
            else:
                files = None
                
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

                if files is not None:
                    fname = files[i]
                else:
                    fname = caxfiles[i]

                self.table.setCellWidget(i, 0, zone_cbox)
                item = QtGui.QTableWidgetItem(fname)
                self.table.setItem(i, 1, item)

    def get_versions(self):
        """Get list of available EGV versions"""

        path = "/home/prog/prod/tools/egv"
        if os.path.isdir(path):
            ver_list = os.listdir(path)
        else:
            ver_list = []
        return ver_list

    def run_egv(self):
        """Running EGV..."""
        
        if hasattr(self.parent, "bunlist"):
            reactor = self.parent.params.egv_reactor
            bundle = self.parent.bunlist[0]
            fuetype = bundle.data.fuetype
            if fuetype == "A10XM":
                fuel = "ATRIUM10XM"
            elif fuetype == "A10B":
                fuel = "ATRIUM10B"
            elif fuetype == "OPT2":
                fuel = "SVEA96OPTIMA2"
            elif fuetype == "OPT3":
                fuel = "SVEA96OPTIMA3"
            elif fuetype == "AT11":
                fuel = "ATRIUM11"
            else:
                print "Unknown fuel type"
                return

            zones = []
            for zone in self.parent.params.egv_zones:
                if zone == "Lower End":
                    zones.append("NEDRE ÄNDZON")
                elif zone == "Lower Active":
                    zones.append("NEDRE AKTIVZON")
                elif zone == "Upper Active":
                    zones.append("ÖVRE AKTIVZON")
                elif zone == "Upper End":
                    zones.append("ÖVRE ÄNDZON")
                else:
                    zones.append(None)

            files = self.parent.params.egv_files
            caxfiles = []
            for i in range(len(zones)):
                if zones[i]:
                    zone = zones[i]
                    fname = files[i]
                    fdict = {"ZON" : zone, "FIL" : fname}
                    caxfiles.append(fdict)

            version = self.parent.params.egv_version
            remove = not self.file_chbox.isChecked()
            egv_status, infolines = do_egv(reactor, fuel, caxfiles,
                                           egv_version=version, 
                                           verbose=False, remove=remove)
            
            msgBox = QtGui.QMessageBox()
            xpos = self.parent.pos().x() + self.parent.size().width() / 2
            ypos = self.parent.pos().y() + self.parent.size().height() / 2
            msgBox.move(0.8*xpos, ypos)

            # adjust size
            hspacer = QtGui.QSpacerItem(350, 0, QtGui.QSizePolicy.Minimum, 
                                        QtGui.QSizePolicy.Expanding)
            layout = msgBox.layout()
            layout.addItem(hspacer, layout.rowCount(), 0, 1, 
                           layout.columnCount())

            msgBox.setWindowTitle("EGV status")
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            
            if egv_status:
                msgBox.setText("EGV-run passed.\n\nCongratulations!")
                msgBox.setIcon(QtGui.QMessageBox.Information)
            else:
                if re.search("^\s*ERROR", infolines[0]):
                    msgBox.setText("EGV-run failed.")
                    infolines.append("Check EGV input options!")
                    infotext = "\n".join(infolines)
                    msgBox.setDetailedText(QtCore.QString.fromUtf8(infotext))
                    msgBox.setIcon(QtGui.QMessageBox.Critical)
                else:
                    sublines = []
                    for line in infolines:
                        parts = line.split(":")[1:]
                        s = ":".join(parts).strip()
                        sublines.append(s)
                    sublines.insert(0, "The following criteria were not met:")
                    infotext = "\n".join(sublines) 
                    msgBox.setText("EGV-run did not pass.\n\nSorry!")
                    msgBox.setDetailedText(QtCore.QString.fromUtf8(infotext))
                    msgBox.setIcon(QtGui.QMessageBox.Warning)
            status = msgBox.exec_()
