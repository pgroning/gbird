from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
import os
import numpy as np
from PyQt4 import QtGui, QtCore


class Data(object):
    """A class that can be used to organize data in its attributes"""
    pass


class EnrichmentDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)

        self.settings = QtCore.QSettings("greenbird")
        self.parent = parent
        self.setup()
        self.set_table_data()

    def setup(self):
        self.setWindowTitle("Edit enrichments")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.5*xpos, 0.8*ypos, 300, 300))

        self.table_view = QtGui.QTableView()
        #self.table_view.setShowGrid(False)
        #self.table_view.setSelectionBehavior(
        #    QtGui.QAbstractItemView.SelectRows)
        #self.table_view.setSelectionMode(
        #    QtGui.QAbstractItemView.SingleSelection)
        #self.table_view.setDragDropMode(
        #    QtGui.QAbstractItemView.DragDrop)
        
        model = QtGui.QStandardItemModel(0, 3, self.table_view)
        selection_model = QtGui.QItemSelectionModel(model)
        self.table_view.setModel(model)
        self.table_view.setSelectionModel(selection_model)

        model.setHorizontalHeaderItem(0, QtGui.QStandardItem("Density"))
        model.setHorizontalHeaderItem(1, QtGui.QStandardItem("U-235 (w/o)"))
        model.setHorizontalHeaderItem(2, QtGui.QStandardItem("Gd"))

        horizontalheader = self.table_view.horizontalHeader()
        horizontalheader.setResizeMode(QtGui.QHeaderView.Stretch)
        #horizontalheader.setResizeMode(2, QtGui.QHeaderView.Stretch)

        verticalheader = self.table_view.verticalHeader()
        verticalheader.setResizeMode(QtGui.QHeaderView.Fixed)
        verticalheader.setDefaultSectionSize(25)

        self.fuetype_cbox = QtGui.QComboBox()
        self.fue_list = ["OPT2", "OPT3", "A10B", "A10XM", "AT11"]
        self.fuetype_cbox.addItems(QtCore.QStringList(self.fue_list))

        self.content_cbox = QtGui.QComboBox()
        self.content_list = ["filt.", "unfilt."]
        self.content_cbox.addItems(QtCore.QStringList(self.content_list))

        #self.height_cbox = QtGui.QComboBox()
        #self.height_list = ["zone", "total"]
        #self.height_cbox.addItems(QtCore.QStringList(self.height_list))

        #self.save_button = QtGui.QPushButton("Save...")
        #self.load_button = QtGui.QPushButton("Load...")

        #flo = QtGui.QFormLayout()
        #flo.addRow("Fuel:", self.fuetype_cbox)
        #flo.addRow("Content:", self.content_cbox)
        #flo.addRow("Height:", self.height_cbox)

        vbox = QtGui.QVBoxLayout()
        #vbox.addLayout(flo)
        #vbox.addWidget(self.fuetype_cbox)
        #vbox.addStretch()
        #vbox.addWidget(self.load_button)
        #vbox.addWidget(self.save_button)

        groupbox = QtGui.QGroupBox()
        #groupbox.setTitle("Bundle")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(vbox)
        grid = QtGui.QGridLayout()
        #grid.addWidget(groupbox, 0, 0)
        grid.addWidget(self.table_view, 0, 0)
        
        hbox = QtGui.QHBoxLayout()
        #self.save_button = QtGui.QPushButton("Save As...")
        #self.load_button = QtGui.QPushButton("Load...")
        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")
        #hbox.addWidget(self.save_button)
        #hbox.addWidget(self.load_button)
        hbox.addStretch()
        hbox.addWidget(self.ok_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        #self.connect(self.save_button, QtCore.SIGNAL('clicked()'), 
        #             self.save_bundle_action)
        #self.connect(self.load_button, QtCore.SIGNAL('clicked()'), 
        #             self.load_bundle_action)
        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), 
                     self.ok_action)

        add_icon = "icons/add-icon_32x32.png"
        addRowAction = QtGui.QAction(QtGui.QIcon(add_icon),
                                      'Add row...', self)
        addRowAction.triggered.connect(self.add_row_action)
        
        delete_icon = "icons/delete3-icon_32x32.png"
        deleteRowAction = QtGui.QAction(QtGui.QIcon(delete_icon),
                                         'Delete row', self)
        deleteRowAction.triggered.connect(self.delete_row_action)

        arrow_up_icon = "icons/arrow-up-icon_32x32.png"
        moveUpAction = QtGui.QAction(QtGui.QIcon(arrow_up_icon),
                                     'Move selected cells up', self)
        moveUpAction.triggered.connect(self.move_up_action)
        
        arrow_down_icon = "icons/arrow-down-icon_32x32.png"
        moveDownAction = QtGui.QAction(QtGui.QIcon(arrow_down_icon),
                                       'Move selected cells down', self)
        moveDownAction.triggered.connect(self.move_down_action)

        toolbar = QtGui.QToolBar()
        toolbar.addAction(addRowAction)
        toolbar.addAction(deleteRowAction)
        toolbar.addAction(moveUpAction)
        toolbar.addAction(moveDownAction)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(toolbar)
        #vbox.addLayout(flo)
        vbox.addLayout(grid)
        #vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    #def action(self):
    #    self.close()

    def add_row_action(self):
        """Add single cax file to table cell"""

        #caxfile = self.select_read_file(file_choices="*.cax (*.cax)")
        #if not caxfile:
        #    return

        #i = self.table_view.model().rowCount()
        icur = self.table_view.selectionModel().currentIndex()
        i = icur.row() + 1
        empty_item = QtGui.QStandardItem("")
        self.table_view.model().insertRow(i, empty_item)
        
        item0 = QtGui.QStandardItem("")
        item1 = QtGui.QStandardItem("")
        item2 = QtGui.QStandardItem("")
        self.table_view.model().setItem(i, 0, item0)
        self.table_view.model().setItem(i, 1, item1)
        self.table_view.model().setItem(i, 2, item2)
        #self.table_view.resizeColumnToContents(2)
        
        #nrows = self.table_view.model().rowCount()
        #for i in range(nrows):
        #    vheader = QtGui.QStandardItem(str(nrows - i))
        #    self.table_view.model().setVerticalHeaderItem(i, vheader)

    def delete_row_action(self):
        row = self.table_view.selectionModel().currentIndex().row()
        self.table_view.model().takeRow(row)
        #self.table_view.removeRow(row)

    def set_table_data(self):
        """Set table cell data"""
        
        self.clear_all()

        FUE = np.array([[1, 10.549, 0.71, 0.00],[2, 10.549, 2.20, 0.00]])
        nrows = FUE.shape[0]
        
        for i in range(nrows):
            #index = '{0:d}'.format(int(FUE[i, 0]))
            #index_item = QtGui.QStandardItem(index)
            
            dens = '{0:.3f}'.format(FUE[i, 1])
            dens_item = QtGui.QStandardItem(dens)

            enr = '{0:.2f}'.format(FUE[i, 2])
            enr_item = QtGui.QStandardItem(enr)

            ba = '{0:.2f}'.format(FUE[i, 3])
            ba_item = QtGui.QStandardItem(ba)
            
            #self.table_view.model().setItem(i, 0, index_item)
            self.table_view.model().setItem(i, 0, dens_item)
            self.table_view.model().setItem(i, 1, enr_item)
            self.table_view.model().setItem(i, 2, ba_item)

            #vheader = QtGui.QStandardItem(str(nfiles - i))
            #self.table_view.model().setVerticalHeaderItem(i, vheader)

            #self.table_view.setRowHeight(i, 25)
            #self.table_view.model().setRowHeight(i, 25)
            #item.setCheckable(True)
            #item.setCheckState(QtCore.Qt.Unchecked)
            #item.setCheckState(QtCore.Qt.Checked)
        #self.table_view.setColumnWidth(0, 80)
        #self.table_view.setColumnWidth(1, 80)
        #self.table_view.resizeColumnToContents(2)
        
        #fuetype = self.parent.bunlist[0].data.fuetype
        #fuetype = self.data.fuetype
        #ifue = self.fue_list.index(fuetype)
        #self.fuetype_cbox.setCurrentIndex(ifue)

        #if content == "filtered":
        #self.content_cbox.setCurrentIndex(0)
        #else:
        #    self.content_cbox.setCurrentIndex(1)

        #if self.data.height == "zone":
        #    self.height_cbox.setCurrentIndex(0)
        #else:
        #    self.height_cbox.setCurrentIndex(1)

    def ok_action(self):
        """Import data from cax files"""

        #self.get_table_data()
        #self.parent.init_bundle()
        #bundle = self.parent.bunlist[0]
        #bundle.data.fuetype = self.data.fuetype
        #bundle.data.caxfiles = self.data.caxfiles

        #if self.height_cbox.currentIndex() == 0:
        #bundle.data.nodes = self.data.nodes
        #bundle.data.btf_nodes = self.data.btf_nodes
        #elif self.height_cbox.currentIndex() == 1:  # convert to zone height
        #    bundle.data.nodes = self.zone_height(self.data.nodes)
        #    bundle.data.btf_nodes = self.zone_height(self.data.btf_nodes)
        
        #bundle.data.content = self.data.content
        self.close()
        #self.parent.import_data()

    def get_table_data(self):
        """Get data from dialog widgets"""
                
        fuetype = str(self.fuetype_cbox.currentText())
        if self.content_cbox.currentIndex() == 0:
            content = "filtered"
        else:
            content = "unfiltered"

        #if self.height_cbox.currentIndex() == 0:
        #    height = "zone"
        #else:
        #    height = "total"

        node_list = []
        btf_list = []
        file_list = []
        nrows = self.table_view.model().rowCount()
        for i in range(nrows):
            node_item = self.table_view.model().item(i, 0)
            #node_list.append(int(node_item.text()))
            node_list.append(float(node_item.text()))
            btf_item = self.table_view.model().item(i, 1)
            #btf_list.append(int(btf_item.text()))
            btf_list.append(float(btf_item.text()))
            file_item = self.table_view.model().item(i, 2)
            file_list.append(str(file_item.text()))
        node_list.reverse()
        btf_list.reverse()
        file_list.reverse()
        
        self.data = Data()
        self.data.fuetype = fuetype
        self.data.content = content
        self.data.nodes = node_list
        #self.data.height = height
        self.data.btf_nodes = btf_list
        self.data.caxfiles = file_list
                
    def move_up_action(self):
        """Swap rows in order to move selected item up one step"""
        if self.table_view.selectionModel().hasSelection():
            # get current index
            icur = self.table_view.selectionModel().currentIndex()
            irow = icur.row()
            icol = icur.column()
            if irow == 0:  # if first row do nothing
                return

            select_items = []
            ncols = self.table_view.model().columnCount()
            for c in range(ncols):
                item1 = self.table_view.model().item(irow, c)
                item2 = self.table_view.model().item(irow - 1, c)
                idx = item1.index()
                if self.table_view.selectionModel().isSelected(idx):
                    t1 = item1.text()
                    t2 = item2.text()
                    i1 = QtGui.QStandardItem(t1)
                    i2 = QtGui.QStandardItem(t2)
                    self.table_view.model().setItem(irow, c, i2)
                    self.table_view.model().setItem(irow - 1, c, i1)
                    item = self.table_view.model().item(irow - 1, c)
                    select_items.append(item)
            
            select = QtGui.QItemSelectionModel.Select
            noupdate = QtGui.QItemSelectionModel.NoUpdate
            for item in select_items:
                idx = item.index()
                self.table_view.selectionModel().select(idx, select)
            self.table_view.selectionModel().setCurrentIndex(idx, noupdate)
            
    def move_down_action(self):
        """Swap rows in order to move selected data down one step"""

        if self.table_view.selectionModel().hasSelection():
            # get current index
            icur = self.table_view.selectionModel().currentIndex()
            irow = icur.row()
            icol = icur.column()
            if irow == self.table_view.model().rowCount() - 1:  # last row
                return

            select_items = []
            ncols = self.table_view.model().columnCount()
            for c in range(ncols):
                item1 = self.table_view.model().item(irow, c)
                item2 = self.table_view.model().item(irow + 1, c)
                idx = item1.index()
                if self.table_view.selectionModel().isSelected(idx):
                    t1 = item1.text()
                    t2 = item2.text()
                    i1 = QtGui.QStandardItem(t1)
                    i2 = QtGui.QStandardItem(t2)
                    self.table_view.model().setItem(irow, c, i2)
                    self.table_view.model().setItem(irow + 1, c, i1)
                    item = self.table_view.model().item(irow + 1, c)
                    select_items.append(item)
            
            select = QtGui.QItemSelectionModel.Select
            noupdate = QtGui.QItemSelectionModel.NoUpdate
            for item in select_items:
                idx = item.index()
                self.table_view.selectionModel().select(idx, select)
            self.table_view.selectionModel().setCurrentIndex(idx, noupdate)

    def clear_all(self):
        """Remove all rows"""
 
        nrows = self.table_view.model().rowCount()
        self.table_view.model().removeRows(0, nrows)

