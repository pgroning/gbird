import os
import ConfigParser
from PyQt4 import QtGui, QtCore

class BundleDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)

        self.settings = QtCore.QSettings("greenbird")
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Bundle")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.8*xpos, 0.9*ypos, 800, 300))

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

        model.setHorizontalHeaderItem(0, QtGui.QStandardItem("Height"))
        model.setHorizontalHeaderItem(1, QtGui.QStandardItem("BTF"))
        model.setHorizontalHeaderItem(2, QtGui.QStandardItem("Files"))

        verticalheader = self.table_view.verticalHeader()
        verticalheader.setResizeMode(QtGui.QHeaderView.Fixed)
        verticalheader.setDefaultSectionSize(25)

        #flo = QtGui.QFormLayout()
        self.fuetype_cbox = QtGui.QComboBox()
        self.fue_list = ["OPT2", "OPT3", "A10B", "A10XM", "AT11"]
        self.fuetype_cbox.addItems(QtCore.QStringList(self.fue_list))

        self.save_button = QtGui.QPushButton("Save...")
        self.load_button = QtGui.QPushButton("Load...")

        flo = QtGui.QFormLayout()
        flo.addRow("Fuel:", self.fuetype_cbox)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(flo)
        #vbox.addWidget(self.fuetype_cbox)
        vbox.addStretch()
        vbox.addWidget(self.save_button)
        vbox.addWidget(self.load_button)

        groupbox = QtGui.QGroupBox()
        #groupbox.setTitle("Bundle")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(vbox)
        grid = QtGui.QGridLayout()
        grid.addWidget(groupbox, 0, 0)
        grid.addWidget(self.table_view, 0, 1)
        
        hbox = QtGui.QHBoxLayout()
        #self.save_button = QtGui.QPushButton("Save As...")
        #self.load_button = QtGui.QPushButton("Load...")
        self.import_button = QtGui.QPushButton("Import")
        self.cancel_button = QtGui.QPushButton("Cancel")
        #hbox.addWidget(self.save_button)
        #hbox.addWidget(self.load_button)
        hbox.addStretch()
        hbox.addWidget(self.import_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.save_button, QtCore.SIGNAL('clicked()'), 
                     self.save_bundle)
        self.connect(self.load_button, QtCore.SIGNAL('clicked()'), 
                     self.load_bundle)
        self.connect(self.import_button, QtCore.SIGNAL('clicked()'), 
                     self.import_data)

        add_icon = "icons/add-icon_32x32.png"
        addFileAction = QtGui.QAction(QtGui.QIcon(add_icon),
                                      'Add file', self)
        addFileAction.triggered.connect(self.add_file)
        
        delete_icon = "icons/delete3-icon_32x32.png"
        deleteFileAction = QtGui.QAction(QtGui.QIcon(delete_icon),
                                         'Delete file', self)
        deleteFileAction.triggered.connect(self.delete_file)

        arrow_up_icon = "icons/arrow-up-icon_32x32.png"
        moveUpAction = QtGui.QAction(QtGui.QIcon(arrow_up_icon),
                                     'Move selected file up', self)
        moveUpAction.triggered.connect(self.move_up)
        
        arrow_down_icon = "icons/arrow-down-icon_32x32.png"
        moveDownAction = QtGui.QAction(QtGui.QIcon(arrow_down_icon),
                                       'Move selected file down', self)
        moveDownAction.triggered.connect(self.move_down)

        toolbar = QtGui.QToolBar()
        toolbar.addAction(addFileAction)
        toolbar.addAction(deleteFileAction)
        toolbar.addAction(moveUpAction)
        toolbar.addAction(moveDownAction)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(toolbar)
        #vbox.addLayout(flo)
        vbox.addLayout(grid)
        #vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def action(self):
        self.close()

    def add_file(self):
        """Add single cax file to table"""

        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_default",
                                           QtCore.QString("")).toString()
        self.settings.endGroup()
        file_choices = "*.cax (*.cax)"
        dialog = QtGui.QFileDialog()
        #url = QtCore.QUrl()
        #dialog.setSidebarUrls(url)
        caxfile = unicode(dialog.getOpenFileName(self,
                                                 'Select file',
                                                 path_default,
                                                 file_choices))
        if caxfile:
            # Save default path to config file
            path = os.path.split(caxfile)[0]
            self.settings.beginGroup("PATH")
            self.settings.setValue("path_default", QtCore.QString(path))
            self.settings.endGroup()

            i = 0
            empty_item = QtGui.QStandardItem("")
            self.table_view.model().insertRow(i, empty_item)

            item0 = QtGui.QStandardItem("")
            item1 = QtGui.QStandardItem("")
            item2 = QtGui.QStandardItem(caxfile)
            self.table_view.model().setItem(i, 0, item0)
            self.table_view.model().setItem(i, 1, item1)
            self.table_view.model().setItem(i, 2, item2)
            self.table_view.resizeColumnToContents(2)

            nrows = self.table_view.model().rowCount()
            for i in range(nrows):
                vheader = QtGui.QStandardItem(str(nrows - i))
                self.table_view.model().setVerticalHeaderItem(i, vheader)

    def delete_file(self):
        row = self.table_view.selectionModel().currentIndex().row()
        self.table_view.model().takeRow(row)
        #self.table_view.removeRow(row)

    def update_table(self):
        """Load settings from project setup file"""
        #self.parent.newProject()  # Create a bundle instance
        self.clear_all()
        #self.item_model.clear()
        caxfiles = self.parent.bunlist[0].data.caxfiles
        height = self.parent.bunlist[0].data.nodes
        nsegs = len(caxfiles)
        
        for i, caxfile in enumerate(caxfiles):
            item0 = QtGui.QStandardItem(str(height[i]))
            item1 = QtGui.QStandardItem(str(height[i]))
            item2 = QtGui.QStandardItem(caxfile)
            self.table_view.model().setItem(i, 0, item0)
            self.table_view.model().setItem(i, 1, item1)
            self.table_view.model().setItem(i, 2, item2)
            vheader = QtGui.QStandardItem(str(nsegs - i))
            self.table_view.model().setVerticalHeaderItem(i, vheader)
            #self.table_view.setRowHeight(i, 25)
            #self.table_view.model().setRowHeight(i, 25)
            #item.setCheckable(True)
            #item.setCheckState(QtCore.Qt.Unchecked)
            #item.setCheckState(QtCore.Qt.Checked)
        #self.table_view.setColumnWidth(0, 80)
        #self.table_view.setColumnWidth(1, 80)
        self.table_view.resizeColumnToContents(2)
        
        fuetype = self.parent.bunlist[0].data.fuetype
        ifue = self.fue_list.index(fuetype)
        self.fuetype_cbox.setCurrentIndex(ifue)

    def import_data(self):
        """Import data from cax files"""
        self.close()
        self.parent.import_data()
        #self.close()
        
    def move_up(self):
        """Swap rows in order to move selected item up one step"""
        if self.table_view.selectionModel().hasSelection():
            # get current index
            icur = self.table_view.selectionModel().currentIndex()
            irow = icur.row()
            icol = icur.column()
            if irow == 0:  # first row. do nothing
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
            
    def move_down(self):
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

