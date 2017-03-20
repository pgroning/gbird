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

        self.listview = QtGui.QListView()
        #self.listview.setModelColumn(1)
        #self.listview.setWindowTitle('Example List')
        #self.listview.setMinimumSize(600, 400)
        self.listmodel = QtGui.QStandardItemModel(self.listview)
        self.selectmodel = QtGui.QItemSelectionModel(self.listmodel)
        self.listview.setModel(self.listmodel)

        self.listwidget = QtGui.QListWidget()
        #lview.setAcceptDrops(True)
        
        flo = QtGui.QFormLayout()
        self.fuetype_cbox = QtGui.QComboBox()
        self.fue_list = ["OPT2", "OPT3", "A10B", "A10XM", "AT11"]
        self.fuetype_cbox.addItems(QtCore.QStringList(self.fue_list))

        self.add_button = QtGui.QPushButton("Add...")
        self.connect(self.add_button, QtCore.SIGNAL('clicked()'),
                     self.add_file)

        self.delete_button = QtGui.QPushButton("Delete")
        self.connect(self.delete_button, QtCore.SIGNAL('clicked()'),
                     self.delete_file)
        
        #print self.delete_button.size()
        #self.files_cbox = QtGui.QComboBox()
        #self.files_cbox.addItems(QtCore.QStringList([]))

        #self.nodes_cbox = QtGui.QComboBox()
        #self.nodes_cbox.addItems(QtCore.QStringList([]))

        self.move_down_button = QtGui.QPushButton("Down")
        self.move_up_button = QtGui.QPushButton("Up")
        self.move_down_button.setMaximumWidth(40)
        self.move_up_button.setMaximumWidth(40)
        #self.move_down_button.setFlat(True)

        #self.move_down_button.setSizeHint(40)
        #self.move_down_button.setSizePolicy(QtGui.QSizePolicy.Maximum,
        #                                    QtGui.QSizePolicy.Maximum)

        move_hbox = QtGui.QHBoxLayout()
        move_hbox.addWidget(self.move_down_button)
        move_hbox.addWidget(self.move_up_button)

        flo.addRow("Fuel type:", self.fuetype_cbox)
        flo.addRow("File:", self.add_button)
        flo.addRow("File:", self.delete_button)
        #flo.addRow("Move:", self.move_up_button)
        flo.addRow("Move:", move_hbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("Bundle")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        grid = QtGui.QGridLayout()
        grid.addWidget(groupbox, 0, 0)
        grid.addWidget(self.listwidget, 0, 1)
        grid.addWidget(self.listview, 0, 2)
        
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

        arrow_down_icon = "icons/arrow-down-icon_32x32.png"
        moveDownAction = QtGui.QAction(QtGui.QIcon(arrow_down_icon),
                                       'Move selected file down', self)

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
        filename = unicode(QtGui.QFileDialog.getOpenFileName(self,
                                                             'Select file',
                                                             path_default,
                                                             file_choices))
        if filename:
            self.listwidget.addItem(filename)

    def delete_file(self):
        #row = self.listwidget.currentRow()
        #self.listwidget.takeItem(row)
        print self.selectmodel.currentIndex()
        row = 1
        self.listmodel.takeRow(row)

    def load_bundle(self):
        """Load settings from project setup file"""
        self.parent.newProject()  # Create a bundle instance
        self.listmodel.clear()
        caxfiles = self.parent.bunlist[0].data.caxfiles
        #self.listwidget.addItems(QtCore.QStringList(caxfiles))

        for caxfile in caxfiles:
            item = QtGui.QStandardItem(caxfile)
            item.setCheckable(True)
            #item.setCheckState(QtCore.Qt.Unchecked)
            item.setCheckState(QtCore.Qt.Checked)
            self.listmodel.appendRow(item)

        fuetype = self.parent.bunlist[0].data.fuetype
        ifue = self.fue_list.index(fuetype)
        self.fuetype_cbox.setCurrentIndex(ifue)

    def import_data(self):
        """Import data from cax files"""
        self.close()
        self.parent.import_data()
        #self.close()
        
