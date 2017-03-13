from PyQt4 import QtGui, QtCore

class CasDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent

        self.setWindowTitle("CASMO settings")
        xpos = parent.pos().x() + parent.size().width() / 2
        ypos = parent.pos().y() + parent.size().height() / 2
        self.setGeometry(QtCore.QRect(xpos, ypos, 150, 120))

        flo = QtGui.QFormLayout()
        self.text1 = QtGui.QLineEdit("%.2f" % 3.14)
        self.text2 = QtGui.QLineEdit("%.2f" % 3.14)
        flo.addRow("Maximum depletion:", self.text1)
        flo.addRow("Depletion threshold:", self.text2)

        hbox = QtGui.QHBoxLayout()
        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")
        hbox.addWidget(self.cancel_button)
        hbox.addWidget(self.ok_button)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), self.action)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(flo)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def action(self):
        self.close()
