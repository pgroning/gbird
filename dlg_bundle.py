from PyQt4 import QtGui, QtCore

class BundleDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("New bundle")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.8*xpos, 0.9*ypos, 800, 300))

        #lview = QtGui.QListView()
        self.listwidget = QtGui.QListWidget()
        #lview.setAcceptDrops(True)
        
        flo = QtGui.QFormLayout()
        self.fuetype_cbox = QtGui.QComboBox()
        fue_list = ["OPT2", "OPT3", "A10B", "A10XM", "AT11"]
        self.fuetype_cbox.addItems(QtCore.QStringList(fue_list))

        self.add_button = QtGui.QPushButton("Add...")
        self.connect(self.add_button, QtCore.SIGNAL('clicked()'),
                     self.add_file)

        self.delete_button = QtGui.QPushButton("Delete")
        self.connect(self.delete_button, QtCore.SIGNAL('clicked()'),
                     self.delete_file)
        
        #self.files_cbox = QtGui.QComboBox()
        #self.files_cbox.addItems(QtCore.QStringList([]))

        self.nodes_cbox = QtGui.QComboBox()
        self.nodes_cbox.addItems(QtCore.QStringList([]))

        flo.addRow("Fuel type:", self.fuetype_cbox)
        flo.addRow("Files:", self.add_button)
        flo.addRow("Files:", self.delete_button)
        flo.addRow("Nodes:", self.nodes_cbox)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("Bundle")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        grid = QtGui.QGridLayout()
        grid.addWidget(groupbox, 0, 0)
        grid.addWidget(self.listwidget, 0, 1)
        
        hbox = QtGui.QHBoxLayout()
        self.save_button = QtGui.QPushButton("Save As...")
        self.load_button = QtGui.QPushButton("Load...")
        self.ok_button = QtGui.QPushButton("Import")
        self.cancel_button = QtGui.QPushButton("Cancel")
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.load_button)
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
        row = self.listwidget.currentRow()
        self.listwidget.takeItem(row)
