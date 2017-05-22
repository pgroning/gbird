from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt

from PyQt4 import QtGui, QtCore
import numpy as np

import matplotlib.patches as mpatches
try:  # patheffects not available for older versions of matplotlib
    import matplotlib.patheffects as path_effects
except:
    pass


#class cpin(object):
class FuePin(object):
    def __init__(self, axes):
        self.axes = axes

    def set_circle(self, x, y, r, c=None):
        self.x = x
        self.y = y
        if c is None:
            c = self.facecolor
        self.circle = mpatches.Circle((x, y), r, fc=c, ec=(0.1, 0.1, 0.1))
        self.circle.set_linestyle('solid')
        self.circle.set_linewidth(2.0)
        try:
            self.circle.set_path_effects([path_effects.
                                          withSimplePatchShadow()])
        except:
            pass

        # Set background rectangle
        d = 2*r + 0.019
        self.rectangle = mpatches.Rectangle((x - d/2, y - d/2), d, d,
                                            fc=(1, 1, 1), alpha=1.0,
                                            ec=(1, 1, 1))
        self.rectangle.set_fill(True)
        self.rectangle.set_linewidth(0.0)
        
    def set_text(self, string='', fsize=8):
        # if hasattr(self,'text'):
        #    self.text.remove()
        self.text = self.axes.text(self.x, self.y, string, ha='center',
                                   va='center', fontsize=fsize)

    def is_clicked(self, xc, yc):
        r2 = (xc - self.x)**2 + (yc - self.y)**2
        # Mouse click is within pin radius ?
        if r2 < self.circle.get_radius()**2:
            return True
        else:
            return False

    def set_clickpatch(self, edge_color=(0, 0, 0)):
        r = self.circle.get_radius() * 1.2
        x = self.x
        y = self.y
        
        alpha = self.rectangle.get_alpha()
        if alpha > 0.0:
            fc = self.rectangle.get_fc()
            edge_color = (1 - np.array(fc)).tolist()  # complement color

        self.clickpatch = mpatches.Circle((x, y), r, fc=(1, 1, 1), alpha=1.0,
                                          ec=edge_color)
        self.clickpatch.set_linestyle('solid')
        self.clickpatch.set_fill(False)
        self.clickpatch.set_linewidth(3.0)
        self.axes.add_patch(self.clickpatch)

    def set_maxpin_patch(self, edge_color=(1, 0, 0)):
        d = self.circle.get_radius() * 2 * 1.25
        x = self.x - d / 2
        y = self.y - d / 2
        self.maxpin_patch = mpatches.Rectangle((x, y), d, d, fc=(1, 1, 1), 
                                               alpha=1.0, ec=edge_color)
        self.maxpin_patch.set_linestyle('solid')
        self.maxpin_patch.set_fill(False)
        self.maxpin_patch.set_linewidth(3.0)
        self.axes.add_patch(self.maxpin_patch)



class EnrDialog(QtGui.QDialog):
    def __init__(self, parent, mode="edit"):
        # QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.mode = mode

        # self.setWindowTitle("Window title")
        # set x-pos relative to cursor position
        # xpos = QCursor.pos().x() - 250
        # set dialog pos relative to main window
        xpos = parent.pos().x() + parent.size().width() / 2
        ypos = parent.pos().y() + parent.size().height() / 2
        self.setGeometry(QtCore.QRect(xpos, ypos, 150, 120))

        case_num = int(parent.case_cbox.currentIndex())
        ipin = parent.pinselection_index
        enr = parent.enrpinlist[case_num][ipin].ENR
        ba = parent.enrpinlist[case_num][ipin].BA
        ba = 0 if np.isnan(ba) else ba
        if mode == "edit":
            self.setWindowTitle("Edit enrichment")
        elif mode == "add":
            self.setWindowTitle("Add enrichment")
        self.enr_text = QtGui.QLineEdit("%.2f" % enr)
        dens = parent.enrpinlist[case_num][ipin].DENS
        self.dens_text = QtGui.QLineEdit("%.3f" % dens)
        self.ba_text = QtGui.QLineEdit("%.2f" % ba)
        validator = QtGui.QDoubleValidator(0, 9.99, 2, self)
        self.enr_text.setValidator(validator)
        self.ba_text.setValidator(validator)
        validator = QtGui.QDoubleValidator(0, 9.99, 3, self)
        self.dens_text.setValidator(validator)

        flo = QtGui.QFormLayout()
        flo.addRow("%U-235:", self.enr_text)
        flo.addRow("Density (g/cm-3):", self.dens_text)
        flo.addRow("%Gd:", self.ba_text)

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
        self.enr = self.enr_text.text().toDouble()[0]
        self.dens = self.dens_text.text().toDouble()[0]
        self.ba = self.ba_text.text().toDouble()[0]
        if self.mode == "edit":
            self.parent.enrpin_edit_callback()
        elif self.mode == "add":
            self.parent.enrpin_add_callback()