#            mi = QtCore.QModelIndex()  # dummy model index
#            rselect = self.table_view.selectionModel().isRowSelected(irow, mi)
#            if rselect:  # entire row is selected
#                ncols = self.table_view.model().columnCount()
#                for c in range(ncols):
#                    val1 = self.table_view.model().item(irow, c).text()
#                    val2 = self.table_view.model().item(irow + 1, c).text()
#                    item1 = QtGui.QStandardItem(val1)
#                    item2 = QtGui.QStandardItem(val2)
#                    self.table_view.model().setItem(irow, c, item2)
#                    self.table_view.model().setItem(irow + 1, c, item1)
#                    flag1 = QtGui.QItemSelectionModel.Select
#                    flag2 = QtGui.QItemSelectionModel.Rows
#                    idx = self.table_view.model().item(irow + 1, 2).index()
#                    
#                    self.table_view.selectionModel().select(idx, flag1 | flag2)
#            else:
#                val1 = self.table_view.model().item(irow, icol).text()
#                val2 = self.table_view.model().item(irow + 1, icol).text()
#                item1 = QtGui.QStandardItem(val1)
#                item2 = QtGui.QStandardItem(val2)
#                self.table_view.model().setItem(irow, icol, item2)
#                self.table_view.model().setItem(irow + 1, icol, item1)
#                flag1 = QtGui.QItemSelectionModel.Select
#                idx = self.table_view.model().item(irow + 1, icol).index()
#                self.table_view.selectionModel().select(idx, flag1)
#
#            #sel_flag2 = QtGui.QItemSelectionModel.Rows
#            #cmi = self.table_view.model().item(irow + 1, 2).index()
#            #select = QtGui.QItemSelectionModel.Select
#            self.table_view.selectionModel().setCurrentIndex(idx, flag1)
#            #self.table_view.selectionModel().select(cmi, sel_flag | sel_flag2)

    def clear_all(self):
        """Remove all rows"""
        nrows = self.table_view.model().rowCount()
        self.table_view.model().removeRows(0, nrows)

    def load_bundle(self):
        """Reading project setup file"""

        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_default",
                                           QtCore.QString("")).toString()
        self.settings.endGroup()
        file_choices = "*.pro (*.pro)"
        filename = unicode(QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                             path_default,
                                                             file_choices))
        if filename:
            # Read project data and create bundle instance
            self.parent.read_pro(filename)
            self.update_table()

    def save_bundle(self):
        """Save data to project file"""
        
        filename = self.select_write_file()
        if not filename:
            return
        
        config = ConfigParser.SafeConfigParser()
        config.add_section("Bundle")
        fuetype = str(self.fuetype_cbox.currentText())
        config.set("Bundle", "fuel", fuetype)

        nrows = self.table_view.model().rowCount()
        file_list = []
        height_list = []
        btf_list = []
        for irow in range(nrows):
            height_item = self.table_view.model().item(irow, 0)
            btf_item = self.table_view.model().item(irow, 1)
            file_item = self.table_view.model().item(irow, 2)
            height_list.append(str(height_item.text()))
            if str(btf_item.text()):
                btf_list.append(str(btf_item.text()))
            else:
                btf_list.append("-")
            file_list.append(str(file_item.text()))
        
        file_str = "\n".join(file_list)
        config.set("Bundle", "files", file_str)

        height_str = "\n".join(height_list)
        config.set("Bundle", "height", height_str)

        config.add_section("BTF")
        btf_str = "\n".join(btf_list)
        config.set("BTF", "height", btf_str)
        
        with open(filename, "wb") as configfile:
            config.write(configfile)

    def select_write_file(self):
        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_default",
                                           QtCore.QString("")).toString()
        self.settings.endGroup()
        file_choices = "*.pro (*.pro)"
        filename = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save file',
                                                             path_default,
                                                             file_choices))
        if filename:
            # Save default path to config file
            path = os.path.split(filename)[0]
            self.settings.beginGroup("PATH")
            self.settings.setValue("path_default", QtCore.QString(path))
            self.settings.endGroup()
            
        return filename
    
