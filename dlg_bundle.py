from PyQt4 import QtGui, QtCore

class BundleDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Bundle")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.8*xpos, 0.9*ypos, 800, 300))

        self.table_view = QtGui.QTableView()
        #self.table_view.setShowGrid(False)
        self.table_view.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection)
        
        model = QtGui.QStandardItemModel(0, 3, self.table_view)
        selection_model = QtGui.QItemSelectionModel(model)
        self.table_view.setModel(model)
        self.table_view.setSelectionModel(selection_model)

        model.setHorizontalHeaderItem(0, QtGui.QStandardItem(
                "Height"))
        model.setHorizontalHeaderItem(1, QtGui.QStandardItem(
                "Height (BTF)"))
        model.setHorizontalHeaderItem(2, QtGui.QStandardItem(
                "Files"))

        verticalheader = self.table_view.verticalHeader()
        verticalheader.setResizeMode(QtGui.QHeaderView.Fixed)
        verticalheader.setDefaultSectionSize(25)

        flo = QtGui.QFormLayout()
        self.fuetype_cbox = QtGui.QComboBox()
        self.fue_list = ["OPT2", "OPT3", "A10B", "A10XM", "AT11"]
        self.fuetype_cbox.addItems(QtCore.QStringList(self.fue_list))

        #self.add_button = QtGui.QPushButton("Add...")
        #self.connect(self.add_button, QtCore.SIGNAL('clicked()'),
        #             self.add_file)

        #self.delete_button = QtGui.QPushButton("Delete")
        #self.connect(self.delete_button, QtCore.SIGNAL('clicked()'),
        #             self.delete_file)
        
        #print self.delete_button.size()
        #self.files_cbox = QtGui.QComboBox()
        #self.files_cbox.addItems(QtCore.QStringList([]))

        #self.nodes_cbox = QtGui.QComboBox()
        #self.nodes_cbox.addItems(QtCore.QStringList([]))

        #self.move_down_button = QtGui.QPushButton("Down")
        #self.move_up_button = QtGui.QPushButton("Up")
        #self.move_down_button.setMaximumWidth(40)
        #self.move_up_button.setMaximumWidth(40)
        #self.move_down_button.setFlat(True)

        #self.move_down_button.setSizeHint(40)
        #self.move_down_button.setSizePolicy(QtGui.QSizePolicy.Maximum,
        #                                    QtGui.QSizePolicy.Maximum)

        #move_hbox = QtGui.QHBoxLayout()
        #move_hbox.addWidget(self.move_down_button)
        #move_hbox.addWidget(self.move_up_button)

        flo.addRow("Fuel type:", self.fuetype_cbox)
        #flo.addRow("File:", self.add_button)
        #flo.addRow("File:", self.delete_button)
        #flo.addRow("Move:", self.move_up_button)
        #flo.addRow("Move:", move_hbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("Bundle")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        grid = QtGui.QGridLayout()
        grid.addWidget(groupbox, 0, 0)
        grid.addWidget(self.table_view, 0, 1)
        
        hbox = QtGui.QHBoxLayout()
        self.save_button = QtGui.QPushButton("Save As...")
        self.load_button = QtGui.QPushButton("Load...")
        self.import_button = QtGui.QPushButton("Import")
        self.cancel_button = QtGui.QPushButton("Cancel")
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.load_button)
        hbox.addStretch()
        hbox.addWidget(self.import_button)
        hbox.addWidget(self.cancel_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
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
        # Import default path from config file
        path_default = "."
        
        file_choices = "*.cax (*.cax)"
        caxfile = unicode(QtGui.QFileDialog.getOpenFileName(self,
                                                            'Select file',
                                                            path_default,
                                                            file_choices))
        if caxfile:
            i = self.table_view.model().rowCount()
            item0 = QtGui.QStandardItem("")
            item1 = QtGui.QStandardItem("")
            item2 = QtGui.QStandardItem(caxfile)
            self.table_view.model().setItem(i, 0, item0)
            self.table_view.model().setItem(i, 1, item1)
            self.table_view.model().setItem(i, 2, item2)
            self.table_view.resizeColumnToContents(2)

    def delete_file(self):
        row = self.table_view.selectionModel().currentIndex().row()
        self.table_view.model().takeRow(row)
        #self.table_view.removeRow(row)

    def load_bundle(self):
        """Load settings from project setup file"""
        self.parent.newProject()  # Create a bundle instance
        self.clear_all()
        #self.item_model.clear()
        caxfiles = self.parent.bunlist[0].data.caxfiles
        height = self.parent.bunlist[0].data.nodes
        
        for i, caxfile in enumerate(caxfiles):
            item0 = QtGui.QStandardItem(str(height[i]))
            item1 = QtGui.QStandardItem(str(height[i]))
            item2 = QtGui.QStandardItem(caxfile)
            self.table_view.model().setItem(i, 0, item0)
            self.table_view.model().setItem(i, 1, item1)
            self.table_view.model().setItem(i, 2, item2)
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
        print "move up"
        #print self.table_view.selectionModel().selectedRows()[0].row()
        print self.table_view.selectionModel().hasSelection()
        ci = self.table_view.selectionModel().currentIndex()  # QModelIndex
        #ci = self.selection_model.currentIndex()  # QModelIndex
        print ci.row()
        print self.table_view.model().rowCount()

    def move_down(self):
        """Swap rows in order to move selected data down one step"""
        if self.table_view.selectionModel().hasSelection():
            # get current index
            icur = self.table_view.selectionModel().currentIndex()
            irow = icur.row()
            icol = icur.column()
            if irow == self.table_view.model().rowCount() - 1:  # last row
                return
            mi = QtCore.QModelIndex()  # dummy model index
            rselect = self.table_view.selectionModel().isRowSelected(irow, mi)
            if rselect:  # entire row is selected
                ncols = self.table_view.model().columnCount()
                for c in range(ncols):
                    val1 = self.table_view.model().item(irow, c).text()
                    val2 = self.table_view.model().item(irow + 1, c).text()
                    item1 = QtGui.QStandardItem(val1)
                    item2 = QtGui.QStandardItem(val2)
                    self.table_view.model().setItem(irow, c, item2)
                    self.table_view.model().setItem(irow + 1, c, item1)
                    flag1 = QtGui.QItemSelectionModel.Select
                    flag2 = QtGui.QItemSelectionModel.Rows
                    idx = self.table_view.model().item(irow + 1, 2).index()
                    
                    self.table_view.selectionModel().select(idx, flag1 | flag2)
            else:
                val1 = self.table_view.model().item(irow, icol).text()
                val2 = self.table_view.model().item(irow + 1, icol).text()
                item1 = QtGui.QStandardItem(val1)
                item2 = QtGui.QStandardItem(val2)
                self.table_view.model().setItem(irow, icol, item2)
                self.table_view.model().setItem(irow + 1, icol, item1)
                flag1 = QtGui.QItemSelectionModel.Select
                idx = self.table_view.model().item(irow + 1, icol).index()
                self.table_view.selectionModel().select(idx, flag1)

            #sel_flag2 = QtGui.QItemSelectionModel.Rows
            #cmi = self.table_view.model().item(irow + 1, 2).index()
            #select = QtGui.QItemSelectionModel.Select
            self.table_view.selectionModel().setCurrentIndex(idx, flag1)
            #self.table_view.selectionModel().select(cmi, sel_flag | sel_flag2)

    def clear_all(self):
        """Remove all rows"""
        nrows = self.table_view.model().rowCount()
        self.table_view.model().removeRows(0, nrows)
        
