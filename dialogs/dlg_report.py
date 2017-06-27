import numpy as np
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
        
        self.insert_text()

        hbox = QtGui.QHBoxLayout()
        self.close_button = QtGui.QPushButton("Close")
        hbox.addStretch()
        hbox.addWidget(self.close_button)
        self.connect(self.close_button, QtCore.SIGNAL('clicked()'),
                     self.close)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.report)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def update(self):
        self.report.clear()
        self.insert_text()

    def closeEvent(self, event):
        """This method is called before closing the dialog"""
        
        del self.parent.report_dlg  # delete parent attr that holds the object

    def insert_text(self):

        ibundle = self.parent.ibundle
        iseg = int(self.parent.ui.case_cbox.currentIndex())
        bundle = self.parent.bunlist[ibundle]
        segdata = bundle.segments[iseg].data

        font = QtGui.QFont("monospace")  # font with fixed width
        font.setStyleHint(QtGui.QFont.TypeWriter)  # fallback font
        self.report.setFont(font)
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
        self.report.append("")  # new line
        self.report.append("Fuel pin enrichments (w/o): ")
        header = "{0:10s} {1:10s} {2:10s} {3:6s} {4:10s}".format(
            "Index", "Density", "U-235", "Gd", "Number")
        self.report.append(header)
        self.report.setFontWeight(50) 
        formstr = "{0:>3d} {1:>14.3f} {2:>8.2f} {3:>7.2f} {4:>7d}"
        pinobjects = self.parent.pinobjects[iseg]
        totnum = 0
        for i, pin in enumerate(self.parent.enrpinlist[iseg]):
            num = len([1 for p in pinobjects if p.LFU == i + 1])
            BA = 0 if np.isnan(pin.BA) else pin.BA
            tline = formstr.format(i+1, pin.DENS, pin.ENR, BA, num)
            self.report.append(tline)
            totnum += num
        self.report.append("{0:>43s}".format("---"))
        self.report.append("{0:>43d}".format(totnum))
