from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
import os
import numpy as np
from PyQt4 import QtGui, QtCore

from pin import FuePin


class Data(object):
    """A class that can be used to organize data in its attributes"""
    pass

    
class DensItemDelegate(QtGui.QStyledItemDelegate):
    """Class that is used to validate user input"""
    
    def createEditor(self, parent, option, index):
        line_edit = QtGui.QLineEdit(parent)
        line_edit.setMaxLength(6)
        validator = QtGui.QDoubleValidator(0, 99.999, 3, self)
        line_edit.setValidator(validator)
        return line_edit

    
class EnrItemDelegate(QtGui.QStyledItemDelegate):
    """Class that is used to validate user input"""
    
    def createEditor(self, parent, option, index):
        line_edit = QtGui.QLineEdit(parent)
        line_edit.setMaxLength(4)
        validator = QtGui.QDoubleValidator(0, 9.99, 2, self)
        line_edit.setValidator(validator)
        return line_edit
    

class EnrichmentDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)

        path = os.path.realpath(__file__)
        self.appdir = os.path.split(path)[0] + os.sep

        self.settings = QtCore.QSettings("greenbird")
        self.parent = parent
        self.setup()
        self.set_table_data()
        self.ok = False  # True if Ok button is clicked

    def setup(self):
        self.setWindowTitle("Edit enrichments")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.5*xpos, 0.8*ypos, 350, 400))

        self.table_view = QtGui.QTableView()
        self.table_view.setSortingEnabled(True)
        #self.table_view.setShowGrid(False)
        self.table_view.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        #self.table_view.setSelectionMode(
        #    QtGui.QAbstractItemView.SingleSelection)
        #self.table_view.setDragDropMode(
        #    QtGui.QAbstractItemView.DragDrop)

        # Put constraints on user input
        self.dens_delegate = DensItemDelegate()
        self.table_view.setItemDelegateForColumn(1, self.dens_delegate)
        self.enr_delegate = EnrItemDelegate()
        self.table_view.setItemDelegateForColumn(2, self.enr_delegate)
        self.table_view.setItemDelegateForColumn(3, self.enr_delegate)

        model = QtGui.QStandardItemModel(0, 4, self.table_view)
        selection_model = QtGui.QItemSelectionModel(model)
        self.table_view.setModel(model)
        self.table_view.setSelectionModel(selection_model)

        model.setHorizontalHeaderItem(0, QtGui.QStandardItem("Index"))
        model.setHorizontalHeaderItem(1, QtGui.QStandardItem("Density"))
        model.setHorizontalHeaderItem(2, QtGui.QStandardItem("% U-235"))
        model.setHorizontalHeaderItem(3, QtGui.QStandardItem("% Gd"))

        self.table_view.setColumnHidden(0, True)  # do not display index column
        
        horizontalheader = self.table_view.horizontalHeader()
        horizontalheader.setResizeMode(QtGui.QHeaderView.Stretch)
        #horizontalheader.setResizeMode(2, QtGui.QHeaderView.Stretch)

        verticalheader = self.table_view.verticalHeader()
        verticalheader.setResizeMode(QtGui.QHeaderView.Fixed)
        verticalheader.setDefaultSectionSize(25)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.table_view, 0, 0)
        
        hbox = QtGui.QHBoxLayout()
        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")
        self.reset_button = QtGui.QPushButton("Reset")
        hbox.addWidget(self.reset_button)
        hbox.addStretch()
        hbox.addWidget(self.cancel_button)
        hbox.addWidget(self.ok_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), 
                     self.ok_action)
        self.connect(self.reset_button, QtCore.SIGNAL('clicked()'), 
                     self.reset_action)

        add_icon = self.appdir + "icons/add-icon_32x32.png"
        addRowAction = QtGui.QAction(QtGui.QIcon(add_icon),
                                      'Add row...', self)
        addRowAction.triggered.connect(self.add_row_action)
        
        delete_icon = self.appdir + "icons/delete3-icon_32x32.png"
        deleteRowAction = QtGui.QAction(QtGui.QIcon(delete_icon),
                                         'Delete row', self)
        deleteRowAction.triggered.connect(self.delete_row_action)

        arrow_up_icon = self.appdir + "icons/arrow-up-icon_32x32.png"
        moveUpAction = QtGui.QAction(QtGui.QIcon(arrow_up_icon),
                                     'Move selected cells up', self)
        moveUpAction.triggered.connect(self.move_up_action)
        
        arrow_down_icon = self.appdir + "icons/arrow-down-icon_32x32.png"
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

    def add_row_action(self):
        """Add single cax file to table cell"""

        i = self.table_view.model().rowCount()
        #icur = self.table_view.selectionModel().currentIndex()
        #i = icur.row() + 1
        empty_item = QtGui.QStandardItem("")
        self.table_view.model().insertRow(i, empty_item)

        index = '{0:d}'.format(i)
        item0 = QtGui.QStandardItem(index)
        item1 = QtGui.QStandardItem("0.000")
        item2 = QtGui.QStandardItem("0.00")
        item3 = QtGui.QStandardItem("0.00")
        self.table_view.model().setItem(i, 0, item0)
        self.table_view.model().setItem(i, 1, item1)
        self.table_view.model().setItem(i, 2, item2)
        self.table_view.model().setItem(i, 3, item3)

        #self.table_view.clearSelection()
        self.table_view.selectionModel().clearSelection()
        select = QtGui.QItemSelectionModel.Select
        noupdate = QtGui.QItemSelectionModel.NoUpdate
        ncols = self.table_view.model().columnCount()
        for j in range(ncols):
            index = self.table_view.model().item(i, j).index()
            self.table_view.selectionModel().select(index, select)
        self.table_view.selectionModel().setCurrentIndex(index, noupdate)

    def delete_row_action(self):
        i = self.table_view.selectionModel().currentIndex().row()
        self.table_view.model().takeRow(i)
        #self.table_view.removeRow(row)

        if i >= self.table_view.model().rowCount():
            i = self.table_view.model().rowCount() - 1
        
        # Update indicies
        nrows = self.table_view.model().rowCount()
        for row in range(i, nrows):
            index = '{0:d}'.format(row)
            index_item = QtGui.QStandardItem(index)
            self.table_view.model().setItem(row, 0, index_item)

        # Update row selection
        select = QtGui.QItemSelectionModel.Select
        noupdate = QtGui.QItemSelectionModel.NoUpdate
        ncols = self.table_view.model().columnCount()
        for j in range(ncols):
            index = self.table_view.model().item(i, j).index()
            self.table_view.selectionModel().select(index, select)
        self.table_view.selectionModel().setCurrentIndex(index, noupdate)

    def reset_action(self):
        """reset all cells"""
        self.set_table_data()
        #msgBox = QtGui.QMessageBox()
        #status = msgBox.information(self, "Reset",
        #                            "Continue?",
        #                            QtGui.QMessageBox.Yes |
        #                            QtGui.QMessageBox.Cancel)
        #if status == QtGui.QMessageBox.Yes:
        #    self.set_table_data()
        
    def set_table_data(self):
        """Set table cell data"""
        
        self.clear_all()

        iseg = int(self.parent.case_cbox.currentIndex())
        enrpinlist = self.parent.enrpinlist[iseg]
        
        for i, pin in enumerate(enrpinlist):
            index = '{0:d}'.format(i)
            index_item = QtGui.QStandardItem(index)
            
            dens = '{0:.3f}'.format(pin.DENS)
            dens_item = QtGui.QStandardItem(dens)

            enr = '{0:.2f}'.format(pin.ENR)
            enr_item = QtGui.QStandardItem(enr)

            ba = 0 if np.isnan(pin.BA) else pin.BA
            ba = '{0:.2f}'.format(ba)
            ba_item = QtGui.QStandardItem(ba)
            
            self.table_view.model().setItem(i, 0, index_item)
            self.table_view.model().setItem(i, 1, dens_item)
            self.table_view.model().setItem(i, 2, enr_item)
            self.table_view.model().setItem(i, 3, ba_item)

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
        """Update enrpinlist"""

        msgBox = QtGui.QMessageBox()
        status = msgBox.information(self, "Update",
                                    "Continue?",
                                    QtGui.QMessageBox.Yes |
                                    QtGui.QMessageBox.Cancel)
        if status == QtGui.QMessageBox.Cancel:
            return

        self.get_table_data()

        iseg = int(self.parent.case_cbox.currentIndex())

        # Create new enrpin list
        enrpinlist = []
        nrows = len(self.data.enr)
        cmap = self.parent.get_colormap(nrows)
        for i in range(nrows):
            enrpin = FuePin(self.parent.axes)
            enrpin.facecolor = cmap[i]
            enrpin.DENS = self.data.dens[i]
            enrpin.ENR = self.data.enr[i]
            if self.data.ba[i] < 0.00001:
                enrpin.BA = np.nan
                enrpin.BAindex = np.nan
            else:
                enrpin.BA = self.data.ba[i]
                enrpin.BAindex = 7300  # Gd
            enrpinlist.append(enrpin)

        self.parent.enrpinlist[iseg] = enrpinlist

        # Update fue pins
        index = self.data.index
        isort = [i for i, e in sorted(enumerate(index), key=lambda x:x[1])]
        for pin in self.parent.pinobjects[iseg]:
            i = pin.LFU - 1
            if i > max(index):
                i = max(index)
            j = isort[i]
            pin.LFU = j + 1
            pin.ENR = enrpinlist[j].ENR
            pin.BA = enrpinlist[j].BA

        self.close()
        self.ok = True

    def get_table_data(self):
        """Get data from dialog widgets"""

        index_list = []
        dens_list = []
        enr_list = []
        ba_list = []
        nrows = self.table_view.model().rowCount()
        for i in range(nrows):
            index_item = self.table_view.model().item(i, 0)
            index_list.append(int(index_item.text()))
            dens_item = self.table_view.model().item(i, 1)
            dens_list.append(float(dens_item.text()))
            enr_item = self.table_view.model().item(i, 2)
            enr_list.append(float(enr_item.text()))
            ba_item = self.table_view.model().item(i, 3)
            ba_list.append(float(ba_item.text()))

        self.data = Data()
        self.data.index = index_list
        self.data.dens = dens_list
        self.data.enr = enr_list
        self.data.ba = ba_list
                
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

