#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is the main window of the program.
"""

from IPython.core.debugger import Tracer  # Set tracepoint (used for debugging)
# Usage: Tracer()()
# Set a tracepoint that works with Qt
from pyqt_trace import pyqt_trace as qtrace
# Usage: qtrace()

try:
    import cPickle as pickle
except:
    import pickle

import sys
import os
import time
import copy
import re
import numpy as np
from PyQt4 import QtGui, QtCore

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg \
    as FigureCanvas
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg \
# as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

#try:  # patheffects not available for older versions of matplotlib
#    import matplotlib.patheffects as path_effects
#except:
#    pass

from bundle import Bundle
from btf import Btf
from plot import PlotWin
from dlg_cascalc import CasDialog, CasRunDialog
from dlg_pertcalc import PertDialog
from dlg_bundle import BundleDialog
from dlg_bundle import SegmentDialog
from dlg_report import ReportDialog
from dlg_findpoint import FindDialog
from dlg_enrichment import EnrichmentDialog
from dlg_egv import EgvDialog
from pin import FuePin, EnrDialog
from pincount import PinCount
from casinp import Casinp
from progbar import ProgressBar
from map_s96 import s96o2
from map_a10 import a10xm
from map_a11 import at11
from threads import ImportThread, QuickCalcThread, RunC4Thread


class dataThread(QtCore.QThread):
    def __init__(self, parent):
        QThread.__init__(self)
        self.parent = parent
        self._kill = False

    def __del__(self):
        self.wait()

    def run(self):
        if not self._kill:
            self.dataobj = casio()
            self.dataobj.readinp(self.parent._filename)
            self.dataobj.readcax()
            self.emit(QtCore.SIGNAL('progressbar_update(int)'), 90)
        if not self._kill:
            self.dataobj.calcbtf()
        if not self._kill:
            self.parent.dataobj = self.dataobj

        # self.parent.dataobj = casio()
        # self.parent.dataobj.readinp(self.parent._filename)
        # self.parent.dataobj.readcax()
        # self.emit(SIGNAL('progressbar_update(int)'),90)
        # self.parent.dataobj.calcbtf()

#"""
#class Circle(object):
#    def __init__(self,axes,x,y,c=(1,1,1),text='',r=0.028):
#        self.axes = axes
#        # radius = 0.028
#        self.circle = mpatches.Circle((x,y), r, fc=c, ec=(0.1, 0.1, 0.1))
#        self.circle.set_linestyle('solid')
#        try:
#            self.circle.set_path_effects([path_effects.withSimplePatchShadow()]#)
#        except: pass
#        self.circle.set_linewidth(2.0)
#        self.x = x
#        self.y = y
#        self.text = self.axes.text(x,y,text,ha='center',va='center',fontsize=8)
#        # self.axes.add_patch(self.circle)
#
#    def set_text(self,text):
#        pass
#        # self.text.remove()
#        # self.text = self.axes.text(self.x,self.y,text,ha='center',
#        va='center',fontsize=8)
#
#    def is_clicked(self,xc,yc):
#        r2 = (xc-self.x)**2 + (yc-self.y)**2
#        if r2 < self.circle.get_radius()**2: #Mouse click is within pin radius
#            return True
#        else:
#            return False
#"""


#class cpin(object):
#    def __init__(self, axes):
#        self.axes = axes
#
#    def set_circle(self, x, y, r, c=None):
#        self.x = x
#        self.y = y
#        if c is None:
#            c = self.facecolor
#        self.circle = mpatches.Circle((x, y), r, fc=c, ec=(0.1, 0.1, 0.1))
#        self.circle.set_linestyle('solid')
#        self.circle.set_linewidth(2.0)
#        try:
#            self.circle.set_path_effects([path_effects.
#                                          withSimplePatchShadow()])
#        except:
#            pass
#
#        # Set background rectangle
#        d = 2*r + 0.019
#        self.rectangle = mpatches.Rectangle((x - d/2, y - d/2), d, d,
#                                            fc=(1, 1, 0), alpha=1.0,
#                                            ec=(1, 1, 1))
#        self.rectangle.set_fill(True)
#        self.rectangle.set_linewidth(0.0)
#        
#    def set_text(self, string='', fsize=8):
#        # if hasattr(self,'text'):
#        #    self.text.remove()
#        self.text = self.axes.text(self.x, self.y, string, ha='center',
#                                   va='center', fontsize=fsize)
#
#    def is_clicked(self, xc, yc):
#        r2 = (xc - self.x)**2 + (yc - self.y)**2
#        # Mouse click is within pin radius ?
#        if r2 < self.circle.get_radius()**2:
#            return True
#        else:
#            return False
#"""

#class EnrDialog(QtGui.QDialog):
#    def __init__(self, parent, mode="edit"):
#        # QDialog.__init__(self, parent)
#        QtGui.QDialog.__init__(self)
#        self.parent = parent
#        self.mode = mode
#
#        # self.setWindowTitle("Window title")
#        # set x-pos relative to cursor position
#        # xpos = QCursor.pos().x() - 250
#        # set dialog pos relative to main window
#        xpos = parent.pos().x() + parent.size().width() / 2
#        ypos = parent.pos().y() + parent.size().height() / 2
#        self.setGeometry(QtCore.QRect(xpos, ypos, 150, 120))
#
#        case_num = int(parent.case_cbox.currentIndex())
#        ipin = parent.pinselection_index
#        enr = parent.enrpinlist[case_num][ipin].ENR
#        ba = parent.enrpinlist[case_num][ipin].BA
#        ba = 0 if np.isnan(ba) else ba
#        if mode == "edit":
#            self.setWindowTitle("Edit enrichment")
#        elif mode == "add":
#            self.setWindowTitle("Add enrichment")
#        self.enr_text = QtGui.QLineEdit("%.2f" % enr)
#        # dens = parent.enrpinlist[case_num][ipin].DENS
#        # self.dens_text = QtGui.QLineEdit("%.3f" % dens)
#        self.ba_text = QtGui.QLineEdit("%.2f" % ba)
#        validator = QtGui.QDoubleValidator(0, 9.99, 2, self)
#        self.enr_text.setValidator(validator)
#        self.ba_text.setValidator(validator)
#        # validator = QtGui.QDoubleValidator(0, 9.99, 3, self)
#        # self.dens_text.setValidator(validator)
#
#        flo = QtGui.QFormLayout()
#        flo.addRow("%U-235:", self.enr_text)
#        #flo.addRow("Density (g/cm-3):", self.dens_text)
#        flo.addRow("%Gd:", self.ba_text)
#
#        hbox = QtGui.QHBoxLayout()
#        self.ok_button = QtGui.QPushButton("Ok")
#        self.cancel_button = QtGui.QPushButton("Cancel")
#        hbox.addWidget(self.cancel_button)
#        hbox.addWidget(self.ok_button)
#        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'),
#                     self.close)
#        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), self.action)
#
#        vbox = QtGui.QVBoxLayout()
#        vbox.addLayout(flo)
#        vbox.addStretch()
#        vbox.addLayout(hbox)
#        self.setLayout(vbox)
#
#    def action(self):
#        self.close()
#        self.enr = self.enr_text.text().toDouble()[0]
#        #self.dens = self.dens_text.text().toDouble()[0]
#        self.ba = self.ba_text.text().toDouble()[0]
#        if self.mode == "edit":
#            self.parent.enrpin_edit_callback()
#        elif self.mode == "add":
#            self.parent.enrpin_add_callback()
#"""

class PinTableWidget(QtGui.QTableWidget):
    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.setColumnCount(4)
        self.setRowCount(100)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                 QtGui.QSizePolicy.Minimum)
        self.setMinimumWidth(180)
        self.setHorizontalHeaderLabels(('Index', 'EXP', 'FINT', 'BTF'))
        self.setSortingEnabled(True)
        self.setColumnHidden(0, True)
        verticalheader = self.verticalHeader()
        verticalheader.setResizeMode(QtGui.QHeaderView.Fixed)
        verticalheader.setDefaultSectionSize(25)

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.connect(self.horizontalHeader(),
                     QtCore.SIGNAL('sectionClicked(int)'),
                     self.parent.tableHeaderSort)
        self.connect(self.verticalHeader(),
                     QtCore.SIGNAL('sectionClicked(int)'), 
                     self.parent.pinSelect)
        self.cellActivated.connect(self.parent.pinSelect)
        self.cellClicked.connect(self.parent.pinSelect)
        
    def sort_items(self):
        self.sortItems(0, QtCore.Qt.AscendingOrder)

    def setpincoords(self):
        """Update table with pin coordinates"""
        
        case_num = int(self.parent.case_cbox.currentIndex())
        npin = len(self.parent.pinobjects[case_num])
        self.setRowCount(npin)
        
        for i, pinobj in enumerate(self.parent.pinobjects[case_num]):
            coord_item = QtGui.QTableWidgetItem(pinobj.coord)
            self.setVerticalHeaderItem(i, coord_item)
            i_item = QtGui.QTableWidgetItem()
            i_item.setData(QtCore.Qt.EditRole, QtCore.QVariant(int(i)))
            self.setItem(i, 0, i_item)

    def selectAll(self):  # redefine built-in selectAll method
        self.sort_items() 
        self.setpincoords()


class InfoLabel(QtGui.QLabel):
    def __init__(self, parent=None, width=100):
        #QtGui.QDialog.__init__(self)
        QtGui.QLabel.__init__(self)
        self.setStyleSheet("""QLabel {background-color : rgb(245, 245, 245); 
                              color : black;}""")
        self.setFrameStyle(QtGui.QFrame.Panel | 
                           QtGui.QFrame.Sunken)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setFixedHeight(20)
        self.setFixedWidth(width)


class Data(object):
    """Empty class with the purpose to organize data"""
    pass


class MainWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        # QtGui.QMainWindow.__init__(self, parent)
        self.appversion = "1.0.0T"
        self.verbose = True

        path = os.path.realpath(__file__)
        self.appdir = os.path.split(path)[0] + os.sep
        
        self.setWindowTitle("Greenbird v" + self.appversion)

        # self.resize(1100,620)
        # self.move(200,200)

        # Init empty class to hold parameters
        self.params = Data()

        # Initial window size/pos last saved
        self.settings = QtCore.QSettings("greenbird")
        self.settings.beginGroup("MainWindow")
        self.resize(self.settings.value("size", QtCore.
                                        QVariant(QtCore.QSize(1100, 620))).
                    toSize())
        self.move(self.settings.value("pos", QtCore.
                                      QVariant(QtCore.QPoint(200, 200))).
                  toPoint())
        self.settings.endGroup()

        # screenShape = QDesktopWidget().screenGeometry()
        # self.resize( screenShape.width()*0.8,screenShape.width()*0.445 )
        # self.setMinimumWidth(1100)
        # self.setMinimumHeight(610)

        self.resizeEvent = self.on_resize

        # Retrieve initial data
        # self.data_init()
        # self.case_id_current = 0

        self.create_menu()
        self.create_toolbar()
        self.create_main_frame()
        self.create_status_bar()

        self.on_draw()  # Init plot

        self.widgets_setenabled(False)
        # self.draw_fuelmap()
        # self.textbox.setText('1 2 3 4')
        # self.data_init()

        # self.case_cbox.setCurrentIndex(0) # Set default plot case
        # self.case_id_current = 0
        # self.on_plot() # Init plot
        # self.on_draw()
        # self.draw_fuelmap()

    def on_resize(self, event):
        self.axes.set_xlim(0, 1.2)
        self.axes.set_ylim(0, 1)

    def openFile(self):
        """Open bundle object from pickle file"""

        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_default",
                                           QtCore.QString("")).toString()
        self.settings.endGroup()
        # file_choices = "inp (*.inp);;pickle (*.p)"
        file_choices = "Data files (*.gbi *.cax)"
        filename = unicode(QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                             path_default,
                                                             file_choices))
        if filename:
            self.setCursor(QtCore.Qt.WaitCursor)
            # Save default path to config file
            path = os.path.split(filename)[0]
            self.settings.beginGroup("PATH")
            self.settings.setValue("path_default", QtCore.QString(path))
            self.settings.endGroup()

            filext = os.path.splitext(filename)[1]
            #if filext == ".gbi":  # pickle file
            self.load_pickle(filename)
            #self.fig_update()
            self.chanbow_sbox_update()
            self.widgets_setenabled()
            #else:
            #    msgBox = QtGui.QMessageBox()
            #    status = msgBox.information(self, "Importing data",
            #                                "Continue?",
            #                                QtGui.QMessageBox.Yes |
            #                                QtGui.QMessageBox.Cancel)
            #    self.statusBar().showMessage('Importing data from %s' 
            #                                 % filename, 2000)
            #    self._filename = filename
            #    if status == QtGui.QMessageBox.Yes:
            #        self.setCursor(QtCore.Qt.WaitCursor)
            #        self.ibundle = 0
            #        #if filext == ".inp":
            #        #    self.read_inp(filename)
            #        #    #self.quick_calc(state_num=0)  # reference calculation
            #        if filext == ".cax":
            #            self.read_cax(filename)
            #            self.fig_update()
            self.setCursor(QtCore.Qt.ArrowCursor)

#    def newProject(self):
#        """Open project setup file"""
#        
#        # Import default path from config file
#        self.settings.beginGroup("PATH")
#        path_default = self.settings.value("path_default",
#                                           QtCore.QString("")).toString()
#        self.settings.endGroup()
#        file_choices = "*.pro (*.pro)"
#        filename = unicode(QtGui.QFileDialog.getOpenFileName(self, 'Open file',
#                                                             path_default,
#                                                             file_choices))
#        if filename:
#            # Save default path to config file
#            path = os.path.split(filename)[0]
#            self.settings.beginGroup("PATH")
#            self.settings.setValue("path_default", QtCore.QString(path))
#            self.settings.endGroup()
#            self.ibundle = 0
#            self.read_pro(filename)
                    
    def load_pickle(self, filename):
        """Load bundle object from pickle file"""

        self.statusBar().showMessage('Load project from %s' % filename, 2000)
        # self.bundle = Bundle()
        # self.bundle.loadpic(filename)
        print "Loading data from file " + filename
        self.clear_data()

        with open(filename, 'rb') as fp:
            self.params = pickle.load(fp)
            self.bunlist = pickle.load(fp)
            try:
                self.biascalc = pickle.load(fp)
            except EOFError:  # biascalc exists?
                pass

        self.ibundle = len(self.bunlist) - 1
        self.init_pinobjects()
        self.init_cboxes()
 
    def read_cax(self, filename):
        """Importing data from a single cax file"""
        
        self.clear_data()
        bundle = Bundle()
        bundle.read_single_cax(filename)
        bundle.new_btf()
        self.bunlist = []
        self.bunlist.append(bundle)

        self.init_pinobjects()
        #self.fig_update()

