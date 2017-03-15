from PyQt4 import QtGui, QtCore

class ReportDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Fuel report")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(0.8*xpos, 0.9*ypos, 600, 400))

        self.report = QtGui.QTextEdit()
        self.report.setReadOnly(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        self.report.setSizePolicy(sizePolicy)
        
        self.text_insert()

        hbox = QtGui.QHBoxLayout()
        self.save_button = QtGui.QPushButton("Save As...")
        self.close_button = QtGui.QPushButton("Close")
        hbox.addWidget(self.save_button)
        hbox.addStretch()
        hbox.addWidget(self.close_button)
        self.connect(self.close_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.save_button, QtCore.SIGNAL('clicked()'), 
                     self.save_action)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.report)
        #vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def action(self):
        self.close()

    def save_action(self):
        pass

    def text_insert(self):

        ibundle = self.parent.ibundle
        iseg = int(self.parent.case_cbox.currentIndex())
        bundle = self.parent.bunlist[ibundle]
        segdata = bundle.segments[iseg].data

        self.report.setFontPointSize(14)
        # Font Weight:Light=25, Normal=50, Demibold=63, Bold=75, Black=87
        self.report.setFontWeight(75)
        self.report.setText("File: ")
        self.report.moveCursor(QtGui.QTextCursor.End)
        self.report.setFontWeight(50)
        self.report.insertPlainText(segdata.caxfile)

        self.report.setFontWeight(75)
        self.report.append("Fuel type: ")
        self.report.moveCursor(QtGui.QTextCursor.End)
        self.report.setFontWeight(50)
        self.report.insertPlainText(bundle.data.fuetype)

        self.report.setFontWeight(75)
        self.report.append("")
        self.report.append("Fuel pin enrichments (w/o): ")
        
        
