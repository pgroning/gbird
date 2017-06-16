#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is the main window of the program.
"""

# Set tracepoint (used for debugging).  Usage: Tracer()()
from IPython.core.debugger import Tracer

# Set a tracepoint that works with Qt.  Usage: qtrace()
from pyqt_trace import pyqt_trace as qtrace

import sys
import os
import time
import copy
import re
import numpy as np
from PyQt4 import QtGui, QtCore

try:
    import cPickle as pickle
except:
    import pickle

from ui import Ui_MainWindow
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
from threads import ImportThread, LoadPickleThread
from threads import QuickCalcThread, RunC4Thread
from fuelmap import FuelMap



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

        # Setup menus and toolbars in main window
        self.ui = Ui_MainWindow()
        self.ui.setup(self)

        self.resizeEvent = self.ui.on_resize

        self.widgets_setenabled(False)

        self.fuelmap = FuelMap(self)
        
    def openFile(self):
        """Open bundle object from pickle file"""

        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_default",
                                           QtCore.QString("")).toString()
        self.settings.endGroup()
        file_choices = "Data files (*.gbi *.cax)"
        filename = unicode(QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                             path_default,
                                                             file_choices))
        if filename:
            self.clear_data()

            self.thread = LoadPickleThread(self, filename)
            self.connect(self.thread, QtCore.SIGNAL('finished()'), 
                     self.__load_pickle_finished)
            self.thread.start()

            self.statusBar().showMessage('Load project from %s' % filename)
            #self.setCursor(QtCore.Qt.WaitCursor)

            # Save default path to config file
            path = os.path.split(filename)[0]
            self.settings.beginGroup("PATH")
            self.settings.setValue("path_default", QtCore.QString(path))
            self.settings.endGroup()

            #filext = os.path.splitext(filename)[1]
            #self.load_pickle(filename)
            #self.chanbow_sbox_update()
            #self.widgets_setenabled()
            #self.setCursor(QtCore.Qt.ArrowCursor)
 
    def __load_pickle_finished(self):
        print "load pickle finished"
        self.ibundle = len(self.bunlist) - 1
        self.init_pinobjects()
        self.init_cboxes()

        self.chanbow_sbox_update()
        self.widgets_setenabled()
        self.__quickcalc_setenabled()
        #self.setCursor(QtCore.Qt.ArrowCursor)
                   
#    def load_pickle(self, filename):
#        """Load bundle object from pickle file"""
#
#        #self.statusBar().showMessage('Load project from %s' % filename, 2000)
#
#        #print "Loading data from file " + filename
#        #self.clear_data()
#
#        with open(filename, 'rb') as fp:
#            self.params = pickle.load(fp)
#            self.bunlist = pickle.load(fp)
#            try:
#                self.biascalc = pickle.load(fp)
#            except EOFError:  # biascalc exists?
#                pass
#
#        self.ibundle = len(self.bunlist) - 1
#        self.init_pinobjects()
#        self.init_cboxes()
 
    def read_cax(self, filename):
        """Importing data from a single cax file"""
        
        self.clear_data()
        bundle = Bundle()
        bundle.read_single_cax(filename)
        bundle.new_btf()
        self.bunlist = []
        self.bunlist.append(bundle)

        self.init_pinobjects()

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
                
        self.thread = ImportThread(self)
        self.connect(self.thread, QtCore.SIGNAL('import_data_finished()'), 
                     self.__import_data_finished)
        self.connect(self.thread, QtCore.SIGNAL('finished()'), 
                     self.__quickcalc_setenabled)
        self.connect(self.thread, QtCore.SIGNAL('progressbar_update(int)'),
                     self.__progressbar_update)

        self.ibundle = 0
        self.thread.start()
        self.statusBar().showMessage("Importing data...")

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
            self.timer.start(60)  # argument sets the update period in ms
        else:
            self.timer.start(1000)
            
    def __import_data_finished(self):
        """importation of data finished"""

        self.init_pinobjects()
        self.init_cboxes()
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
        #self.calcAction.setEnabled(status)
        self.ui.quickcalc_action.setEnabled(status)

    def init_cboxes(self):
        """Initiate combo boxes"""
        
        # init segment combo box
        nsegments = len(self.bunlist[-1].segments)
        seglist = map(str, range(1, nsegments + 1))
        self.ui.case_cbox.addItems(QtCore.QStringList(seglist))

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
            
            self.ui.canvas.print_figure(filename, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % filename, 2000)

    def export_to_ascii(self):
        """Export data to file using YAML format"""

        iseg = int(self.ui.case_cbox.currentIndex())
        param = str(self.ui.param_cbox.currentText())

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
                        pinobj = FuePin(self.ui.axes)
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
            cmap = self.fuelmap.get_colormap(enr_levels.size)
            for i in range(enr_levels.size):
                enrobj = FuePin(self.ui.axes)
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

        case_num = int(self.ui.case_cbox.currentIndex())
        ipin = self.pinselection_index  # copy attributes from selected pin

        enrobj = FuePin(self.ui.axes)
        enrobj.facecolor = self.enrpinlist[case_num][ipin].facecolor
        enrobj.DENS = self.enr_dlg.dens
        enrobj.ENR = self.enr_dlg.enr
        if self.enr_dlg.ba < 0.00001:
            enrobj.BA = np.nan
            enrobj.BAindex = np.nan
        else:
            enrobj.BA = self.enr_dlg.ba
            enrobj.BAindex = 7300  # Gd

        self.enrpinlist[case_num].append(enrobj)
        self.fig_update()

    def enrpin_edit(self):
        """edit enr pin"""
        self.enr_dlg = EnrDialog(self, "edit")
        self.enr_dlg.exec_()  # Make dialog modal

    def enrpin_edit_callback(self):
        """enr pin edit callback"""

        case_num = int(self.ui.case_cbox.currentIndex())
        ipin = self.pinselection_index  # index of enr level pin to be edited
        enrpin = self.enrpinlist[case_num][ipin]

        # update fue pins
        for pin in self.pinobjects[case_num]:
            if pin.LFU == ipin + 1:
                pin.ENR = self.enr_dlg.enr
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

        case_num = int(self.ui.case_cbox.currentIndex())
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

        case_num = int(self.ui.case_cbox.currentIndex())
        enrlist = [pin.ENR for pin in self.enrpinlist[case_num]]
        isort = [i for i, e in sorted(enumerate(enrlist), key=lambda x:x[1])]
        
        cmap = self.fuelmap.get_colormap(len(isort))
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
        ipoint = int(self.ui.point_sbox.value())
        iseg = int(self.ui.case_cbox.currentIndex())
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
            self.ui.point_sbox.setValue(ipoint)

    def set_pinvalues(self):
        """Update pin values"""

        param_str = str(self.ui.param_cbox.currentText())
        iseg = int(self.ui.case_cbox.currentIndex())

        state_num = self.ibundle
        bundle = self.bunlist[state_num]
        segment = bundle.segments[iseg]
        
        self.ui.point_sbox.setMaximum(len(segment.statepoints) - 1)
        point_num = int(self.ui.point_sbox.value())
        
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
        self.ui.table.sort_items()
        #self.table.sortItems(0, QtCore.Qt.AscendingOrder)
        self.ui.table.clearContents()
        self.ui.table.setpincoords()
        
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

                    self.ui.table.setItem(k, 1, expItem)
                    self.ui.table.setItem(k, 2, fintItem)
                    self.ui.table.setItem(k, 3, btfItem)
                    k += 1
        
        statepoint = segment.statepoints[point_num]
        burnup = statepoint.burnup
        voi = statepoint.voi
        vhi = statepoint.vhi
        kinf = statepoint.kinf
        fint = statepoint.fint
        btf = BTF.max()
        tfu = statepoint.tfu
        tmo = statepoint.tmo
        
        formstr = "{0:.0f} / {1:.0f}".format(voi, vhi)
        self.ui.voi_vhi_text.setText(formstr)
        formstr = "{0:.0f} / {1:.0f}".format(tfu, tmo)
        self.ui.tfu_tmo_text.setText(formstr)
        formstr = "{0:.3f}".format(burnup)
        self.ui.burnup_text.setText(formstr)
        formstr = "{0:.5f}".format(kinf)
        self.ui.kinf_text.setText(formstr)
        formstr = "{0:.3f}".format(fint)
        self.ui.fint_text.setText(formstr)
        formstr = "{0:.4f}".format(btf)
        self.ui.btf_text.setText(formstr)
        
        npins = len(self.pinobjects[iseg])
        cmap = self.fuelmap.get_colormap(npins, "jet")

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
            j = self.pinobjects[iseg][i].LFU - 1
            fc = self.enrpinlist[iseg][j].circle.get_facecolor()
            self.pinobjects[iseg][i].circle.set_facecolor(fc)

            if param_str == "ENR":
                x = self.pinobjects[iseg][i].ENR
                if xmax == xmin:
                    y = 0.5
                else:
                    y = (x - xmin) / (xmax - xmin)
                ic = int(round(y * (npins - 1)))
                self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])
                text = self.enrpinlist[iseg][j].text.get_text()

            elif param_str == "BTF":
                x = self.pinobjects[iseg][i].BTF
                
                if not np.isnan(x):
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

            elif param_str == "EXP":
                x = self.pinobjects[iseg][i].EXP
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

            elif param_str == "FINT":
                x = self.pinobjects[iseg][i].FINT
                if xmax == xmin:
                    y = 0.5
                else:
                    y = (x - xmin) / (xmax - xmin)

                ic = int(round(y * (npins - 1)))
                self.pinobjects[iseg][i].rectangle.set_facecolor(cmap[ic])

                text = '{0:.0f}'.format(x * 100)
            elif param_str == "ROD":
                return
                
            self.pinobjects[iseg][i].text.remove()
            self.pinobjects[iseg][i].set_text(text)

        if self.track_maxpin.isChecked():
            self.mark_maxpins()

        self.ui.canvas.draw()
        self.plot_update()
        self.report_update()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 'Save file', '',
                                                   file_choices))
        if path:
            self.ui.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = "Greenbird version " + self.appversion
        QtGui.QMessageBox.about(self, "About the software", msg.strip())

    def tableHeaderSort(self):
        # Sort header
        case_num = int(self.ui.case_cbox.currentIndex())
        for i, pinobj in enumerate(self.pinobjects[case_num]):
            index = int(self.ui.table.item(i, 0).text())
            item = QtGui.QTableWidgetItem(
                str(self.pinobjects[case_num][index].coord))
            self.ui.table.setVerticalHeaderItem(i, item)

    def tableSelectRow(self, i):
        index = next(j for j in range(self.ui.table.rowCount())
                     if int(self.ui.table.item(j, 0).text()) == i)
        self.ui.table.selectRow(index)

    def pinSelect(self, i):
        if hasattr(self.ui.table.item(i, 0), "text"):
            index = int(self.ui.table.item(i, 0).text())
            self.mark_pin(index)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_8:  # Up arrow key was pressed
            iseg = int(self.ui.case_cbox.currentIndex())
            imax = self.ui.case_cbox.count() - 1
            if iseg < imax:
                iseg += 1
                self.ui.case_cbox.setCurrentIndex(iseg)  # increase segment
        elif key == QtCore.Qt.Key_2:  # Down arrow key was pressed
            iseg = int(self.ui.case_cbox.currentIndex())
            if iseg > 0:
                iseg -= 1
                self.ui.case_cbox.setCurrentIndex(iseg)  # decrease segment
        elif key == QtCore.Qt.Key_4:  # Left arrow key was pressed
            ipoint = self.ui.point_sbox.value()
            imin = self.ui.point_sbox.minimum()
            if ipoint > imin:
                ipoint -= 1
                self.ui.point_sbox.setValue(ipoint)  # increase state point
        elif key == QtCore.Qt.Key_6:  # Right arrow key was pressed
            ipoint = self.ui.point_sbox.value()
            imax = self.ui.point_sbox.maximum()
            if ipoint < imax:
                ipoint += 1
                self.ui.point_sbox.setValue(ipoint)  # decrease state point

    def on_click(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #

        #if qApp.keyboardModifiers() & Qt.ControlModifier: # ctrl+click
        #    remove = False
        #else:
        #    remove = True
        #    pass
        
        if not hasattr(self, "pinobjects"):  # is data initialized?
            return

        case_num = int(self.ui.case_cbox.currentIndex())

        if event.button is 1:  # left mouse click
            # check if any pin is selected and return the index
            i = next((i for i, cobj in enumerate(self.pinobjects[case_num])
                      if cobj.is_clicked(event.xdata, event.ydata)), None)

            if i is not None and i >= 0:  # A pin is selected
                self.tableSelectRow(i)
                self.mark_pin(i)

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

    def halfsym_pin(self, i, case_num=None):
        """Find the corresponding pin for half symmetry"""

        if case_num is None:
            case_num = int(self.ui.case_cbox.currentIndex())

        pos = self.pinobjects[case_num][i].pos
        sympos = list(reversed(pos))
        j = next(k for k, po in enumerate(self.pinobjects[case_num])
                 if po.pos == sympos)
        return j

    def casecor_pin(self, case_num):
        """Find the corresponding pin for another segment"""
        
        current_case_num = int(self.ui.case_cbox.currentIndex())
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
        case_num = int(self.ui.case_cbox.currentIndex())
        self.clicked_pin = self.pinobjects[case_num][i]
        self.clicked_pin.set_clickpatch()
        
        # mark enr pin
        LFU = self.clicked_pin.LFU
        self.mark_enrpin(self.enrpinlist[case_num][LFU - 1])

        self.ui.canvas.draw()
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

        #sender = QtCore.QObject.sender(self)
        #label = str(sender.text())
        #LFU = int(label.replace("#", ""))
        
        case_num = int(self.ui.case_cbox.currentIndex())
        bundle = self.bunlist[self.ibundle]

        if (hasattr(bundle.data, "segment_connect_list") and
            bundle.data.segment_connect_list[case_num]):
            ncases = len(self.pinobjects)
            for iseg in range(ncases):
                if bundle.data.segment_connect_list[iseg]:
                    self.enr_modify(mod, iseg)
        else:
            self.enr_modify(mod, case_num)

        self.ui.canvas.draw()
        self.enr_fields_update()  # Update info fields

    def enr_fields_update(self):
        """Update enr value in info fields"""

        iseg = int(self.ui.case_cbox.currentIndex())
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
        orig_seg_enr = self.bunlist[0].segments[iseg].data.ave_enr
        diff_seg_enr = segment.ave_enr - orig_seg_enr
        formstr = '{0:.4f} ({1:+.4f})'.format(segment.ave_enr, diff_seg_enr)
        self.ui.ave_enr_text.setText(formstr)
        
        # Update bundle enr
        bundle_enr = bundle.ave_enr_calc()
        if not hasattr(bundle, "ave_enr"):
            bundle.ave_enr = bundle_enr  # save orig. calc
        
        orig_bundle_enr = self.bunlist[0].ave_enr
        diff_bundle_enr = bundle_enr - orig_bundle_enr
        formstr = '{0:.4f} ({1:+.4f})'.format(bundle_enr, diff_bundle_enr)
        self.ui.bundle_enr_text.setText(formstr)

        # Update number of pin types
        fuetype = self.bunlist[0].data.fuetype
        pins = PinCount(LFU_list, FUE_list, fuetype)
        formstr = '{0:d}'.format(pins.noofpintypes)
        self.ui.rod_types_text.setText(formstr)

        self.report_update()

    def enr_modify(self, mod, case_num=None, ipin=None):
        halfsym = True
        if case_num is None:
            case_num = int(self.ui.case_cbox.currentIndex())
        ivec = []
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
            pinLFU = self.pinobjects[case_num][i].LFU
            if mod == "add":
                if pinLFU < len(self.enrpinlist[case_num]):
                    self.__pinenr_update(i, pinLFU + 1, case_num)
            elif mod == "sub":
                if pinLFU > 1:
                    self.__pinenr_update(i, pinLFU - 1, case_num)

    def __pinenr_update(self, i, pinLFU, case_num=None):
        if case_num is None:
            case_num = int(self.ui.case_cbox.currentIndex())
        j = pinLFU - 1
        self.pinobjects[case_num][i].LFU = pinLFU
        self.pinobjects[case_num][i].ENR = self.enrpinlist[case_num][j].ENR
        
        if np.isnan(self.enrpinlist[case_num][j].BA):
            self.pinobjects[case_num][i].BA = 0.0
        else:
            self.pinobjects[case_num][i].BA = self.enrpinlist[case_num][j].BA

        if case_num == int(self.ui.case_cbox.currentIndex()):
            fc = self.enrpinlist[case_num][j].circle.get_facecolor()
            self.pinobjects[case_num][i].circle.set_facecolor(fc)
            
            text = self.enrpinlist[case_num][j].text.get_text()
            if str(self.ui.param_cbox.currentText()) == 'ENR':
                self.pinobjects[case_num][i].text.remove()
                self.pinobjects[case_num][i].set_text(text)

    def __lfumap(self, iseg):
        """Creating LFU map from pinobjects"""
                
        # Initialize new LFU map and fill with zeros
        LFU_old = self.bunlist[-1].segments[iseg].data.LFU
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
        
        self.ui.axes.clear()
        self.fuelmap.draw()
        self.set_pinvalues()
        self.toggle_pin_bgcolors()
        
        # Update info field
        iseg = int(self.ui.case_cbox.currentIndex())
        sim = self.bunlist[0].segments[iseg].data.sim
        text = sim.replace("SIM", "").replace("'", "").strip()
        self.ui.sim_info_field.setText(text)
        self.enr_fields_update()

    def mark_maxpins(self, param=None):
        """Mark pin with maximum value"""

        self.remove_maxpins()

        iseg = int(self.ui.case_cbox.currentIndex())
        ipoint = int(self.ui.point_sbox.value())
        bundle = self.bunlist[self.ibundle]
        segment = bundle.segments[iseg]
        if param == None:
            param = str(self.ui.param_cbox.currentText())
        if param not in ["FINT", "EXP", "BTF"]:
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

        self.maxpins = []
        M_max = M.max()
        if M_max > 0.00001:
            i_arr, j_arr = np.where(M > M.max()*0.99999)
            for i, j in zip(i_arr, j_arr):
                maxpin = next(p for p in self.pinobjects[iseg] 
                                   if p.pos == [i, j])
                maxpin.set_maxpin_patch()
                self.maxpins.append(maxpin)

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
        """Clear fuel map figure axes and delete bundle and GUI field data"""

        self.ui.param_cbox.setCurrentIndex(0)
        self.ui.point_sbox.setValue(0)
        self.ui.chanbow_sbox.setValue(0)

        widgets = [self.ui.case_cbox, self.ui.sim_info_field, 
                   self.ui.rod_types_text,
                   self.ui.ave_enr_text, self.ui.bundle_enr_text,
                   self.ui.burnup_text, self.ui.kinf_text, self.ui.fint_text,
                   self.ui.btf_text, self.ui.voi_vhi_text, self.ui.tfu_tmo_text]
        for w in widgets:
            w.clear()

        self.show_cmap.setChecked(False)
        self.ui.table.clearContents()

        if hasattr(self, "bundle"):
            del self.bundle
        
        if hasattr(self, "pinobjects"):
            del self.pinobjects

        # Clear and restore figure
        self.ui.axes.clear()  # Clears the figure axes
        self.ui.fig.set_facecolor('0.75')  # set facecolor to gray

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
        
        iseg = int(self.ui.case_cbox.currentIndex())
        segment = self.bunlist[self.ibundle].segments[iseg]
        if hasattr(segment.data, "box_offset"):
            box_offset = segment.data.box_offset * 10
        else:
            box_offset = 0
        self.ui.chanbow_sbox.setValue(box_offset)
        
    def toggle_cmap(self, status):
        """slot triggered on colorAction signal"""

        if self.colorAction.isChecked():
            self.show_cmap.setChecked(True)
        else:
            self.show_cmap.setChecked(False)
        self.toggle_pin_bgcolors()
    
    def toggle_pin_bgcolors(self):
        """Toggle pin background colors"""
        
        iseg = int(self.ui.case_cbox.currentIndex())
        if self.show_cmap.isChecked():
            self.colorAction.setChecked(True)
            for pin in self.pinobjects[iseg]:
                pin.rectangle.set_alpha(1.0)
        else:
            self.colorAction.setChecked(False)
            for pin in self.pinobjects[iseg]:
                pin.rectangle.set_alpha(0.0)
        self.ui.canvas.draw()

    def toggle_maxpins(self):
        """track maxpin on/off"""
        if self.track_maxpin.isChecked():
            self.mark_maxpins()
        else:
            self.remove_maxpins()
        self.ui.canvas.draw()

    def remove_maxpins(self):
        if hasattr(self, "maxpins"):
            for ipin in range(len(self.maxpins)):
                try:
                    self.maxpins[ipin].maxpin_patch.remove()
                except:
                    pass

    def widgets_setenabled(self, status=True):

        widgets = [self.ui.param_cbox, self.ui.case_cbox, self.ui.point_sbox,
                   self.ui.chanbow_sbox, self.ui.table]
        for w in widgets:
            w.setEnabled(status)
    
        #for a in self.toolbar_actions:
        #    a.setEnabled(status)
        #qtrace()
        for a in self.ui.menu_actions:
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