#    def dataobj_finished(self):
#        print "dataobject constructed"
#        self.init_pinobjects()
#
#        # Perform reference quick calculation for base case
#        print "Performing a reference quick calculation..."
#        ncases = len(self.dataobj.cases)
#        for case_num in range(ncases):
#            self.quick_calc(case_num)
#
#        # self.thread.quit()
#        # self.draw_fuelmap()
#        # self.set_pinvalues()
#        self.timer.stop()
#
#        # Update case number list box
#        for i in range(1, ncases + 1):
#            self.case_cbox.addItem(str(i))
#        
#        self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'),
#                     self.fig_update)
#        self.fig_update()
#
#        self.progressbar.update(100)
#        self.progressbar.setWindowTitle("All data imported")
#        self.progressbar.button.setText("Ok")
#        self.progressbar.button.clicked.disconnect(self.killThread)
#        self.progressbar.button.clicked.connect(self.progressbar.close)
#        self.progressbar.button.setEnabled(True)

        # QtGui.QMessageBox.information(self,"Done!","All data imported!")

    def __progressbar_update(self, val=None):
        if val is not None:
            self.progressbar._value = max(val, self.progressbar._value)
        self.progressbar.update(self.progressbar._value)
        self.progressbar._value += 1

    def __killThread(self):
        """Kill progress thread"""

        self.disconnect(self.timer, QtCore.SIGNAL('timeout()'),
                        self.__progressbar_update)
        #self.disconnect(self.thread, QtCore.SIGNAL('finished()'),
        #                self.dataobj_finished)
        self.disconnect(self.thread, QtCore.SIGNAL('progressbar_update(int)'),
                        self.__progressbar_update)
        self.thread._kill = True
        self.thread.terminate()
        self.progressbar.close()
        self.__file_cleanup()
        # self.progressbar.close
        # self.thread.wait()

#    def read_pro(self, filename):
#        """Reading project setup file"""
#        self.clear_data()
#        bundle = Bundle()
#        if not bundle.readpro(filename):  # stop if error is encountered
#            return
#        self.bunlist = []
#        self.bunlist.append(bundle)
#        self.ibundle = 0

    def __file_cleanup(self):
        """Cleanup files"""
        filenames = os.listdir(".")
        regexp = "^tmp.+\.(inp|out|cax|cfg|log)$"
        rec = re.compile(regexp)
        for fname in filenames:
            if rec.match(fname):
                os.remove(fname)

    def init_bundle(self):
        """initialize a bundle instance"""
        self.bunlist = [Bundle()]
        
    def import_data(self):
        """Importing data from card image file"""
        
        #msgBox = QtGui.QMessageBox()
        #status = msgBox.information(self, "Importing data", "Continue?",
        #                            QtGui.QMessageBox.Yes |
        #                            QtGui.QMessageBox.Cancel)
        #self.statusBar().showMessage('Importing data from %s' % filename, 2000)
        #self._filename = filename
        #if status == QtGui.QMessageBox.Yes:
        
        self.thread = ImportThread(self)
        self.connect(self.thread, QtCore.SIGNAL('import_data_finished()'), 
                     self.__import_data_finished)
        self.connect(self.thread, QtCore.SIGNAL('finished()'), 
                     self.__quickcalc_setenabled)
        self.connect(self.thread, QtCore.SIGNAL('progressbar_update(int)'),
                     self.__progressbar_update)

        # self.setCursor(QtCore.Qt.WaitCursor)

        self.ibundle = 0
        self.thread.start()
        self.statusBar().showMessage("Importing data...")

            #self.clear_data()
            #bundle = Bundle()
            #if not bundle.readpro(filename):  # stop if error is encountered
            #    self.setCursor(QtCore.Qt.ArrowCursor)
            #    return
            # inarg content="unfiltered" reads the whole file content

            
            #bundle = self.bunlist[0]
            #bundle.readcax(content=bundle.data.content)
            #bundle.new_btf()
            
            # Perform reference calculation
            #print "Performing reference calculation..."
            #self.biascalc = Bundle(parent=self.bunlist[0])
            #self.biascalc.new_calc(model="C3", dep_max=None,
            #                       dep_thres=None, voi=None)
            
            #self.init_pinobjects()
            #self.init_cboxes()

            #self.setCursor(QtCore.Qt.ArrowCursor)
            #qtrace()

        self.progressbar = ProgressBar()
        self.progressbar.setWindowTitle("Importing data...")
        xpos = self.pos().x() + self.width()/2 - self.progressbar.width()/2
        ypos = self.pos().y() + self.height()/2 - self.progressbar.height()/2
        self.progressbar.move(xpos, ypos)
        self.progressbar.show()
        self.progressbar.button.clicked.connect(self.__killThread)
        
        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), 
                     self.__progressbar_update)
        self.progressbar._value = 1
        if self.bunlist[0].data.content == "filtered":
            self.timer.start(60)  # argument is update period in ms
        else:
            self.timer.start(1000)

            #self.thread.wait()
            #self.thread.terminate()
            ##self.fig_update()
            #self.widgets_setenabled(True)
        #else:
        #    return
            
    def __import_data_finished(self):
        """importation of data finished"""

        self.init_pinobjects()
        self.init_cboxes()
        # self.setCursor(QtCore.Qt.ArrowCursor)
        self.widgets_setenabled(True)

        self.timer.stop()
        self.progressbar.update(100)
        self.progressbar.setWindowTitle("All data imported")
        self.progressbar.button.setText("Ok")
        self.progressbar.button.clicked.disconnect(self.__killThread)
        self.progressbar.button.clicked.connect(self.progressbar.close)
        self.statusBar().showMessage("Done!", 2000)

    def __quickcalc_setenabled(self, status=True):
        """Enable/disable quickcalc"""
        self.calcAction.setEnabled(status)
        self.quickcalc_action.setEnabled(status)


        '''
        #self.progressbar = ProgressBar()
        
        #self.dataobj = casio()
        self.thread = dataThread(self)
        self.connect(self.thread,SIGNAL('finished()'),self.dataobj_finished)
        self.connect(self.thread,SIGNAL('progressbar_update(int)'),
        # self.progressbar_update)
        self.thread.start()
        
        self.progressbar = ProgressBar()
        xpos = self.pos().x() + self.width()/2 - self.progressbar.width()/2
        ypos = self.pos().y() + self.height()/2 -
        self.progressbar.height()/2
        self.progressbar.move(xpos,ypos)
        self.progressbar.show()
        self.progressbar.button.setEnabled(False)
        self.progressbar.button.clicked.connect(self.killThread)
        # self.progressbar.button.clicked.connect(self.progressbar.close)
        
        self.timer = QTimer()
        self.connect(self.timer,SIGNAL('timeout()'),self.progressbar_update)
        self.progressbar._value = 1
        self.timer.start(500)
        
        # time.sleep(20)
        # self.thread.terminate()
        # pyqt_trace()
        
        # print self.dataobj.data.caxfiles
        
        # self.dataobj = casio()
        # self.dataobj.readinp(filename)
        # self.dataobj.readcax()
        
        # self.dataobj.calcbtf()
        # fuetype = 'SVEA-96'
        # self.dataobj.btf = btf(self.dataobj,fuetype)
        
        # self.setpincoords()
        # self.draw_fuelmap()
        # self.set_pinvalues()
        # self.dataobj.savecas()
        '''
        #else:
        #    return

    def init_cboxes(self):
        """Initiate combo boxes"""
        
        # init segment combo box
        nsegments = len(self.bunlist[-1].segments)
        seglist = map(str, range(1, nsegments + 1))
        self.case_cbox.addItems(QtCore.QStringList(seglist))
        #self.connect(self.case_cbox, QtCore.SIGNAL('currentIndexChanged(int)'),
        #             self.fig_update)
        # init voi combo box
        #voilist = map(str, self.bunlist[-1].segments[0].data.voilist)
        #self.voi_cbox.addItems(QtCore.QStringList(voilist))
        #self.vhi_cbox.addItems(QtCore.QStringList(voilist))
        #self.connect(self.voi_cbox, QtCore.SIGNAL('currentIndexChanged(int)'),
        #             self.set_point_number)
        #self.connect(self.vhi_cbox, QtCore.SIGNAL('currentIndexChanged(int)'),
        #             self.set_point_number) 

    def saveData(self):
        """Save bundle object to pickle file"""

        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_save_file",
                                           QtCore.QString("")).toString()
        self.settings.endGroup()

        file_choices = "Project files (*.gbi)"
        filename = unicode(QtGui.QFileDialog.getSaveFileName(self,
                                                             "Save project",
                                                             path_default,
                                                             file_choices))
        if filename:  # ok button clicked
            fname_split =  os.path.splitext(filename)
            if fname_split[1] != ".gbi":
                filename = filename + ".gbi"  # add file extension
            with open(filename, 'wb') as fp:
                pickle.dump(self.params, fp, 1)
                pickle.dump(self.bunlist, fp, 1)
                if hasattr(self, "biascalc"):
                    pickle.dump(self.biascalc, fp, 1)
            print "Project saved to file " + filename

    def saveFigure(self):
        """Save fuel map to .png format"""
 
        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_save_figure",
                                           QtCore.QString("")).toString()
        self.settings.endGroup()
        
        file_choices = "PNG (*.png)|*.png"
        filename = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save As',
                                                             path_default,
                                                             file_choices))
        if filename:
            # Save default path to config file
            path = os.path.split(filename)[0]
            self.settings.beginGroup("PATH")
            self.settings.setValue("path_save_figure", QtCore.QString(path))
            self.settings.endGroup()
            
            self.canvas.print_figure(filename, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % filename, 2000)

    def export_to_ascii(self):
        """Export data to file using YAML format"""

        iseg = int(self.case_cbox.currentIndex())
        param = str(self.param_cbox.currentText())

        LFU = self.bunlist[self.ibundle].segments[iseg].data.LFU
        M = np.zeros(LFU.shape).astype(float)

        P = [getattr(pin, param) for pin in self.pinobjects[iseg]]

        k = 0
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                if LFU[i, j] > 0:
                    M[i, j] = P[k]
                    k += 1

        outfile = self.select_yamlfile()
        #outfile = "gb-export.yml"
        f = open(outfile, "w")
        for v in M:
            line = ', '.join(map(str, v))
            f.write("- [" + line + "]\n")
        f.close()

    def select_yamlfile(self):
        """Select file for writing"""
        
        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_save_file",
                                           QtCore.QString("")).toString()
        self.settings.endGroup()
        file_choices = "YAML (*.yml *.yaml)"
        filename = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save file',
                                                             path_default,
                                                             file_choices))
        if filename:
            fname_split =  os.path.splitext(filename)
            if fname_split[1] not in [".yml", ".yaml"]:
                filename = filename + ".yml"  # add file extension
            # Save default path to config file
            path = os.path.split(filename)[0]
            self.settings.beginGroup("PATH")
            self.settings.setValue("path_save_file", QtCore.QString(path))
            self.settings.endGroup()    
        return filename

    def plot_pin(self):
        self.open_plotwin(plotmode="pin")
            
    def open_plotwin(self, plotmode=None):
        """Open plot window"""

        if hasattr(self, "bunlist"):  # data is imported
            if not hasattr(self, "plotwin"):  # plot win is not already open
                self.plotwin = PlotWin(self, plotmode)
                self.plotwin.show()
        else:
            msg = "There is no data to plot."
            msgBox = QtGui.QMessageBox()
            msgBox.information(self, "No data", msg.strip(), msgBox.Close)

    def plot_update(self):
        if hasattr(self, "plotwin"):  # plot win is open
            self.plotwin.on_plot()

    def report_update(self):
        if hasattr(self, "report_dlg"):
            self.report_dlg.update()

    def get_colormap(self, npins, colormap="rainbow"):
        if colormap == "rainbow":
            cm = plt.cm.gist_rainbow_r(np.linspace(0, 1, npins))[:,:3]
            cmap = cm.tolist()
        elif colormap == "jet":
            #cm = plt.cm.RdBu_r(np.linspace(0, 1, npins))[:,:3]
            cm = plt.cm.jet(np.linspace(0, 1, npins))[:,:3]
            #cm = plt.cm.Spectral_r(np.linspace(0, 1, npins))[:,:3]
            cmap = cm.tolist()
        elif colormap == "bmr":
            n = npins + 1
            v00 = np.zeros(n)
            v11 = np.ones(n)
            v01 = np.linspace(0, 1, n)
            v10 = v01[::-1]  # revert array
            # blue -> magenta
            cm_bm = np.vstack((v01, v00, v11)).transpose()[:-1]
            # magenta -> red
            cm_mr = np.vstack((v11, v00, v10)).transpose()
            cm = np.vstack((cm_bm, cm_mr))
            ic = np.linspace(0, len(cm) - 1, npins).astype(int).tolist()
            cmap = [cm[i] for i in ic]
        return cmap

