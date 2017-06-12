from PyQt4 import QtGui, QtCore


class Ui_MainWindow(object):
    """Creates ui widgets in main frame"""

    def __init__(self, parent=None):
        #super(Ui, self).__init__(parent)
        #self.parent = parent
        pass

    def setup(self, parent):
        self.create_statusbar(parent)

    def create_statusbar(self, parent):
        self.status_text = QtGui.QLabel("Main window")
        parent.statusBar().addWidget(self.status_text, 1)


