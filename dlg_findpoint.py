from PyQt4 import QtGui, QtCore
from pyqt_trace import pyqt_trace as qtrace

class FindDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setWindowTitle("Find state point")
        xpos = self.parent.pos().x() + self.parent.size().width() / 2
        ypos = self.parent.pos().y() + self.parent.size().height() / 2
        self.setGeometry(QtCore.QRect(xpos, ypos, 150, 120))

        flo = QtGui.QFormLayout()
        
        voi_list = map(str, self.parent.bunlist[-1].segments[0].data.voilist)
        self.voi_cbox = QtGui.QComboBox()
        self.voi_cbox.addItems(QtCore.QStringList(voi_list))

        self.vhi_cbox = QtGui.QComboBox()
        self.vhi_cbox.addItems(QtCore.QStringList(voi_list))

        tfu_list = [""]
        self.tfu_cbox = QtGui.QComboBox()
        self.tfu_cbox.addItems(QtCore.QStringList(tfu_list))

        tmo_list = [""]
        self.tmo_cbox = QtGui.QComboBox()
        self.tmo_cbox.addItems(QtCore.QStringList(tmo_list))

        #exp_list = [""]
        #self.exp_cbox = QtGui.QComboBox()
        #self.exp_cbox.addItems(QtCore.QStringList(exp_list))

        self.exp_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.exp_slider.setRange(0, 100)
        self.exp_slider.setValue(0)
        self.exp_slider.setTracking(True)
        self.exp_slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        #self.connect(self.exp_slider, QtCore.SIGNAL('valueChanged(int)'), 
        #             self.exp_slider_action)

        flo.addRow("VOI:", self.voi_cbox)
        flo.addRow("VHI:", self.vhi_cbox)
        flo.addRow("TFU:", self.tfu_cbox)
        flo.addRow("TMO:", self.tmo_cbox)
        #flo.addRow("EXP:", self.exp_cbox)
        flo.addRow("EXP:", self.exp_slider)

        groupbox = QtGui.QGroupBox()
        groupbox.setTitle("Parameters")
        groupbox.setStyleSheet("QGroupBox {border: 1px solid silver;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px 0px 0px 0px}")
        groupbox.setLayout(flo)
        grid = QtGui.QGridLayout()
        grid.addWidget(groupbox, 0, 0)
        
        hbox = QtGui.QHBoxLayout()
        self.find_button = QtGui.QPushButton("Find")
        self.close_button = QtGui.QPushButton("Close")
        hbox.addWidget(self.find_button)
        hbox.addWidget(self.close_button)
        self.connect(self.close_button, QtCore.SIGNAL('clicked()'),
                     self.close)
        self.connect(self.find_button, QtCore.SIGNAL('clicked()'), 
                     self.find_action)

        vbox = QtGui.QVBoxLayout()
        #vbox.addLayout(flo)
        vbox.addLayout(grid)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def closeEvent(self, event):
        """This method is called before closing the dialog"""
        del self.parent.findpoint_dlg

    def find_action(self):
        voi = int(self.voi_cbox.currentText())
        vhi = int(self.vhi_cbox.currentText())
        exp_percent = self.exp_slider.value()
        
        self.parent.set_point_number(voi=voi, vhi=vhi, exp_percent=exp_percent)

    #def exp_slider_action(self):
    #    svalue = self.exp_slider.value()
    #    print "slider value = " + str(svalue)
        