#    def get_colormap_old(self, num_enr_levels, colormap="rainbow"):
#
#        n = num_enr_levels + 1
#        #n = int(np.ceil(num_enr_levels / 4.0)) + 1
#        v00 = np.zeros(n)
#        v11 = np.ones(n)
#        v01 = np.linspace(0, 1, n)
#        v10 = v01[::-1]  # revert array
#
#        if colormap == "rainbow":
#            # magenta -> blue
#            cm_mb = np.vstack((v10, v00, v11)).transpose()[:-1]  # remove last elem
#            # blue -> cyan
#            # remove last element
#            cm_bc = np.vstack((v00, v01, v11)).transpose()[:-1]
#            # cyan -> green
#            cm_cg = np.vstack((v00, v11, v10)).transpose()[:-1]
#            # green -> yellow
#            cm_gy = np.vstack((v01, v11, v00)).transpose()[:-1]
#            # yellow -> red
#            cm_yr = np.vstack((v11, v10, v00)).transpose()
#            cm = np.vstack((cm_mb, cm_bc, cm_cg, cm_gy, cm_yr))
#        elif colormap == "bmr":
#            # blue -> magenta
#            cm_bc = np.vstack((v01, v00, v11)).transpose()[:-1]
#            # magenta -> red
#            cm_mr = np.vstack((v11, v00, v10)).transpose()
#            cm = np.vstack((cm_bc, cm_mr))
#        elif colormap == "byr":
#            # blue -> yellow
#            cm_by = np.vstack((v01, v01, v10)).transpose()[:-1]
#            # yellow -> red
#            cm_yr = np.vstack((v11, v10, v00)).transpose()
#            cm = np.vstack((cm_by, cm_yr))
#            
#        ic = np.linspace(0, len(cm) - 1, num_enr_levels).astype(int).tolist()
#        cmap = [cm[i].tolist() for i in ic]
#        return cmap

    def init_pinobjects(self):
        self.pinobjects = []
        self.enrpinlist = []

        state_num = self.ibundle
        bundle = self.bunlist[state_num]
        
        nsegments = len(bundle.segments)

        for iseg in range(nsegments):
            LFU = bundle.segments[iseg].data.LFU
            ENR = bundle.segments[iseg].data.ENR
            BA = bundle.segments[iseg].data.BA
            
            pinlist = []
            for i in range(LFU.shape[0]):
                for j in range(LFU.shape[1]):
                    if LFU[i, j] > 0:
                        pinobj = FuePin(self.axes)
                        pinobj.pos = [i, j]
                        pinobj.ENR = ENR[i, j]
                        pinobj.BA = BA[i, j]
                        pinobj.LFU = LFU[i, j]
                        pinlist.append(pinobj)
            self.pinobjects.append(pinlist)
            
            enrlist = []
            FUE = bundle.segments[iseg].data.FUE
            enr_dens = FUE[:, 1]
            enr_levels = FUE[:, 2]
            enr_baindex = FUE[:, 3]
            enr_ba = FUE[:, 4]
            cmap = self.get_colormap(enr_levels.size)
            for i in range(enr_levels.size):
                enrobj = FuePin(self.axes)
                enrobj.facecolor = cmap[i]
                enrobj.ENR = enr_levels[i]
                enrobj.BA = enr_ba[i]
                enrobj.BAindex = enr_baindex[i]
                enrobj.DENS = enr_dens[i]
                enrlist.append(enrobj)
            self.enrpinlist.append(enrlist)

    def enrpin_add(self):
        """add enr pin"""
        self.enr_dlg = EnrDialog(self, "add")
        self.enr_dlg.exec_()  # Make dialog modal

    def enrpin_add_callback(self):
        """enr pin add callback"""

        case_num = int(self.case_cbox.currentIndex())
        ipin = self.pinselection_index  # copy attributes from selected pin

        enrobj = FuePin(self.axes)
        enrobj.facecolor = self.enrpinlist[case_num][ipin].facecolor
        #enrobj.DENS = self.enrpinlist[case_num][ipin].DENS
        enrobj.DENS = self.enr_dlg.dens
        enrobj.ENR = self.enr_dlg.enr
        if self.enr_dlg.ba < 0.00001:
            enrobj.BA = np.nan
            enrobj.BAindex = np.nan
        else:
            enrobj.BA = self.enr_dlg.ba
            enrobj.BAindex = 7300  # Gd

        self.enrpinlist[case_num].append(enrobj)

        # if enrobj.ENR > self.enrpinlist[case_num][-1].ENR:
        #    self.enrpinlist[case_num].append(enrobj)
        # else:
        #    i = next(i for i, enrpin in enumerate(self.enrpinlist[case_num])
        #             if enrpin.ENR > enrobj.ENR)
        #    self.enrpinlist[case_num].insert(i, enrobj)
        self.fig_update()

    def enrpin_edit(self):
        """edit enr pin"""
        self.enr_dlg = EnrDialog(self, "edit")
        self.enr_dlg.exec_()  # Make dialog modal

    def enrpin_edit_callback(self):
        """enr pin edit callback"""

        case_num = int(self.case_cbox.currentIndex())
        ipin = self.pinselection_index  # index of enr level pin to be edited
        enrpin = self.enrpinlist[case_num][ipin]

        # update fue pins
        for pin in self.pinobjects[case_num]:
            if pin.LFU == ipin + 1:
                pin.ENR = self.enr_dlg.enr
                #pin.DENS = enrpin.DENS
                pin.DENS = self.enr_dlg.dens
                pin.BA = self.enr_dlg.ba

        # update enr level pin
        self.enrpinlist[case_num][ipin].ENR = self.enr_dlg.enr
        self.enrpinlist[case_num][ipin].DENS = self.enr_dlg.dens
        if self.enr_dlg.ba < 0.00001:
            self.enrpinlist[case_num][ipin].BA = np.nan
        else:
            self.enrpinlist[case_num][ipin].BA = self.enr_dlg.ba
        self.fig_update()

    def enrpin_remove(self):
        """Remove enr level pin"""
        msgBox = QtGui.QMessageBox()
        status = msgBox.information(self, "Remove enrichment", "Are you sure?",
                                    QtGui.QMessageBox.Yes |
                                    QtGui.QMessageBox.Cancel)
        if status == QtGui.QMessageBox.Cancel:
            return

        case_num = int(self.case_cbox.currentIndex())
        ipin = self.pinselection_index  # index of enr level pin to be removed
        
        del self.enrpinlist[case_num][ipin]  # remove the selected pin
        
        enrpin_num = len(self.enrpinlist[case_num])
        if ipin >= enrpin_num:
            j = enrpin_num - 1
        else:
            j = ipin
        
        for pin in self.pinobjects[case_num]:
            if pin.LFU == ipin + 1:
                pin.ENR = self.enrpinlist[case_num][j].ENR
                if np.isnan(self.enrpinlist[case_num][j].BA):
                    pin.BA = 0.0
                else:
                    pin.BA = self.enrpinlist[case_num][j].BA
            if pin.LFU > enrpin_num:
                pin.LFU = enrpin_num
        self.fig_update()

    def enrpin_sort(self):
        """sorting enr levels on enr"""

        msgBox = QtGui.QMessageBox()
        status = msgBox.information(self, "Sort enrichments", "Are you sure?",
                                    QtGui.QMessageBox.Yes |
                                    QtGui.QMessageBox.Cancel)
        if status == QtGui.QMessageBox.Cancel:
            return

        case_num = int(self.case_cbox.currentIndex())
        enrlist = [pin.ENR for pin in self.enrpinlist[case_num]]
        isort = [i for i, e in sorted(enumerate(enrlist), key=lambda x:x[1])]
        
        cmap = self.get_colormap(len(isort))
        pinlist_sorted = []
        for i, j in enumerate(isort):
            pinlist_sorted.append(self.enrpinlist[case_num][j])
            pinlist_sorted[-1].facecolor = cmap[i]
        self.enrpinlist[case_num] = pinlist_sorted

        # Update pin LFU
        invsort = [i for i, e in sorted(enumerate(isort), key=lambda x:x[1])]
        for pin in self.pinobjects[case_num]:
            i = pin.LFU - 1
            pin.LFU = invsort[i] + 1
        
        self.fig_update()

    def open_enrichment_dlg(self):
        """open enrichment dialog"""
        self.enrichment_dlg = EnrichmentDialog(self)
        self.enrichment_dlg.exec_()
        if self.enrichment_dlg.ok:
            self.fig_update()

    def open_segment_dlg(self):
        """open bundle edit dialog"""
        self.bunedit_dlg = SegmentDialog(self)
        self.bunedit_dlg.exec_()
        if self.bunedit_dlg.update_btf:
            self.bunlist[self.ibundle].new_btf()
            self.fig_update()
        elif self.bunedit_dlg.update_figure:
            self.fig_update()

    def open_bundle_dlg(self):
        """open bundle settings dialog"""
        self.bundle_dlg = BundleDialog(self)
        self.bundle_dlg.exec_()  # Make dialog modal

    def open_pert_dlg(self):
        self.pert_dlg = PertDialog(self)
        self.pert_dlg.exec_()

    def open_cas_dlg(self):
        """open cas settings dialog"""
        self.cas_dlg = CasDialog(self)
        self.cas_dlg.exec_()
        
    def open_fullcalc_dlg(self):
        """open run fullcalc dialog"""
        self.fullcalc_dlg = CasRunDialog(self)
        self.fullcalc_dlg.exec_()

    def open_report_dlg(self):
        """open fuel report dialog"""
        if hasattr(self, "bunlist"):  # check that data has been imported
            if not hasattr(self, "report_dlg"):  # not already open?
                self.report_dlg = ReportDialog(self)
                #self.report_dlg.setModal(False)
                self.report_dlg.show()  # Make dialog non-modal
                #self.report_dlg.exec_()

    def open_findpoint_dlg(self):
        """open find statepoint dialog"""
        if hasattr(self, "bunlist"):  # check that data has been imported
            if not hasattr(self, "findpoint_dlg"):  # not already open?
                self.findpoint_dlg = FindDialog(self)
                self.findpoint_dlg.show()  # Make dialog non-modal
                
    def open_egv_dlg(self):
        """Open egv settings dialog"""
        self.egv_dlg = EgvDialog(self)
        self.egv_dlg.exec_()

    def set_point_number(self, voi=40.0, vhi=40.0, exp_pc=0):
        ipoint = int(self.point_sbox.value())
        iseg = int(self.case_cbox.currentIndex())
        bundle = self.bunlist[self.ibundle]
        segment = bundle.segments[iseg]
        statepoint = segment.statepoints[ipoint]
        
        voi = float(voi)
        vhi = float(vhi)
        #statepoints = segment.get_statepoints(voi, vhi, tfu)
        statepoints = segment.get_statepoints(voi, vhi)
        if statepoints == None:
            return
        burnvec = [s.burnup for s in statepoints]
        burn_range = max(burnvec) - min(burnvec)
        exp = exp_pc / 100.0 * burn_range + min(burnvec)
        index = [i for i, e in enumerate(burnvec) if e <= exp][-1]
        exp = burnvec[index]
        
        ipoint = segment.findpoint(burnup=exp, voi=voi, vhi=vhi)
        if ipoint is not None:
            self.point_sbox.setValue(ipoint)

        #voi = int(self.voi_cbox.currentText())
        #vhi = int(self.vhi_cbox.currentText())
        #if statepoint.voi != voi or statepoint.vhi != vhi:
        #    ipoint = segment.findpoint(voi=voi, vhi=vhi)
        #    if ipoint is not None:
        #        self.point_sbox.setValue(ipoint)

    def set_pinvalues(self):
        """Update pin values"""

        param_str = str(self.param_cbox.currentText())
        iseg = int(self.case_cbox.currentIndex())

        state_num = self.ibundle
        bundle = self.bunlist[state_num]
        segment = bundle.segments[iseg]
        
        self.point_sbox.setMaximum(len(segment.statepoints) - 1)
        point_num = int(self.point_sbox.value())
        
        #voi = segment.statepoints[point_num].voi
        #ivoi = segment.data.voilist.index(voi)
        #if ivoi != self.voi_cbox.currentIndex():
        #    self.voi_cbox.setCurrentIndex(ivoi)
        #vhi = segment.statepoints[point_num].vhi
        #ivhi = segment.data.voilist.index(vhi)
        #if ivhi != self.vhi_cbox.currentIndex():
        #    self.vhi_cbox.setCurrentIndex(ivhi)

        ENR = segment.data.ENR
        
        EXP = segment.statepoints[point_num].EXP
        FINT = segment.statepoints[point_num].POW

        burnup = segment.statepoints[point_num].burnup
        btf_burnpoints = bundle.btf.burnpoints
        
        index_array = np.where(btf_burnpoints == burnup)[0]
        if len(index_array) > 0:  # is BTF calculated for the specific burnup?
            btf_num = index_array[0]
            BTF = bundle.btf.DOX[btf_num, :, :]
        else:
            BTF = np.zeros(np.shape(bundle.btf.DOX)[1:])
            BTF.fill(np.nan)

        npst = segment.data.npst
        LFU = segment.data.LFU
        BA = segment.data.BA
        
        # Sorting table column 0 in ascending order
        self.table.sort_items()
        #self.table.sortItems(0, QtCore.Qt.AscendingOrder)
        self.table.clearContents()
        self.table.setpincoords()
        
        k = 0
        for i in xrange(npst):
            for j in xrange(npst):
                if LFU[i, j] > 0:
                    self.pinobjects[iseg][k].EXP = EXP[i, j]
                    self.pinobjects[iseg][k].FINT = FINT[i, j]
                    self.pinobjects[iseg][k].BTF = BTF[i, j]

                    expItem = QtGui.QTableWidgetItem()
                    expItem.setData(QtCore.Qt.EditRole, QtCore.QVariant(
                        float(np.round(EXP[i, j], 3))))
                    fintItem = QtGui.QTableWidgetItem()
                    fintItem.setData(QtCore.Qt.EditRole, QtCore.QVariant(
                        float(np.round(FINT[i, j], 3))))
                    btfItem = QtGui.QTableWidgetItem()
                    btfItem.setData(QtCore.Qt.EditRole, QtCore.QVariant(
                        float(np.round(BTF[i, j], 3))))

                    self.table.setItem(k, 1, expItem)
                    self.table.setItem(k, 2, fintItem)
                    self.table.setItem(k, 3, btfItem)
                    k += 1
        
        statepoint = segment.statepoints[point_num]
        #statepoint = state.statepoints[point_num]
        burnup = statepoint.burnup
        voi = statepoint.voi
        vhi = statepoint.vhi
        kinf = statepoint.kinf
        fint = statepoint.fint
        btf = BTF.max()
        tfu = statepoint.tfu
        tmo = statepoint.tmo
        
        formstr = "{0:.0f} / {1:.0f}".format(voi, vhi)
        self.voi_vhi_text.setText(formstr)
        formstr = "{0:.0f} / {1:.0f}".format(tfu, tmo)
        self.tfu_tmo_text.setText(formstr)
        formstr = "{0:.3f}".format(burnup)
        self.burnup_text.setText(formstr)
        formstr = "{0:.5f}".format(kinf)
        self.kinf_text.setText(formstr)
        formstr = "{0:.3f}".format(fint)
        self.fint_text.setText(formstr)
        formstr = "{0:.4f}".format(btf)
        self.btf_text.setText(formstr)

        #self.statusBar().showMessage("""Burnup=%.3f : VOI=%.0f : VHI=%.0f :
