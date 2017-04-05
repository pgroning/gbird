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

        self.table_view = QtGui.QTableView()
        model = QtGui.QStandardItemModel(0, 2, self.table_view)
        selection_model = QtGui.QItemSelectionModel(model)
        self.table_view.setModel(model)
        self.table_view.setSelectionModel(selection_model)

        model.setHorizontalHeaderItem(0, QtGui.QStandardItem("Zone"))
        model.setHorizontalHeaderItem(1, QtGui.QStandardItem("Files"))

        self.add_row()
        
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
        vbox.addWidget(self.table_view)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def ok_action(self):
        self.close()
        
    def add_row(self):
        """add row to table"""
        i = 0
        empty_item = QtGui.QStandardItem("")
        self.table_view.model().insertRow(i, empty_item)

        #item0 
        #self.table_view.model().setItem(i, 0, item0)