#Kinf=%.5f : Fint=%.3f : BTF=%.4f : TFU=%.0f : TMO=%.0f"""
#                                     % (burnup, voi, vhi, kinf, fint, btf,
#                                        tfu, tmo))
        
        npins = len(self.pinobjects[iseg])
        #cmap = self.get_colormap(npins, "bmr")
        cmap = self.get_colormap(npins, "jet")

        # Sort params and get color map
        #if param_str == "FINT":
        #    v = np.array([pin.FINT for pin in self.pinobjects[iseg]])
        #    uni_fint = np.unique(v)
        #    cmap = self.get_colormap(uni_fint.size, "bmr")
        #elif param_str == "BTF":
        #    v = np.array([pin.BTF for pin in self.pinobjects[iseg]])
        #    uni_btf = np.unique(v)
        #    cmap = self.get_colormap(uni_btf.size, "bmr")
        #elif param_str == "EXP":
        #    v = np.array([pin.EXP for pin in self.pinobjects[iseg]])
        #    uni_exp = np.unique(v)
        #    cmap = self.get_colormap(uni_exp.size, "bmr")

        if param_str == "ENR":
            v = np.array([pin.ENR for pin in self.pinobjects[iseg]])
        if param_str == "EXP":
            v = np.array([pin.EXP for pin in self.pinobjects[iseg]])
        elif param_str == "FINT":
            v = np.array([pin.FINT for pin in self.pinobjects[iseg]])
        elif param_str == "BTF":
            v = np.array([pin.BTF for pin in self.pinobjects[iseg]])
        xmin = v.min()
        xmax = v.max()

        for i in xrange(npins):
            #if self.pinobjects[iseg][i].BA < 0.00001:
            #    j = next(j for j, epin in enumerate(self.enrpinlist[iseg])
            #             if epin.ENR == self.pinobjects[iseg][i].ENR)
            #else:
            #    j = next(j for j, epin in enumerate(self.enrpinlist[iseg])
            #             if epin.BA == self.pinobjects[iseg][i].BA
            #             and epin.ENR == self.pinobjects[iseg][i].ENR)
            #self.pinobjects[iseg][i].LFU = j + 1
            j = self.pinobjects[iseg][i].LFU - 1
            fc = self.enrpinlist[iseg][j].circle.get_facecolor()
            self.pinobjects[iseg][i].circle.set_facecolor(fc)

            if param_str == "ENR":
                x = self.pinobjects[iseg][i].ENR
                #xave = v.mean()
                #k = 2
                #y = 1 / (1 + np.exp(-k * (x - xave)))  # sigmoid function
                if xmax == xmin:
                    y = 0.5
                else:
                    y = (x - xmin) / (xmax - xmin)
                ic = int(round(y * (npins - 1)))
                self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])

                text = self.enrpinlist[iseg][j].text.get_text()
                #self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[i])
                #self.pinobjects[iseg][i].rectangle.set_facecolor((1, 1, 1))
                
            elif param_str == "BTF":
                x = self.pinobjects[iseg][i].BTF
                
                if not np.isnan(x):
                    #xave = v.mean()
                    #xstd = v.std()
                    #if xstd == 0:
                    #    y = 0
                    #else:
                    #    k = 3
                    #    y = 1 / (1 + np.exp(-k * (x - xave) / xstd))
                    if xmax == xmin:
                        y = 0.5
                    else:
                        y = (x - xmin) / (xmax - xmin)
                    ic = int(round(y * (npins - 1)))
                    self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])
                    btf_ratio = x / btf * 1000
                    text = ('%.0f' % (btf_ratio))
                else:
                    self.pinobjects[iseg][i].rectangle.set_facecolor((1, 1, 1))
                    text = "nan"

                #pin_btf = self.pinobjects[iseg][i].BTF
                #if np.isnan(pin_btf):
                #    text = "nan"
                #    self.pinobjects[iseg][i].rectangle.set_facecolor((1, 1, 1))
                #else:
                #    btf_ratio = pin_btf / btf * 1000
                #    if int(btf_ratio) == 1000:
                #        text = "1e3"
                #    else:
                #        text = ('%.0f' % (btf_ratio))
                #    ic = next(i for i, v in enumerate(uni_btf) if v == pin_btf)
                #    self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])
            
            elif param_str == "EXP":
                x = self.pinobjects[iseg][i].EXP
                
                #xave = v.mean()
                #xstd = v.std()
                #if xstd == 0:
                #    y = 0
                #else:
                #    k = 3
                #    y = 1 / (1 + np.exp(-k * (x - xave) / xstd))
                if xmax == xmin:
                    y = 0.1
                else:
                    y = (x - xmin) / (xmax - xmin)

                ic = int(round(y * (npins - 1)))
                self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])
                if x < 10:
                    text = '{0:.1f}'.format(x)
                else:
                    text = '{0:.0f}'.format(x)

                #if self.pinobjects[iseg][i].EXP < 10:
                #    text = ('%.1f' % (self.pinobjects[iseg][i].EXP))
                #else:
                #    text = ('%.0f' % (self.pinobjects[iseg][i].EXP))
                #pin_exp = self.pinobjects[iseg][i].EXP
                #ic = next(i for i, v in enumerate(uni_exp) if v == pin_exp)
                #self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])

            elif param_str == "FINT":
                x = self.pinobjects[iseg][i].FINT
                
                #xave = v.mean()
                #xstd = v.std()
                #if xstd == 0:
                #    y = 0
                #else:
                #    k = 3
                #    y = 1 / (1 + np.exp(-k * (x - xave) / xstd))
                if xmax == xmin:
                    y = 0.5
                else:
                    y = (x - xmin) / (xmax - xmin)

                ic = int(round(y * (npins - 1)))
                self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])

                text = '{0:.0f}'.format(x * 100)
                #text = ('%.0f' % (x * 100))
                #pin_fint = self.pinobjects[iseg][i].FINT
                #ic = next(i for i, v in enumerate(uni_fint) if v == pin_fint)
                #self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])
            elif param_str == "ROD":
                return
                
            self.pinobjects[iseg][i].text.remove()
            self.pinobjects[iseg][i].set_text(text)

        if self.track_maxpin.isChecked():
            self.mark_maxpins()

        self.canvas.draw()
        self.plot_update()
        self.report_update()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 'Save file', '',
                                                   file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = "Greenbird version " + self.appversion
        QtGui.QMessageBox.about(self, "About the software", msg.strip())

    def tableHeaderSort(self):
        # print "Sort header"
        case_num = int(self.case_cbox.currentIndex())
        for i, pinobj in enumerate(self.pinobjects[case_num]):
            # for i,pinobj in enumerate(self.circlelist):
            # item = QTableWidgetItem(str(self.table.item(i,0).text()))
            index = int(self.table.item(i, 0).text())
            item = QtGui.QTableWidgetItem(
                str(self.pinobjects[case_num][index].coord))
            # item = QTableWidgetItem(str(self.circlelist[index].coord))
            self.table.setVerticalHeaderItem(i, item)

    def tableSelectRow(self, i):
        index = next(j for j in range(self.table.rowCount())
                     if int(self.table.item(j, 0).text()) == i)
        self.table.selectRow(index)

    def pinSelect(self, i):
        if hasattr(self.table.item(i, 0), "text"):
            index = int(self.table.item(i, 0).text())
            self.mark_pin(index)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_8:  # Up arrow key was pressed
            iseg = int(self.case_cbox.currentIndex())
            imax = self.case_cbox.count() - 1
            if iseg < imax:
                iseg += 1
                self.case_cbox.setCurrentIndex(iseg)  # increase segment
        elif key == QtCore.Qt.Key_2:  # Down arrow key was pressed
            iseg = int(self.case_cbox.currentIndex())
            if iseg > 0:
                iseg -= 1
                self.case_cbox.setCurrentIndex(iseg)  # decrease segment
        elif key == QtCore.Qt.Key_4:  # Left arrow key was pressed
            ipoint = self.point_sbox.value()
            imin = self.point_sbox.minimum()
            if ipoint > imin:
                ipoint -= 1
                self.point_sbox.setValue(ipoint)  # increase state point
        elif key == QtCore.Qt.Key_6:  # Right arrow key was pressed
            ipoint = self.point_sbox.value()
            imax = self.point_sbox.maximum()
            if ipoint < imax:
                ipoint += 1
                self.point_sbox.setValue(ipoint)  # decrease state point

    def on_click(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        #

        # print event.x,event.y
        #if qApp.keyboardModifiers() & Qt.ControlModifier: # ctrl+click
        #    remove = False
        #else:
        #    remove = True
        #    pass
        #qtrace()
        if not hasattr(self, "pinobjects"):  # is data initialized?
            return

        case_num = int(self.case_cbox.currentIndex())

        if event.button is 1:  # left mouse click
            # print event.xdata, event.ydata
            # check if any pin is selected and return the index
            i = next((i for i, cobj in enumerate(self.pinobjects[case_num])
                      if cobj.is_clicked(event.xdata, event.ydata)), None)

            if i is not None and i >= 0:  # A pin is selected
                self.tableSelectRow(i)
                self.mark_pin(i)
                # self.pinselection_index = i
                # j = self.halfsym_pin(i)

        elif event.button is 3:  # right mouse click
            # check if any fuel pin is clicked
            i = next((i for i, cobj in enumerate(self.pinobjects[case_num])
                      if cobj.is_clicked(event.xdata, event.ydata)), None)
            if i is not None and i >= 0:  # A pin is right clicked
                if (not hasattr(self, "pinselection_index") or
                    self.pinselection_index != i):
                    self.tableSelectRow(i)
                    self.mark_pin(i)
                    
                popMenu = QtGui.QMenu(self)
                popMenu.addAction("Plot", self.plot_pin)
                popMenu.exec_(QtGui.QCursor.pos())
 
            #    self.pin_popMenu = QtGui.QMenu(self)
            #    enr_menu = self.pin_popMenu.addMenu("Enr list...")
            #    check_icon = self.appdir + "icons/ok-apply-icon_32x32.png"
            #    icon = QtGui.QIcon(check_icon)
            #    npins = len(self.enrpinlist[case_num])
            #    for j in range(npins):
            #        ipin = j + 1
            #        label = "#" + str(ipin)
            #        action = QtGui.QAction(icon, label, self)
            #        action.triggered.connect(self.enr_update)
            #        if self.pinobjects[case_num][i].LFU == ipin:
            #            action.setIconVisibleInMenu(True)
            #        enr_menu.addAction(action)
            #        #enr_menu.addAction(label, self.pin_update)
            #    self.pin_popMenu.exec_(QtGui.QCursor.pos())
                
            else: # check if enr level pin is clicked
                i = next((i for i, cobj in enumerate(self.enrpinlist[case_num])
                          if cobj.is_clicked(event.xdata, event.ydata)), None)
                if i is not None and i >= 0:  # An enr level pin is selected
                    self.pinselection_index = i
                    
                    popMenu = QtGui.QMenu(self)
                    popMenu.addAction("Add...", self.enrpin_add)
                    popMenu.addAction("Edit...", self.enrpin_edit)
                    popMenu.addAction("Remove", self.enrpin_remove)
                    popMenu.addAction("Sort", self.enrpin_sort)
                    popMenu.exec_(QtGui.QCursor.pos())

                    #self.popMenu = QtGui.QMenu(self)
                    #self.popMenu.addAction("Add...", self.enrpin_add)
                    #self.popMenu.addAction("Edit...", self.enrpin_edit)
                    #self.popMenu.addAction("Remove", self.enrpin_remove)
                    #self.popMenu.addAction("Sort", self.enrpin_sort)
                    #self.popMenu.exec_(QtGui.QCursor.pos())

    def halfsym_pin(self, i, case_num=None):
        """Find the corresponding pin for half symmetry"""

        if case_num is None:
            case_num = int(self.case_cbox.currentIndex())

        pos = self.pinobjects[case_num][i].pos
        sympos = list(reversed(pos))
        j = next(k for k, po in enumerate(self.pinobjects[case_num])
                 if po.pos == sympos)
        return j

    def casecor_pin(self, case_num):
        """Find the corresponding pin for another segment"""
        
        current_case_num = int(self.case_cbox.currentIndex())
        i = self.pinselection_index
        ipos = self.pinobjects[current_case_num][i].pos
        try:
            j = next(k for k, po in enumerate(self.pinobjects[case_num])
                     if po.pos == ipos)
        except:  # no corresponding pin found
            j = np.nan
        return j

    def mark_pin(self, i, edge_color=(0, 0, 0)):
        
        if hasattr(self, "clicked_pin"):
            try:
                self.clicked_pin.clickpatch.remove()
            except:
                pass
            
        self.pinselection_index = i
        case_num = int(self.case_cbox.currentIndex())
        self.clicked_pin = self.pinobjects[case_num][i]
        self.clicked_pin.set_clickpatch()
        
        # mark enr pin
        #LFU = self.pinobjects[case_num][i].LFU
        LFU = self.clicked_pin.LFU
        self.mark_enrpin(self.enrpinlist[case_num][LFU - 1])

        self.canvas.draw()
        self.plot_update()

    def mark_enrpin(self, pin, edge_color=(0.4, 0.4, 0.4)):

        if hasattr(self, "marked_enrpin"):
            try:
                self.marked_enrpin.clickpatch.remove()
            except:
                pass
        self.marked_enrpin = pin
        self.marked_enrpin.set_clickpatch(edge_color=edge_color)

    def enr_add(self):
        self.enr_update("add")
        
    def enr_sub(self):
        self.enr_update("sub")

    def enr_update(self, mod="add"):
        """Update pin enrichment"""

        #print "update pin"
        #sender = QtCore.QObject.sender(self)
        #label = str(sender.text())
        #LFU = int(label.replace("#", ""))
        
        case_num = int(self.case_cbox.currentIndex())
        bundle = self.bunlist[self.ibundle]

        if (hasattr(bundle.data, "segment_connect_list") and
            bundle.data.segment_connect_list[case_num]):
            ncases = len(self.pinobjects)
            for iseg in range(ncases):
                if bundle.data.segment_connect_list[iseg]:
                    self.enr_modify(mod, iseg)
        else:
            self.enr_modify(mod, case_num)

        self.canvas.draw()
        self.enr_fields_update()  # Update info fields

    def enr_fields_update(self):
        """Update enr value in info fields"""

        iseg = int(self.case_cbox.currentIndex())
        istate = self.ibundle
        bundle = self.bunlist[istate]

        # Update enr for all segments
        LFU_list = []
        FUE_list = []
        for i, segment in enumerate(bundle.segments):
            LFU = self.__lfumap(i)
            FUE = self.__fuemap(i)
            segment.ave_enr_calc(LFU, FUE)
            if not hasattr(segment.data, "ave_enr"):  # save orig. calc
                segment.data.ave_enr = segment.ave_enr
            LFU_list.append(LFU)
            FUE_list.append(FUE)
        
        segment = bundle.segments[iseg]
        #self.ave_enr_text.setText("%.5f" % segment.ave_enr)
        orig_seg_enr = self.bunlist[0].segments[iseg].data.ave_enr
        diff_seg_enr = segment.ave_enr - orig_seg_enr
        formstr = '{0:.4f} ({1:+.4f})'.format(segment.ave_enr, diff_seg_enr)
        self.ave_enr_text.setText(formstr)
        #self.ave_denr_text.setText("%.5f" % diff_seg_enr)
        
        # Update bundle enr
        bundle_enr = bundle.ave_enr_calc()
        if not hasattr(bundle, "ave_enr"):
            bundle.ave_enr = bundle_enr  # save orig. calc
        
        # self.bundle_enr_text.setText("%.5f" % bundle_enr)
        orig_bundle_enr = self.bunlist[0].ave_enr
        diff_bundle_enr = bundle_enr - orig_bundle_enr
        formstr = '{0:.4f} ({1:+.4f})'.format(bundle_enr, diff_bundle_enr)
        self.bundle_enr_text.setText(formstr)
        #self.bundle_denr_text.setText("%.5f" % diff_bundle_enr)

        # Update number of pin types
        fuetype = self.bunlist[0].data.fuetype
        pins = PinCount(LFU_list, FUE_list, fuetype)
        formstr = '{0:d}'.format(pins.noofpintypes)
        self.rod_types_text.setText(formstr)

        self.report_update()

    def enr_modify(self, mod, case_num=None, ipin=None):
        halfsym = True
        if case_num is None:
            case_num = int(self.case_cbox.currentIndex())
        ivec = []
        # ipin = self.pinselection_index
        # ivec.append(ipin)
        if ipin is None:
            ipin = self.casecor_pin(case_num)
        if np.isnan(ipin):
            return
        ivec.append(ipin)
        if halfsym:
            isym = self.halfsym_pin(ivec[0], case_num)
            if isym != ivec[0]:
                ivec.append(isym)
        for i in ivec:
            # print "Increase enrichment for pin " + str(i)
            #pinEnr = self.pinobjects[case_num][i].ENR
            #pinBA = self.pinobjects[case_num][i].BA
            pinLFU = self.pinobjects[case_num][i].LFU
            
            #for j, x in enumerate(self.enrpinlist[case_num]):
            #    if np.isnan(x.BA):
            #        x.BA = 0.0
            #    if x.ENR == pinEnr and x.BA == pinBA:
            #        break
            if mod == "add":
                if pinLFU < len(self.enrpinlist[case_num]):
                    self.__pinenr_update(i, pinLFU + 1, case_num) 
                #if j < len(self.enrpinlist[case_num]) - 1:
                #    self.__pinenr_update(i, j + 1, case_num)
            elif mod == "sub":
                if pinLFU > 1:
                    self.__pinenr_update(i, pinLFU - 1, case_num)
                #if j > 0:
                #    self.__pinenr_update(i, j - 1, case_num)

    def __pinenr_update(self, i, pinLFU, case_num=None):
        # i = self.pinselection_index
        if case_num is None:
            case_num = int(self.case_cbox.currentIndex())
        j = pinLFU - 1
        self.pinobjects[case_num][i].LFU = pinLFU
        self.pinobjects[case_num][i].ENR = self.enrpinlist[case_num][j].ENR
        
        if np.isnan(self.enrpinlist[case_num][j].BA):
            self.pinobjects[case_num][i].BA = 0.0
        else:
            self.pinobjects[case_num][i].BA = self.enrpinlist[case_num][j].BA

        if case_num == int(self.case_cbox.currentIndex()):
            fc = self.enrpinlist[case_num][j].circle.get_facecolor()
            self.pinobjects[case_num][i].circle.set_facecolor(fc)
            
            text = self.enrpinlist[case_num][j].text.get_text()
            if str(self.param_cbox.currentText()) == 'ENR':
                self.pinobjects[case_num][i].text.remove()
                self.pinobjects[case_num][i].set_text(text)
        
        # self.bundle.cases[case_num].states[-1].LFU = self.__lfumap(case_num)
        # self.dataobj.cases[case_num].qcalc[0].LFU = self.__lfumap(case_num)
        # self.canvas.draw()

    def __lfumap(self, iseg):
        """Creating LFU map from pinobjects"""
        
        # print "Creating LFU map"
        # case_num = int(self.case_cbox.currentIndex())
        
        # Initialize new LFU map and fill with zeros
        LFU_old = self.bunlist[-1].segments[iseg].data.LFU
        # LFU_old = self.bundle.cases[case_num].states[-1].LFU
        LFU = np.zeros(LFU_old.shape).astype(int)
        
        k = 0
        for i in xrange(LFU.shape[0]):
            for j in xrange(LFU.shape[1]):
                if LFU_old[i, j] > 0:
                    LFU[i, j] = self.pinobjects[iseg][k].LFU
                    k += 1
        return LFU

    def __fuemap(self, iseg):
        """Creating FUE map from enr level pins"""

        FUE_old = self.bunlist[-1].segments[iseg].data.FUE
        #FUE_old = self.bundle.cases[case_num].states[-1].FUE
        nfue = len(self.enrpinlist[iseg])
        FUE = np.zeros((nfue, FUE_old.shape[1])).astype(float)
        for i in xrange(nfue):
            FUE[i, 0] = i + 1
            FUE[i, 1] = self.enrpinlist[iseg][i].DENS
            FUE[i, 2] = self.enrpinlist[iseg][i].ENR
            FUE[i, 3] = self.enrpinlist[iseg][i].BAindex
            FUE[i, 4] = self.enrpinlist[iseg][i].BA
        return FUE

    def __bamap(self, iseg):
        """Creating BA map from pinobjects"""

        # Initialize new BA map and fill with zeros
        LFU = self.bunlist[-1].segments[iseg].data.LFU
        #LFU = self.bundle.cases[case_num].states[-1].LFU
        BA = np.zeros(LFU.shape).astype(float)

        k = 0
        for i in range(BA.shape[0]):
            for j in range(BA.shape[1]):
                if LFU[i, j] > 0:
                    BA[i, j] = self.pinobjects[iseg][k].BA
                    k += 1
        return BA

    def replace_original_design(self):
        """replacing original with current design"""
        ibundle = self.ibundle
        bundle = self.bunlist[ibundle]
        self.bunlist = []
        self.bunlist.append(bundle)
        self.ibundle = 0
        if hasattr(self, "biascalc"):
            del self.biascalc  # bias calc should be updated

    def generate_inpfiles(self):
        """Generate new .inp files"""
        
        istate = self.ibundle
        bundle = self.bunlist[istate]

        LFU = []
        FUE = []
        TIT = []
        caxfiles = []
        for i, segment in enumerate(bundle.segments):
            LFU.append(self.__lfumap(i))
            FUE.append(self.__fuemap(i))
            TIT.append(segment.data.title)
            caxfiles.append(segment.data.caxfile)

        cinp = Casinp(caxfiles, LFU, FUE, TIT, verbose=False)
        flag = cinp.existfiles()
        if flag > 0 and flag < 1000:  # overwrite existing files?
            msgBox = QtGui.QMessageBox()
            msg = "Files already exist! Overwrite?"
            status = msgBox.information(self, "CASMO input files",
                                        msg, QtGui.QMessageBox.Yes |
                                        QtGui.QMessageBox.Cancel)
            if status == QtGui.QMessageBox.Cancel:
                return

        cinp.createinp(verbose=False)
        if self.verbose:
            print "Generated files:"
            for fname in cinp.newinpfiles:
                print fname

        msgBox = QtGui.QMessageBox()
        msg = "Files were successfully generated!"
        status = msgBox.information(self, "CASMO input files",
                                    msg, QtGui.QMessageBox.Ok)
    
    #def complete_calc(self):
    #    """Performing complete calculation using input templates"""
    #    print "Performing complete calculation..."
    #    istate = self.ibundle
    #    bundle = Bundle(parent=self.bunlist[0])  # set parent to bundle
    #    
    #    iseg = int(self.case_cbox.currentIndex())
    #    if hasattr(self.params, 'cas_version'):
    #        c4ver = self.params.cas_version
    #    else:
    #        c4ver = "2.10.21P_VAT_1.3"
    #    if hasattr(self.params, 'cas_neulib'):
    #        neulib = self.params.cas_neulib
    #    else:
    #        neulib = "j20200"
    #    if hasattr(self.params, 'cas_gamlib'):
    #        gamlib = self.params.cas_gamlib
    #    else:
    #        gamlib = "galb410"
    #
    #    bundle.segments[iseg].complete_calc(c4ver=c4ver, neulib=neulib, 
    #                                        gamlib=gamlib)

    def cas_calc(self):
        """Performing ordinary CASMO calculations..."""

        self.thread = RunC4Thread(self)
        self.connect(self.thread, QtCore.SIGNAL('finished()'), 
                         self.__cas_calc_finished)
        self.thread.start()
        self.statusBar().showMessage("Running Casmo...")

        self.setCursor(QtCore.Qt.WaitCursor)

        self.progressbar = ProgressBar()
        self.progressbar.setWindowTitle("Running Casmo")
        xpos = self.pos().x() + self.width()/2 - self.progressbar.width()/2
        ypos = self.pos().y() + self.height()/2 - self.progressbar.height()/2
        self.progressbar.move(xpos, ypos)
        self.progressbar.show()
        self.progressbar.button.clicked.connect(self.__killThread)

        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), 
                     self.__progressbar_update)
        self.progressbar._value = 1
        self.timer.start(2000)

        ##istate = self.ibundle

        ## create new bundle
        #bundle = Bundle(parent=self.bunlist[0])

        ## update bundle attributes
        #voi = None
        #chanbow = self.chanbow_sbox.value() / 10  # mm -> cm
        #nsegs = len(bundle.segments)
        #for iseg in xrange(nsegs):
        #    LFU = self.__lfumap(iseg)
        #    FUE = self.__fuemap(iseg)
        #    BA = self.__bamap(iseg)
        #    bundle.segments[iseg].set_data(LFU, FUE, BA, voi, chanbow)
        
        ## set calc. parameters
        #model = "C4E"
        #c4ver = self.params.cas_version
        #neulib = self.params.cas_neulib
        #gamlib = self.params.cas_gamlib
        #grid = True if self.params.cas_cpu == "grid" else False
        #keepfiles = self.params.cas_keepfiles

        #bundle.new_calc(model=model, c4ver=c4ver, neulib=neulib, 
        #                gamlib=gamlib, grid=grid, keepfiles=keepfiles)
        #bundle.new_btf()
        #self.bunlist.append(bundle)
        
    def __cas_calc_finished(self):
        """C4 calc finished"""

        self.ibundle = len(self.bunlist) - 1
        self.fig_update()
        self.setCursor(QtCore.Qt.ArrowCursor)

        self.timer.stop()
        self.progressbar.update(100)
        self.progressbar.setWindowTitle("Casmo run completed")
        self.progressbar.button.setText("Ok")
        self.progressbar.button.clicked.disconnect(self.__killThread)
        self.progressbar.button.clicked.connect(self.progressbar.close)
        self.statusBar().showMessage("Done!", 2000)

    def quick_calc(self):
        """Performing perturbation calculation"""
        
        self.thread = QuickCalcThread(self)
        self.connect(self.thread, QtCore.SIGNAL('finished()'), 
                     self.__quick_calc_finished)
        self.thread.start()
        self.statusBar().showMessage("Running quick calc...")

        self.setCursor(QtCore.Qt.WaitCursor)
        
        # remove irrelevant bundle calcs
        while len(self.bunlist) > self.ibundle + 1:
            del self.bunlist[-1]
        
        while len(self.bunlist) > 2:  # limit num of bundles stored in memory
            del self.bunlist[1]
            self.ibundle = len(self.bunlist) - 1
        
        self.progressbar = ProgressBar(button=False)
        self.progressbar.setWindowTitle("Running Quick calc")
        xpos = self.pos().x() + self.width()/2 - self.progressbar.width()/2
        ypos = self.pos().y() + self.height()/2 - self.progressbar.height()/2
        self.progressbar.move(xpos, ypos)
        self.progressbar.show()

        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), 
                     self.__progressbar_update)
        self.progressbar._value = 1
        self.timer.start(150)

#        # Set pert. calc parameters
#        if hasattr(self.params, "pert_model"):
#            pert_model = self.params.pert_model
#        else:
#            pert_model = "C3"
#        if hasattr(self.params, "pert_depmax"):
#            pert_depmax = self.params.pert_depmax
#        else:
#            pert_depmax = None
#        if hasattr(self.params, "pert_depthres"):
#            pert_depthres = self.params.pert_depthres
#        else:
#            pert_depthres = None
#        if hasattr(self.params, "pert_voi"):
#            pert_voi = self.params.pert_voi
#        else:
#            pert_voi = None
        
#        if not hasattr(self, "biascalc"):  # make bias calc?
#            print "Performing reference calculation..."
#            self.biascalc = Bundle(parent=self.bunlist[0])
#            #if self.biascalc.data.voi is not None:
#            #    for s in self.biascalc.segments:
#            #        s.set_data(voi=self.biascalc.data.voi)
#            #dep_max = self.biascalc.data.dep_max
#            #dep_thres = self.biascalc.data.dep_thres
#            #model = self.biascalc.data.model
#            self.biascalc.new_calc(model=pert_model, dep_max=pert_depmax,
#                                   dep_thres=pert_depthres, voi=pert_voi)
#            #self.biascalc.new_btf()
#        
#        # New perturbation calc
#        bundle = Bundle(parent=self.bunlist[0])  # parent is set to orig bundle
#        nsegments = len(bundle.segments)
#
#        #voi = bundle.data.voi
#        voi = None
#        chanbow = self.chanbow_sbox.value() / 10  # mm -> cm
#        for iseg in xrange(nsegments):
#            LFU = self.__lfumap(iseg)
#            FUE = self.__fuemap(iseg)
#            BA = self.__bamap(iseg)
#            bundle.segments[iseg].set_data(LFU, FUE, BA, voi, chanbow)
#        #dep_max = bundle.data.dep_max
#        #dep_thres = bundle.data.dep_thres
#        #model = bundle.data.model
#        bundle.new_calc(model=pert_model, dep_max=pert_depmax, 
#                        dep_thres=pert_depthres, voi=pert_voi)
#
#        if pert_voi is None:
#            bundle = self.bias_subtract(bundle)
#        else:
#            bundle = self.bias_subtract_svoi(bundle)
#
        ## remove bias from perturbation calc
        #for iseg in xrange(len(bundle.segments)):
        #    pts = bundle.segments[iseg].statepoints
        #    burnlist = [p.burnup for p in pts]
        #    
        #    pts0 = [p for p in self.bunlist[0].segments[iseg].statepoints 
        #            if p.burnup in burnlist]
        #    pts1 = [p for p in self.biascalc.segments[iseg].statepoints 
        #            if p.burnup in burnlist]
        #    npst = bundle.segments[iseg].data.npst
        #    Nburnpts = len(pts)
        #    POW = np.zeros((npst, npst, Nburnpts))
        #    kinf = np.zeros(Nburnpts)
        #    for i in xrange(len(pts)):  # bias subtraction
        #        dPOW = pts[i].POW - pts1[i].POW
        #        POW[:, :, i] = pts0[i].POW + dPOW
        #        dkinf = pts[i].kinf - pts1[i].kinf
        #        kinf[i] = pts0[i].kinf + dkinf
        #  
        #    fint = bundle.segments[iseg].fintcalc(POW)
        #    burnup = np.array(burnlist)
        #    EXP = bundle.segments[iseg].expcalc(POW, burnup)
        #    for i in xrange(Nburnpts):
        #        bundle.segments[iseg].statepoints[i].POW = POW[:, :, i]
        #        bundle.segments[iseg].statepoints[i].EXP = EXP[:, :, i]
        #        bundle.segments[iseg].statepoints[i].fint = fint[i]
        #        bundle.segments[iseg].statepoints[i].kinf = kinf[i]
        
#        bundle.new_btf()
#        self.bunlist.append(bundle)
        #self.ibundle = len(self.bunlist) - 1
        #self.fig_update()
        #self.setCursor(QtCore.Qt.ArrowCursor)

    def __quick_calc_finished(self):
        self.ibundle = len(self.bunlist) - 1
        self.fig_update()
        self.setCursor(QtCore.Qt.ArrowCursor)
        
        self.timer.stop()
        self.progressbar.update(100)
        time.sleep(1)
        self.progressbar.close()
        self.statusBar().showMessage("Done!", 2000)

    def bias_subtract(self, bundle):
        """remove bias from perturbation calc"""

        for iseg in xrange(len(bundle.segments)):
            pts = bundle.segments[iseg].statepoints
            burnlist = [p.burnup for p in pts]
            
            pts0 = [p for p in self.bunlist[0].segments[iseg].statepoints 
                    if p.burnup in burnlist]
            pts1 = [p for p in self.biascalc.segments[iseg].statepoints 
                    if p.burnup in burnlist]
            npst = bundle.segments[iseg].data.npst
            Nburnpts = len(pts)
            POW = np.zeros((npst, npst, Nburnpts))
            kinf = np.zeros(Nburnpts)
            for i in xrange(len(pts)):  # bias subtraction
                dPOW = pts[i].POW - pts1[i].POW
                POW[:, :, i] = pts0[i].POW + dPOW
                dkinf = pts[i].kinf - pts1[i].kinf
                kinf[i] = pts0[i].kinf + dkinf
          
            fint = bundle.segments[iseg].fintcalc(POW)
            burnup = np.array(burnlist)
            EXP = bundle.segments[iseg].expcalc(POW, burnup)
            for i in xrange(Nburnpts):
                bundle.segments[iseg].statepoints[i].POW = POW[:, :, i]
                bundle.segments[iseg].statepoints[i].EXP = EXP[:, :, i]
                bundle.segments[iseg].statepoints[i].fint = fint[i]
                bundle.segments[iseg].statepoints[i].kinf = kinf[i]

        return bundle

    def bias_subtract_svoi(self, bundle):
        """remove bias from single voi perturbation calc"""
        
        pbundle = Bundle(parent=bundle)

        for iseg in xrange(len(bundle.segments)):

            voi = bundle.segments[iseg].data.voilist[0]
            npst = bundle.segments[iseg].data.npst

            pts = bundle.segments[iseg].statepoints
            burnlist = [p.burnup for p in pts]

            # Only use state points where voi = vhi
            idx = next((i for i, p in 
                       enumerate(self.bunlist[0].segments[iseg].statepoints)
                       if p.voi != p.vhi), None)
            
            pts0 = [p for p in self.bunlist[0].segments[iseg].statepoints[:idx]
                    if p.burnup in burnlist]
            
            pts1 = [p for p in self.biascalc.segments[iseg].statepoints
                    if p.burnup in burnlist]
            
            Nburnpts = len(pts0)
            POW = np.zeros((npst, npst, Nburnpts))
            kinf = np.zeros(Nburnpts)
            
            for i in xrange(len(pts0)):
                j = bundle.segments[iseg].findpoint(burnup=pts0[i].burnup,
                                                    voi=voi, vhi=voi)
                dPOW = pts[j].POW - pts1[j].POW
                POW[:, :, i] = pts0[i].POW + dPOW
                dkinf = pts[j].kinf - pts1[j].kinf
                kinf[i] = pts0[i].kinf + dkinf
            
            fint = pbundle.segments[iseg].fintcalc(POW)
            burnup = np.array([p.burnup for p in pts0])
            EXP = pbundle.segments[iseg].expcalc(POW, burnup)

            statepoints = copy.deepcopy(pts0)
            for i, p in enumerate(statepoints):
                p.POW = POW[:, :, i]
                p.EXP = EXP[:, :, i]
                p.fint = fint[i]
                p.kinf = kinf[i]
            
            voilist = self.bunlist[0].segments[iseg].data.voilist
            pbundle.segments[iseg].data.voilist = voilist
            pbundle.segments[iseg].statepoints = statepoints
                
        return pbundle
        
        
    def fig_update(self):
        """ Redraw figure and update values"""
        
        # self.on_draw()
        self.axes.clear()
        self.draw_fuelmap()
        self.set_pinvalues()
        self.toggle_pin_bgcolors()
        
        # Update info field
        iseg = int(self.case_cbox.currentIndex())
        sim = self.bunlist[0].segments[iseg].data.sim
        #sim = self.bundle.cases[case_num].states[0].sim
        text = sim.replace("SIM", "").replace("'", "").strip()
        self.sim_info_field.setText(text)
        #self.sim_text.setText(text)
        self.enr_fields_update()

        # Mark pin with maximum value
        #self.mark_maxpin()

    def mark_maxpins(self, param=None):
        """Mark pin with maximum value"""

        self.remove_maxpins()

        iseg = int(self.case_cbox.currentIndex())
        ipoint = int(self.point_sbox.value())
        bundle = self.bunlist[self.ibundle]
        segment = bundle.segments[iseg]
        if param == None:
            param = str(self.param_cbox.currentText())
        if param not in ["FINT", "EXP", "BTF"]:
            #param = "FINT"
            return
        if param == "FINT":
            M = segment.statepoints[ipoint].POW
        elif param == "EXP":
            M = segment.statepoints[ipoint].EXP
        elif param == "BTF":
            burnup = segment.statepoints[ipoint].burnup
            btf_burnpoints = bundle.btf.burnpoints
            index_array = np.where(btf_burnpoints == burnup)[0]
            if len(index_array) > 0:
                ipoint = index_array[0]
                M = bundle.btf.DOX[ipoint, :, :]
            else:
                s = np.shape(segment.statepoints[ipoint].POW)
                M = np.zeros(s)
        
        #ncols = M.shape[0]
        #index = M.argmax()
        #ipos = [index / ncols , index % ncols]  # [i, j]

        self.maxpins = []
        M_max = M.max()
        if M_max > 0.00001:
            #i_arr, j_arr = np.where(M == M.max())
            i_arr, j_arr = np.where(M > M.max()*0.99999)
            for i, j in zip(i_arr, j_arr):
                maxpin = next(p for p in self.pinobjects[iseg] 
                                   if p.pos == [i, j])
                maxpin.set_maxpin_patch()
                self.maxpins.append(maxpin)
        
            #ipos = pos_tuple[0].tolist()
            #ipos = ipos_array.tolist()
            #self.maxpin = next(p for p in self.pinobjects[iseg] 
            #                   if p.pos == ipos)
            #self.maxpin.set_maxpin_patch()

        #pos_tuple = np.where(M == M.max())
        #ipos = pos_tuple[0].tolist()
        #mpin = next(p for p in self.pinobjects[iseg] if p.pos == ipos)
        
        
        #self.toggle_pin_bgcolors()  # must update pin alpha values
        #if self.maxpin.rectangle.get_alpha() > 0.0:
        #    fc = self.maxpin.rectangle.get_fc()
        #    edge_color = (1 - np.array(fc)).tolist()  # complement color
        #    self.maxpin.set_maxpin_patch(edge_color=(0, 0, 0))
        #else:
        #    self.maxpin.set_maxpin_patch()

    def on_draw(self):
        """Setup the figure axis"""

        # clear the axes and redraw the plot anew
        #
        # self.fig.clf()
        self.axes.clear()
        self.axes.axis('equal')
        # self.axes.set_xlim(0,1)
        # self.axes.set_ylim(0,1)
        # self.axes.axis('equal')
        
        # self.axes.set_position([0,0,1,1])
        # self.axes.set_xlim(0,1.2)
        # self.axes.set_ylim(0,1)
        self.axes.set_position([0, 0, 1, 1])
        # self.axes.set_visible(False)
        self.axes.set_frame_on(False)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        
        # self.axes.grid(self.grid_cb.isChecked())

        # xmax = self.slider.value()
        # self.axes.set_xlim(0,xmax)

        # self.axes.axis('equal')
        
        # self.canvas.draw()

    def clear_project(self):
        """Clear current project"""
        
        msgBox = QtGui.QMessageBox()
        status = msgBox.information(self, "Clear current project",
                                    "Unsaved data will be lost!\n\nContinue?",
                                    QtGui.QMessageBox.Yes |
                                    QtGui.QMessageBox.Cancel)
        if status == QtGui.QMessageBox.Yes:
            self.clear_data()
            self.widgets_setenabled(False)

    def clear_data(self):
        """Clear fuel map figure axes and delete bundle- and GUI field data"""

        self.param_cbox.setCurrentIndex(0)
        #self.param_cbox.setEnabled(False)

        self.point_sbox.setValue(0)
        #self.point_sbox.setEnabled(False)

        self.chanbow_sbox.setValue(0)
        #self.chanbow_sbox.setEnabled(False)

        widgets = [self.case_cbox, self.sim_info_field, self.rod_types_text,
                   self.ave_enr_text, self.bundle_enr_text,
                   self.burnup_text, self.kinf_text, self.fint_text,
                   self.btf_text, self.voi_vhi_text, self.tfu_tmo_text]
        for w in widgets:
            w.clear()

        self.show_cmap.setChecked(False)
        
        #self.chanbow_sbox.setValue(0)
        #self.chanbow_sbox.setEnabled(False)

        self.table.clearContents()

        if hasattr(self, "bundle"):
            del self.bundle
        
        if hasattr(self, "pinobjects"):
            del self.pinobjects

        # Clear and restore figure
        self.axes.clear()  # Clears the figure axes
        self.fig.set_facecolor('0.75')  # set facecolor to gray
        #self.fig.clf()
        #self.fig.clear()
        
    def draw_fuelmap(self):
        """Draw fuel map"""

        #self.fig.set_facecolor((1, 1, 0.8784))  # Light yellow
        self.fig.set_facecolor("#CFEECF")  # Tea green

        # Draw outer rectangle
        rect = mpatches.Rectangle((0.035, 0.035), 0.935, 0.935,
                                  fc=(0.8, 0.898, 1), ec=(0.3, 0.3, 0.3))
        self.axes.add_patch(rect)
        
        # Draw control rods
        rodrect_v = mpatches.Rectangle((0.011, 0.13), 0.045, 0.77,
                                       ec=(0.3, 0.3, 0.3))
        rodrect_v.set_fill(False)
        self.axes.add_patch(rodrect_v)
        pp = [[0.011, 0.17], [0.056, 0.17]]
        poly = mpatches.Polygon(pp)
        poly.set_closed(False)
        self.axes.add_patch(poly)
        pp = [[0.011, 0.86], [0.056, 0.86]]
        poly = mpatches.Polygon(pp)
        poly.set_closed(False)
        self.axes.add_patch(poly)

        rodrect_h = mpatches.Rectangle((0.1, 0.95), 0.77, 0.045,
                                       ec=(0.3, 0.3, 0.3))
        rodrect_h.set_fill(False)
        self.axes.add_patch(rodrect_h)
        pp = [[0.14, 0.95], [0.14, 0.995]]
        poly = mpatches.Polygon(pp)
        poly.set_closed(False)
        self.axes.add_patch(poly)
        pp = [[0.83, 0.95], [0.83, 0.995]]
        poly = mpatches.Polygon(pp)
        poly.set_closed(False)
        self.axes.add_patch(poly)

        # a fancy box with round corners (pad).
        p_fancy = mpatches.FancyBboxPatch((0.12, 0.12), 0.77, 0.77,
                                          boxstyle="round,pad=0.04",
                                          # fc=(0.85, 1, 1),
                                          fc=(1, 1, 1),
                                          ec=(0.3, 0.3, 0.3))
        p_fancy.set_linewidth(4.0)
        self.axes.add_patch(p_fancy)
        
        if self.bunlist[0].data.fuetype == 'OPT2':
            s96o2(self)
        elif self.bunlist[0].data.fuetype == 'OPT3':
            s96o2(self)
        elif self.bunlist[0].data.fuetype == 'A10XM':
            a10xm(self)
        elif self.bunlist[0].data.fuetype == 'A10B':
            a10xm(self)
        elif self.bunlist[0].data.fuetype == 'AT11':
            at11(self)

        # Draw symmetry line
        # pp = [[0.035, 0.965], [0.965, 0.035]]
        # poly = mpatches.Polygon(pp)
        # poly.set_closed(False)
        # self.axes.add_patch(poly)
        
    def startpoint(self, case_id):
        voi_val = int(self.voi_cbox.currentText())
        vhi_val = int(self.vhi_cbox.currentText())
        type_val = str(self.type_cbox.currentText())

        case = self.cas.cases[case_id]
        if type_val == 'CCl':
            idx0 = case.findpoint(tfu=293)
            voi = case.statepts[idx0].voi
            vhi = case.statepts[idx0].vhi
            voi_index = [i for i, v in enumerate(self.voilist)
                         if int(v) == voi][0]
            vhi_index = [i for i, v in enumerate(self.vhilist)
                         if int(v) == vhi][0]
            self.voi_cbox.setCurrentIndex(voi_index)
            self.vhi_cbox.setCurrentIndex(vhi_index)
        else:
            idx0 = case.findpoint(voi=voi_val, vhi=vhi_val)
        return idx0

    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        r = 1.0  # resolution factor
        self.dpi = 100 * r
        #self.fig = Figure((6, 5), dpi=self.dpi, facecolor=None)
        #self.fig = Figure((6, 5), dpi=self.dpi)
        self.fig = Figure((6 / r, 5 / r), dpi=self.dpi)
        # self.fig = Figure((6, 5), dpi=self.dpi, facecolor=(1,1,1))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.setParent(self.main_frame)
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)
        self.canvas.setMinimumWidth(500)
        self.canvas.setMinimumHeight(416)
        
        cvbox = QtGui.QVBoxLayout()
        cvbox.addWidget(self.canvas)
        canvasGbox = QtGui.QGroupBox()
        canvasGbox.setStyleSheet("QGroupBox { background-color: rgb(200, 200,\
        200); border:1px solid gray; border-radius:5px;}")
        canvasGbox.setLayout(cvbox)

        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        # self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        # self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        #
 
        #self.sim_info_field = QtGui.QLineEdit()
        #self.sim_info_field.setSizePolicy(QtGui.QSizePolicy.Minimum,
        #                                  QtGui.QSizePolicy.Minimum)
        #self.sim_info_field.setReadOnly(True)
        sim_hbox = QtGui.QHBoxLayout()
        self.sim_info_field = InfoLabel(width=210)
        sim_hbox.addWidget(self.sim_info_field)

        param_label = QtGui.QLabel('Parameter:')
        self.param_cbox = QtGui.QComboBox()
        paramlist = ['ENR', 'FINT', 'EXP', 'BTF']
        #paramlist = ['ENR', 'FINT', 'EXP', 'BTF', 'BTFP', 'XFL1', 'XFL2',
        #             'ROD', 'LOCK']
        for i in paramlist:
            self.param_cbox.addItem(i)
        # self.connect(self.param_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)
        param_hbox = QtGui.QHBoxLayout()
        param_hbox.addWidget(param_label)
        param_hbox.addWidget(self.param_cbox)
        self.connect(self.param_cbox,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.set_pinvalues)

        case_label = QtGui.QLabel('Segment:')
        self.case_cbox = QtGui.QComboBox()
        case_hbox = QtGui.QHBoxLayout()
        case_hbox.addWidget(case_label)
        case_hbox.addWidget(self.case_cbox)
        self.connect(self.case_cbox, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.fig_update)

        point_label = QtGui.QLabel('Point number:')
        self.point_sbox = QtGui.QSpinBox()
        self.point_sbox.setMinimum(0)
        self.point_sbox.setMaximum(10000)
        point_hbox = QtGui.QHBoxLayout()
        point_hbox.addWidget(point_label)
        point_hbox.addWidget(self.point_sbox)
        self.connect(self.point_sbox, QtCore.SIGNAL('valueChanged(int)'),
                     self.set_pinvalues)

        #self.enr_plus_button = QtGui.QPushButton("+ enr")
        #self.enr_minus_button = QtGui.QPushButton("- enr")
        #enr_hbox = QtGui.QHBoxLayout()
        #enr_hbox.addWidget(self.enr_minus_button)
        #enr_hbox.addWidget(self.enr_plus_button)
        #self.connect(self.enr_plus_button, QtCore.SIGNAL('clicked()'),
        #             self.enr_add)
        #self.connect(self.enr_minus_button, QtCore.SIGNAL('clicked()'),
        #             self.enr_sub)
        #self.enr_case_cb = QtGui.QCheckBox("All segments")
        #self.enr_case_cb.setChecked(False)
        #enr_case_hbox = QtGui.QHBoxLayout()
        #enr_case_hbox.addWidget(self.enr_case_cb)

        #self.calc_quick_button = QtGui.QPushButton("Pert. calc")
        #self.calc_full_button = QtGui.QPushButton("Full calc")
        #calc_hbox = QtGui.QHBoxLayout()
        #calc_hbox.addWidget(self.calc_quick_button)
        #calc_hbox.addWidget(self.calc_full_button)
        #self.connect(self.calc_quick_button, QtCore.SIGNAL('clicked()'),
        #             self.quick_calc)

        chanbow_hbox = QtGui.QHBoxLayout()
        self.chanbow_sbox = QtGui.QDoubleSpinBox()
        self.chanbow_sbox.setRange(-3, 3)
        self.chanbow_sbox.setSingleStep(0.25)
        self.chanbow_sbox.setSuffix(" mm")
        chanbow_hbox.addWidget(QtGui.QLabel("Channel bow:"))
        chanbow_hbox.addWidget(self.chanbow_sbox)

        #self.bgcolors_cb = QtGui.QCheckBox("Show color map")
        #self.bgcolors_cb.setChecked(False)
        #bgcolors_hbox = QtGui.QHBoxLayout()
        #bgcolors_hbox.addWidget(self.bgcolors_cb)
        #self.connect(self.bgcolors_cb, QtCore.SIGNAL('clicked()'),
        #             self.toggle_pin_bgcolors)
        
        voi_hbox = QtGui.QHBoxLayout()
        type_label = QtGui.QLabel('Type:')
        self.type_cbox = QtGui.QComboBox()
        typelist = ['Hot', 'HCr', 'CCl', 'CCr']
        for i in typelist:
            self.type_cbox.addItem(i)
        voi_hbox.addWidget(type_label)
        voi_hbox.addWidget(self.type_cbox)

        # self.connect(self.type_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_index)

        voi_hbox = QtGui.QHBoxLayout()
        voi_label = QtGui.QLabel('VOI:')
        self.voi_cbox = QtGui.QComboBox()
        voi_hbox.addWidget(voi_label)
        voi_hbox.addWidget(self.voi_cbox)
        #self.connect(self.voi_cbox, QtCore.SIGNAL('currentIndexChanged(int)'),
        #             self.fig_update)
        #self.connect(self.voi_cbox, QtCore.SIGNAL('currentIndexChanged(int)'),
        #             self.set_pinvalues)

        # Determine voi index
        # voi = self.cas.cases[self.case_id_current].statepts[0].voi
        # voi_index = [i for i,v in enumerate(self.voilist) if int(v) == voi]
        # voi_index = voi_index[0]
        # self.voi_cbox.setCurrentIndex(voi_index)
        # self.connect(self.voi_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)

        vhi_hbox = QtGui.QHBoxLayout()
        vhi_label = QtGui.QLabel('VHI:')
        self.vhi_cbox = QtGui.QComboBox()
        #self.vhilist = ['0', '40', '80']
        #for v in self.vhilist:
        #    self.vhi_cbox.addItem(str(v))
        vhi_hbox.addWidget(vhi_label)
        vhi_hbox.addWidget(self.vhi_cbox)

        type_hbox = QtGui.QHBoxLayout()
        type_label = QtGui.QLabel('Type:')
        self.type_cbox = QtGui.QComboBox()
        typelist = ['Hot', 'HCr', 'CCl', 'CCr']
        for i in typelist:
            self.type_cbox.addItem(i)
        type_hbox.addWidget(type_label)
        type_hbox.addWidget(self.type_cbox)

        exp_hbox = QtGui.QHBoxLayout()
        exp_label = QtGui.QLabel('EXP:')
        self.exp_cbox = QtGui.QComboBox()
        #self.explist = [0, 0.001, 0.1, 0.5, 1.5, 2, 2.5]
        #for e in self.explist:
        #    self.exp_cbox.addItem(str(e))
        exp_hbox.addWidget(exp_label)
        exp_hbox.addWidget(self.exp_cbox)


        findpoint_gbox = QtGui.QGroupBox()
        findpoint_gbox.setTitle("Find state point")
        findpoint_gbox.setStyleSheet("QGroupBox {border: 1px solid gray;\
        border-radius:5px; font: bold; subcontrol-origin: margin;\
        padding: 10px -5px -5px -5px}")
        findpoint_vbox = QtGui.QVBoxLayout()
        findpoint_vbox.addLayout(voi_hbox)
        findpoint_vbox.addLayout(vhi_hbox)
        findpoint_vbox.addLayout(type_hbox)
        findpoint_vbox.addLayout(exp_hbox)
        findpoint_gbox.setLayout(findpoint_vbox)

        # Determine vhi index
        # vhi = self.cas.cases[self.case_id_current].statepts[0].vhi
        # vhi_index = [i for i,v in enumerate(self.vhilist) if int(v) == vhi]
        # vhi_index = vhi_index[0]
        # self.vhi_cbox.setCurrentIndex(vhi_index)
        # self.connect(self.vhi_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)

        # self.case_cbox.setWhatsThis("What is this?")

        # self.connect(self.case_cbox, SIGNAL('activated(QString)'),
        # self.on_case)
        # self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)
        
        # Info form layout
        info_flo = QtGui.QFormLayout()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Minimum)
        # sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.ave_enr_text.sizePolicy().
        # hasHeightForWidth())
        #self.sim_text = QtGui.QLineEdit()
        #self.sim_text.setSizePolicy(sizePolicy)
        #self.sim_text.setReadOnly(True)
        # text = self.bundle.cases[0].states[0].sim
        # self.sim_text.setText(text)
        #info_flo.addRow("SIM", self.sim_text)

        self.burnup_text = InfoLabel()
        self.burnup_text.setSizePolicy(sizePolicy)
        info_flo.addRow("Burnup", self.burnup_text)

        self.kinf_text = InfoLabel()
        self.kinf_text.setSizePolicy(sizePolicy)
        info_flo.addRow("Kinf", self.kinf_text)

        self.fint_text = InfoLabel()
        self.fint_text.setSizePolicy(sizePolicy)
        info_flo.addRow("Fint", self.fint_text)

        self.btf_text = InfoLabel()
        self.btf_text.setSizePolicy(sizePolicy)
        info_flo.addRow("BTF", self.btf_text)

        self.voi_vhi_text = InfoLabel()
        self.voi_vhi_text.setSizePolicy(sizePolicy)
        #self.voi_vhi_text.setNum(40)
        info_flo.addRow("VOI / VHI", self.voi_vhi_text)

        self.tfu_tmo_text = InfoLabel()
        self.tfu_tmo_text.setSizePolicy(sizePolicy)
        info_flo.addRow("TFU / TMO", self.tfu_tmo_text)
        
        #self.rod_types_text = QtGui.QLineEdit()
        self.rod_types_text = InfoLabel()
        self.rod_types_text.setSizePolicy(sizePolicy)
        #self.rod_types_text.setReadOnly(True)
        info_flo.addRow("Rod types", self.rod_types_text)
        
        #self.ave_enr_text = QtGui.QLineEdit()
        self.ave_enr_text = InfoLabel()
        self.ave_enr_text.setSizePolicy(sizePolicy)
        #self.ave_enr_text.setReadOnly(True)
        info_flo.addRow("Segment w/o U-235", self.ave_enr_text)

        #self.ave_denr_text = QtGui.QLineEdit()
        #self.ave_denr_text.setSizePolicy(sizePolicy)
        #self.ave_denr_text.setReadOnly(True)
        #info_flo.addRow(QtCore.QString("Segment %1 w/o")
        #                .arg(QtCore.QChar(0x0394)), self.ave_denr_text)
        
        #self.bundle_enr_text = QtGui.QLineEdit()
        self.bundle_enr_text = InfoLabel()
        self.bundle_enr_text.setSizePolicy(sizePolicy)
        #self.bundle_enr_text.setReadOnly(True)
        info_flo.addRow("Bundle w/o U-235", self.bundle_enr_text)

        #self.bundle_denr_text = QtGui.QLineEdit()
        #self.bundle_denr_text.setSizePolicy(sizePolicy)
        #self.bundle_denr_text.setReadOnly(True)
        #info_flo.addRow(QtCore.QString("Bundle %1 w/o")
        #                .arg(QtCore.QChar(0x0394)), self.bundle_denr_text)
        
        # Construct table widget instance
        self.table = PinTableWidget(self)

        tvbox = QtGui.QVBoxLayout()
        tvbox.addWidget(self.table)
        tableGbox = QtGui.QGroupBox()
        tableGbox.setStyleSheet("QGroupBox { background-color: rgb(200, 200,\
        200); border:1px solid gray; border-radius:5px;}")
        tableGbox.setLayout(tvbox)
        
        # self.hview = QHeaderView

        # self.tableview = QTableView()
        # self.connect(self.table.horizontalHeader().sectionClicked(),
        # SIGNAL('logicalIndex(int)'),self.openFile)
        # self.connect(QHeaderView.sortIndicatorChanged(),
        # SIGNAL('logicalIndex(int)'),self.openFile)
        
        # self.setpincoords()
        self.table.resizeColumnsToContents()

        # Layout with box sizers
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(sim_hbox)
        vbox.addLayout(case_hbox)
        vbox.addLayout(param_hbox)
        vbox.addLayout(chanbow_hbox)
        #vbox.addLayout(point_hbox)
        #vbox.addLayout(voi_hbox)
        #vbox.addLayout(vhi_hbox)
        #vbox.addLayout(exp_hbox)
        #vbox.addLayout(type_hbox)
        #vbox.addWidget(findpoint_gbox)
        #vbox.addLayout(enr_hbox)
        #vbox.addLayout(enr_case_hbox)
        #vbox.addLayout(calc_hbox)
        #vbox.addLayout(bgcolors_hbox)

        # spacerItem = QSpacerItem(1, 1, QSizePolicy.Minimum,
        # QSizePolicy.Minimum)
        # vbox.addItem(spacerItem)
        vbox.addStretch(1)
        vbox.addLayout(point_hbox)
        vbox.addLayout(info_flo)
        #vbox.addLayout(sim_hbox)
        
        groupbox = QtGui.QGroupBox()
        groupbox.setStyleSheet("QGroupBox { background-color: rgb(200, 200,\
        200); border:1px solid gray; border-radius:5px;}")
        groupbox.setLayout(vbox)

        # for w in [  self.textbox, self.draw_button, self.grid_cb,
        #            slider_label, self.slider]:
        
        # for w in [  type_label, self.type_cbox, voi_label, self.voi_cbox,
        #            vhi_label, self.vhi_cbox]:
        #
        #    vbox.addWidget(w)
        #    vbox.setAlignment(w, Qt.AlignHCenter)
        
        # self.bundle = Bundle()
        # self.bundle.setParent(self.main_frame)

        hbox = QtGui.QHBoxLayout()

        # hbox.addWidget(self.bundle)
        # vbox.addLayout(hbox)
        # vbox.addWidget(self.canvas)
        # hbox2.addWidget(self.mpl_toolbar)
        
        spacerItemH = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Minimum)

        # hbox.addLayout(vbox)
        hbox.addWidget(groupbox)
        # hbox.addItem(spacerItemH)
        # hbox.addWidget(self.canvas)
        hbox.addWidget(canvasGbox)
        # hbox.addItem(spacerItemH)
        hbox.addWidget(tableGbox)
        # hbox.addWidget(self.table)
        # hbox.addItem(spacerItemH)

        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)
    
    def create_status_bar(self):
        self.status_text = QtGui.QLabel("Main window")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")
        
        clear_action = self.create_action("&Clear project...",
                                          shortcut="Ctrl+C",
                                          slot=self.clear_project,
                                          tip="Clear current project",
                                          icon="delete-icon_32x32")

        quit_action = self.create_action("&Quit", slot=self.close,
                                         shortcut="Ctrl+Q",
                                         tip="Close the application",
                                         icon="exit-icon_32x32")

        new_project_action = self.create_action("&New...",
                                                slot=self.open_bundle_dlg,
                                                #slot=self.newProject,
                                                shortcut="Ctrl+N",
                                                tip="Create new bundle",
                                                icon="new-icon_32x32")
        
        open_file_action = self.create_action("&Open...",
                                              slot=self.openFile,
                                              shortcut="Ctrl+O",
                                              tip="Open file",
                                              icon="open-file-icon_32x32")

        save_data_action = self.create_action("&Save project...",
                                              slot=self.saveData,
                                              shortcut="Ctrl+S",
                                              tip="Save data to file",
                                              icon="save-icon_32x32")

        save_file_action = self.create_action("&Export to ascii...",
                                                slot=self.export_to_ascii,
                                                tip="Export data to file",
                                                icon="export-icon_32x32")

        save_figure_action = self.create_action("&Export Figure...",
                                                slot=self.saveFigure,
                                                tip="Export fuel map to file",
                                                icon="export-icon_32x32")
        
        self.add_actions(self.file_menu, (new_project_action, open_file_action,
                                          save_data_action,
                                          clear_action, save_file_action,
                                          save_figure_action, None,
                                          quit_action))

        self.edit_menu = self.menuBar().addMenu("&Edit")

        back = self.create_action("Back", slot=self.back_state,
                                  tip="Back to previous",
                                  icon="arrow-undo-icon_32x32")

        forward = self.create_action("Forward", slot=self.forward_state,
                                     tip="Forward to next",
                                     icon="arrow-redo-icon_32x32")

        reset = self.create_action("Reset...", slot=self.reset_state,
                                   tip="Reset all changes...",
                                   icon="undo-icon_32x32")

        enrichment = self.create_action("Enrichments...",
                                        slot=self.open_enrichment_dlg,
                                        tip="Edit enrichment levels...",
                                        icon="table-icon_32x32")
        
        segment = self.create_action("Segments...",
                                    slot=self.open_segment_dlg,
                                    tip="Edit segment heights...",
                                    icon="layers-icon_32x32")

        enr_plus = self.create_action("Increase enr", slot=self.enr_add,
                                      tip="Increase enrichment",
                                      shortcut=QtCore.Qt.Key_Plus, 
                                      icon="add-icon_32x32")

        enr_minus = self.create_action("Decrease enr", slot=self.enr_sub,
                                       tip="Decrease enrichment",
                                       shortcut=QtCore.Qt.Key_Minus, 
                                       icon="remove-icon_32x32")

        #self.allsegs_update = self.create_action("Update all segments",
        #                                         tip="Update all segments",
        #                                         checkable=True)
        
        quickcalc = self.create_action("Quick calc...",
                                       tip="Quick calc model...",
                                       slot=self.open_pert_dlg,
                                       icon="flame-red-icon_32x32")
        
        preferences = self.create_action("Preferences...",
                                         tip="Preferences...",
                                         icon="preferences-icon_32x32")

        replace = self.create_action("Replace original...",
                                     tip="Replace original design...",
                                     slot=self.replace_original_design,
                                     icon="original-icon_32x32")
        
        self.add_actions(self.edit_menu,
                         (back, forward, None, enr_plus, enr_minus, 
                          None,
                          segment, enrichment, quickcalc, None, replace, 
                          reset, preferences))
        
        self.tools_menu = self.menuBar().addMenu("&Tools")
        plot_action = self.create_action("Plot...", tip="Plot...",
                                         slot=self.open_plotwin,
                                         icon="diagram-icon_32x32")
        
        casmo_action = self.create_action("CASMO...", tip="CASMO...",
                                          slot=self.open_cas_dlg,
                                          icon="grid-icon_32x32")

        casinp_action = self.create_action("Generate inp files",
                                           tip="Generate CASMO input files...",
                                           slot=self.generate_inpfiles,
                                           icon="write-icon_32x32")
        
        data_action = self.create_action("Report...", tip="Fuel report...",
                                         slot=self.open_report_dlg,
                                         icon="document-icon_32x32")
        
        find_action = self.create_action("Find point...",
                                         tip="Find state point...",
                                         shortcut="Ctrl+F",
                                         slot=self.open_findpoint_dlg,
                                         icon="binoculars-icon_32x32")
        
        #table_action = self.create_action("Point table...",
        #                                  tip="Point table...")
        
        #optim_action = self.create_action("Optimization...",
        #                                  tip="BTF optimization...")
        
        egv_action = self.create_action("EGV...", tip="EGV...",
                                        slot=self.open_egv_dlg,
                                        icon="letter-e-icon_32x32")

        self.show_cmap = self.create_action("Show color map", checkable=True,
                                            tip="Show background color map",
                                            slot=self.toggle_pin_bgcolors)

        self.track_maxpin = self.create_action("Track max pins", 
                                               checkable=True,
                                               tip="Mark pins with highest value",
                                               slot=self.toggle_maxpins)

        self.add_actions(self.tools_menu,
                         (plot_action, casmo_action, casinp_action,
                          data_action, find_action, egv_action, 
                          self.show_cmap, self.track_maxpin))

        self.run_menu = self.menuBar().addMenu("&Run")
        self.quickcalc_action = self.create_action("&Quick calc", shortcut="F9",
                                                   slot=self.quick_calc,
                                                   tip="Run quick calc",
                                                   icon="flame-red-icon_32x32")
        self.quickcalc_action.setEnabled(False)

        #smallcalc_action = self.create_action("&Small calc",
        #                                  slot=self.quick_calc,
        #                                  tip="Run small calculation")
        
        #fullcalc_action = self.create_action("&Complete calc...",
        #                                     slot=self.open_fullcalc_dlg,
        #                                     tip="Run complete calculation")
        self.add_actions(self.run_menu, (None, self.quickcalc_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", #shortcut='F1',
                                          slot=self.on_about, tip='About',
                                          icon="help-about-icon_32x32")
        
        self.add_actions(self.help_menu, (about_action,))

        self.menu_actions = [save_data_action, clear_action, save_file_action,
                             save_figure_action, back, forward, reset, 
                             enrichment, segment, enr_plus, enr_minus, 
                             quickcalc, replace, plot_action, casmo_action,
                             casinp_action, data_action, find_action, 
                             # egv_action, quickcalc_action]
                             egv_action]

    def create_toolbar(self):

        exit_icon = self.appdir + "icons/exit-icon_32x32.png"
        exitAction = QtGui.QAction(QtGui.QIcon(exit_icon), 'Exit', self)
        # exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        new_icon = self.appdir + "icons/new-icon_32x32.png"
        newAction = QtGui.QAction(QtGui.QIcon(new_icon),
                                   'Create new bundle', self)
        newAction.setStatusTip('Create a new bundle')
        newAction.triggered.connect(self.open_bundle_dlg)
        #newAction.triggered.connect(self.newProject)
        
        file_icon = self.appdir + "icons/open-file-icon_32x32.png"
        fileAction = QtGui.QAction(QtGui.QIcon(file_icon), 'Open file', self)
        fileAction.setStatusTip('Open file')
        fileAction.triggered.connect(self.openFile)

        save_icon = self.appdir + "icons/save-icon_32x32.png"
        saveAction = QtGui.QAction(QtGui.QIcon(save_icon), 'Save to file', self)
        saveAction.setStatusTip('Save to file')
        saveAction.triggered.connect(self.saveData)
        
        color_icon = self.appdir + "icons/color-icon_32x32.png"
        self.colorAction = QtGui.QAction(QtGui.QIcon(color_icon), 
                                         'Show color map', self)
        self.colorAction.setStatusTip('Show color map')
        self.colorAction.setCheckable(True)
        self.colorAction.triggered.connect(self.toggle_cmap)

        calc_icon = self.appdir + "icons/flame-red-icon_32x32.png"
        self.calcAction = QtGui.QAction(QtGui.QIcon(calc_icon),
                                        'Run quick calc', self)
        self.calcAction.setStatusTip('Run simulation')
        self.calcAction.triggered.connect(self.quick_calc)
        self.calcAction.setEnabled(False)

        pre_icon = self.appdir + "icons/preferences-icon_32x32.png"
        settingsAction = QtGui.QAction(QtGui.QIcon(pre_icon), 'Settings', self)
        settingsAction.setStatusTip('Settings')

        diagram_icon = self.appdir + "icons/diagram-icon_32x32.png"
        plotAction = QtGui.QAction(QtGui.QIcon(diagram_icon), 'Plot', self)
        plotAction.setStatusTip('Open plot window')
        plotAction.triggered.connect(self.open_plotwin)

        find_icon = self.appdir + "icons/binoculars-icon_32x32.png"
        findAction = QtGui.QAction(QtGui.QIcon(find_icon), 'Find state point', 
                                   self)
        findAction.setStatusTip('Find state point')
        findAction.triggered.connect(self.open_findpoint_dlg)
        #findAction.setCheckable(True)

        #arrow_left_icon = "icons/arrow-left-icon_32x32.png"
        arrow_undo_icon =  self.appdir + "icons/arrow-undo-icon_32x32.png"
        backAction = QtGui.QAction(QtGui.QIcon(arrow_undo_icon),
                                   'Back to previous design', self)
        backAction.setStatusTip('Back to previous design')
        backAction.triggered.connect(self.back_state)

        #arrow_forward_icon = "icons/arrow-right-icon_32x32.png"
        arrow_redo_icon =  self.appdir + "icons/arrow-redo-icon_32x32.png"
        forwardAction = QtGui.QAction(QtGui.QIcon(arrow_redo_icon),
                                      'Forward to next design', self)
        forwardAction.setStatusTip('Forward to next design')
        forwardAction.triggered.connect(self.forward_state)
        
        add_icon =  self.appdir + "icons/add-icon_32x32.png"
        addAction = QtGui.QAction(QtGui.QIcon(add_icon),
                                  'Increase enrichment', self)
        addAction.setStatusTip('Increase enrichment') 
        addAction.triggered.connect(self.enr_add)
        sub_icon =  self.appdir + "icons/remove-icon_32x32.png"
        subAction = QtGui.QAction(QtGui.QIcon(sub_icon),
                                  'Decrease enrichment', self)
        subAction.setStatusTip('Decrease enrichment')
        subAction.triggered.connect(self.enr_sub)

        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(newAction)
        toolbar.addAction(fileAction)
        toolbar.addAction(saveAction)
        toolbar.addAction(self.calcAction)
        toolbar.addAction(settingsAction)
        toolbar.addAction(self.colorAction)
        toolbar.addAction(plotAction)
        toolbar.addAction(findAction)
        toolbar.addAction(backAction)
        toolbar.addAction(forwardAction)
        toolbar.addAction(subAction)
        toolbar.addAction(addAction)
        toolbar.addAction(exitAction)

        toolbar.setMovable(False)
        toolbar.setFloatable(True)
        toolbar.setAutoFillBackground(False)

        self.toolbar_actions = [saveAction, self.colorAction,
                                # [saveAction, calcAction, self.colorAction,
                                plotAction, findAction, backAction,
                                forwardAction, subAction, addAction]

    def reset(self):
        self.init_pinobjects()
        self.fig_update()
        self.chanbow_sbox_update()

    def reset_state(self):
        """Reset current state"""
        msgBox = QtGui.QMessageBox()
        status = msgBox.information(self, "Reset",
                                    "Continue?",
                                    QtGui.QMessageBox.Yes |
                                    QtGui.QMessageBox.Cancel)
        if status == QtGui.QMessageBox.Yes:
            self.reset()

    def back_state(self):
        """Back to previous state"""

        nbundles = len(self.bunlist)
        if self.ibundle < 0:
            self.ibundle = self.ibundle + nbundles
        self.ibundle -= 1
        if self.ibundle < 0:
            self.ibundle = 0
        else:
            self.reset()
        
    def forward_state(self):
        """Forward to next state"""
        
        nbundles = len(self.bunlist)
        if self.ibundle < 0:
            self.ibundle = self.ibundle + nbundles
        self.ibundle += 1
        if self.ibundle >= nbundles:
            self.ibundle = nbundles - 1
        else:
            self.reset()

    def chanbow_sbox_update(self):
        """Update chanbow spinbox value"""
        
        iseg = int(self.case_cbox.currentIndex())
        segment = self.bunlist[self.ibundle].segments[iseg]
        if hasattr(segment.data, "box_offset"):
            box_offset = segment.data.box_offset * 10
        else:
            box_offset = 0
        self.chanbow_sbox.setValue(box_offset)
        
    def toggle_cmap(self, status):
        """slot triggered on colorAction signal"""

        if self.colorAction.isChecked():
            self.show_cmap.setChecked(True)
        else:
            self.show_cmap.setChecked(False)
        self.toggle_pin_bgcolors()
    
    def toggle_pin_bgcolors(self):
        """Toggle pin background colors"""
        
        iseg = int(self.case_cbox.currentIndex())
        if self.show_cmap.isChecked():
            self.colorAction.setChecked(True)
            for pin in self.pinobjects[iseg]:
                pin.rectangle.set_alpha(1.0)
        else:
            self.colorAction.setChecked(False)
            for pin in self.pinobjects[iseg]:
                pin.rectangle.set_alpha(0.0)
        self.canvas.draw()

    def toggle_maxpins(self):
        """track maxpin on/off"""
        if self.track_maxpin.isChecked():
            self.mark_maxpins()
        else:
            self.remove_maxpins()
        self.canvas.draw()

    def remove_maxpins(self):
        if hasattr(self, "maxpins"):
            for ipin in range(len(self.maxpins)):
                try:
                    self.maxpins[ipin].maxpin_patch.remove()
                except:
                    pass

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, icon=None,
                      tip=None, checkable=False, signal="triggered()"):

        action = QtGui.QAction(text, self)
        if icon is not None:
            #action.setIcon(QtGui.QIcon(":/%s.png" % icon))
            action.setIcon(QtGui.QIcon(self.appdir + "icons/%s.png" % icon))
            action.setIconVisibleInMenu(True)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def widgets_setenabled(self, status=True):

        widgets = [self.param_cbox, self.case_cbox, self.point_sbox,
                   self.chanbow_sbox, self.table]
        for w in widgets:
            w.setEnabled(status)
    
        for a in self.toolbar_actions:
            a.setEnabled(status)

        for a in self.menu_actions:
            a.setEnabled(status)

    def closeEvent(self, event):
        """Runs before program terminates"""

        # Write window size and position to config file
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("size", QtCore.QVariant(self.size()))
        self.settings.setValue("pos", QtCore.QVariant(self.pos()))
        self.settings.endGroup()

        # Close windows before exit
        if hasattr(self, "report_dlg"):
            self.report_dlg.close()
        if hasattr(self, "findpoint_dlg"):
            self.findpoint_dlg.close()

        # Cleanup files
        self.__file_cleanup()

        print "Good bye!"


def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWin()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
