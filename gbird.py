#!/usr/bin/python
"""
This is the main window of the program.
This window embeds a matplotlib (mpl) plot into a PyQt4 GUI application
"""

from IPython.core.debugger import Tracer  # Set tracepoint (used for debugging)
# Usage: Tracer()()
 # Set a tracepoint that works with Qt
from pyqt_trace import pyqt_trace as qtrace 
# Usage: qtrace()

import sys
import os 
import time
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *
# from PyQt4 import QtGui, QtCore

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
#from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches
try:  # patheffects not available for older versions of matplotlib
    import matplotlib.patheffects as path_effects
except:
    pass

from bundle import Bundle
from btf import Btf
from plot import PlotWin
from progbar import ProgressBar
#from map_s96 import s96o2
#from map_a10 import a10xm


class dataThread(QThread):
    def __init__(self,parent):
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
            self.emit(SIGNAL('progressbar_update(int)'),90)
        if not self._kill:
            self.dataobj.calcbtf()
        if not self._kill:
            self.parent.dataobj = self.dataobj

        #self.parent.dataobj = casio()
        #self.parent.dataobj.readinp(self.parent._filename)
        #self.parent.dataobj.readcax()
        #self.emit(SIGNAL('progressbar_update(int)'),90)
        #self.parent.dataobj.calcbtf()

"""
class Circle(object):
    def __init__(self,axes,x,y,c=(1,1,1),text='',r=0.028):
        self.axes = axes
        #radius = 0.028
        self.circle = mpatches.Circle((x,y), r, fc=c, ec=(0.1, 0.1, 0.1))
        self.circle.set_linestyle('solid')
        try:
            self.circle.set_path_effects([path_effects.withSimplePatchShadow()])
        except: pass
        self.circle.set_linewidth(2.0)
        self.x = x
        self.y = y
        self.text = self.axes.text(x,y,text,ha='center',va='center',fontsize=8)
        #self.axes.add_patch(self.circle)
        
        
    def set_text(self,text):
        pass
        #self.text.remove()
        #self.text = self.axes.text(self.x,self.y,text,ha='center',va='center',fontsize=8)


    def is_clicked(self,xc,yc):
        r2 = (xc-self.x)**2 + (yc-self.y)**2
        if r2 < self.circle.get_radius()**2: #Mouse click is within pin radius
            return True
        else:
            return False
"""

class cpin(object):
    def __init__(self, axes):
        self.axes = axes

    def set_circle(self, x, y, r, c=None):
        self.x = x
        self.y = y
        if c is None:
            c = self.facecolor
        self.circle = mpatches.Circle((x,y), r, fc=c, ec=(0.1, 0.1, 0.1))
        self.circle.set_linestyle('solid')
        self.circle.set_linewidth(2.0)
        try:
            self.circle.set_path_effects([path_effects.withSimplePatchShadow()])
        except:
            pass

    def set_text(self, string='', fsize=8):
        #if hasattr(self,'text'):
        #    self.text.remove()
        self.text = self.axes.text(self.x,self.y,string,ha='center',va='center',fontsize=fsize)

    def is_clicked(self, xc, yc):
        r2 = (xc-self.x)**2 + (yc-self.y)**2
        if r2 < self.circle.get_radius()**2: # Mouse click is within pin radius
            return True
        else:
            return False

class EnrDialog(QDialog):
    def __init__(self, parent, mode="edit"):
        #QDialog.__init__(self, parent)
        QDialog.__init__(self)
        self.parent = parent
        self.mode = mode

        #self.setWindowTitle("Window title")
        # set x-pos relative to cursor position
        #xpos = QCursor.pos().x() - 250
        # set dialog pos relative to main window
        xpos = parent.pos().x() + parent.size().width()/2
        ypos = parent.pos().y() + parent.size().height()/2
        self.setGeometry(QRect(xpos, ypos, 150, 120))

        if mode == "edit":
            self.setWindowTitle("Edit enrichment")
            case_num = int(parent.case_cbox.currentIndex())
            ipin = parent.pinselection_index
            enr = parent.enrpinlist[case_num][ipin].ENR
            ba = parent.enrpinlist[case_num][ipin].BA
            ba = 0 if np.isnan(ba) else ba
        elif mode == "add":
            self.setWindowTitle("Add enrichment")
            enr = 0
            ba = 0
        self.enr_text = QLineEdit("%.2f" % enr)
        self.ba_text = QLineEdit("%.2f" % ba)
        validator = QDoubleValidator(0, 9.99, 2, self)
        self.enr_text.setValidator(validator)
        self.ba_text.setValidator(validator)

        flo = QFormLayout()
        flo.addRow("%U-235:", self.enr_text)
        flo.addRow("%Gd:", self.ba_text)
        
        hbox = QHBoxLayout()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        hbox.addWidget(self.cancel_button)
        hbox.addWidget(self.ok_button)
        self.connect(self.cancel_button, SIGNAL('clicked()'), self.close)
        self.connect(self.ok_button, SIGNAL('clicked()'), self.action)
        #if mode == "edit":
        #    self.connect(self.ok_button, SIGNAL('clicked()'), self.edit_action)
        #elif mode == "add":
        #    self.connect(self.ok_button, SIGNAL('clicked()'), self.add_action)
        
        vbox = QVBoxLayout()
        vbox.addLayout(flo)
        vbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def action(self):
        self.close()
        self.enr = self.enr_text.text().toDouble()[0]
        self.ba = self.ba_text.text().toDouble()[0]
        if self.mode == "edit":
            self.parent.enrpin_edit_callback()
        elif self.mode == "add":
            self.parent.enrpin_add_callback()
        
class MainWin(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Main Window')
        
        #self.resize(1100,620)
        #self.move(200,200)
        
        # Initial window size/pos last saved
        self.settings = QSettings("greenbird")
        self.settings.beginGroup("MainWindow")
        self.resize(self.settings.value("size", 
                                        QVariant(QSize(1100, 620))).toSize());
        self.move(self.settings.value("pos", 
                                      QVariant(QPoint(200, 200))).toPoint())
        self.settings.endGroup()
        
        #screenShape = QDesktopWidget().screenGeometry()
        #self.resize( screenShape.width()*0.8,screenShape.width()*0.445 )
        #self.setMinimumWidth(1100)
        #self.setMinimumHeight(610)

        self.resizeEvent = self.on_resize
        
        # Retrieve initial data
        #self.data_init()
        #self.case_id_current = 0

        self.create_menu()
        self.create_toolbar()
        self.create_main_frame()
        self.create_status_bar()
        
        self.on_draw()  # Init plot
        #self.draw_fuelmap()
        #Tracer()()
        #self.textbox.setText('1 2 3 4')
        #self.data_init()
        
        #self.case_cbox.setCurrentIndex(0) # Set default plot case
        #self.case_id_current = 0
        #self.on_plot() # Init plot
        #self.on_draw()
        #self.draw_fuelmap()
        #Tracer()()

    def on_resize(self, event):
        self.axes.set_xlim(0,1.2)
        self.axes.set_ylim(0,1)

    def openFile(self):

        # Import default path from config file
        self.settings.beginGroup("PATH")
        path_default = self.settings.value("path_default",
                                           QString("")).toString()
        self.settings.endGroup()
        #file_choices = "inp (*.inp);;pickle (*.p)"
        file_choices = "Data files (*.inp *.p)"
        filename = unicode(QFileDialog.getOpenFileName(self, 'Open file',
                                                       path_default,
                                                       file_choices))
        if filename:
            # Save default path to config file
            path = os.path.split(filename)[0]
            self.settings.beginGroup("PATH")
            self.settings.setValue("path_default", QString(path))
            self.settings.endGroup()
            
            filext = os.path.splitext(filename)[1]
            if filext == ".p":
                self.load_pickle(filename)
            elif filext == ".inp":
                self.read_cax(filename)
        

    def load_pickle(self,filename):
        self.statusBar().showMessage('Importing data from %s' % filename, 2000)
        self.dataobj = casio()
        self.dataobj.loadpic(filename)

        self.init_pinobjects()
        #fuetype = 'SVEA-96'
        #self.dataobj.btf = btf(self.dataobj,fuetype)

        #self.setpincoords()
        #self.draw_fuelmap()
        #self.set_pinvalues()

        # Update case number list box
        ncases = len(self.dataobj.cases)
        for i in range(1,ncases+1):
            self.case_cbox.addItem(str(i))
        self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'), 
                     self.fig_update)
        self.fig_update()
        
        
    def dataobj_finished(self):
        print "dataobject constructed"
        self.init_pinobjects()

        # Perform reference quick calculation for base case 
        print "Performing a reference quick calculation..."
        ncases = len(self.dataobj.cases)
        for case_num in range(ncases):
            self.quick_calc(case_num)

        #pyqt_trace()
        #self.thread.quit()
        #self.draw_fuelmap()
        #self.set_pinvalues()
        self.timer.stop()

        # Update case number list box
        #ncases = len(self.dataobj.cases)
        for i in range(1,ncases+1):
            self.case_cbox.addItem(str(i))
        self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'), self.fig_update)
        self.fig_update()
            
        self.progressbar.update(100)
        self.progressbar.setWindowTitle('All data imported')
        self.progressbar.button.setText('Ok')
        self.progressbar.button.clicked.disconnect(self.killThread)
        self.progressbar.button.clicked.connect(self.progressbar.close)
        self.progressbar.button.setEnabled(True)
        
        #pyqt_trace()
        #QMessageBox.information(self,"Done!","All data imported!")

    def progressbar_update(self,val=None):
        if val is not None:
            self.progressbar._value = max(val,self.progressbar._value)
        self.progressbar.update(self.progressbar._value)
        self.progressbar._value += 1

    def killThread(self):
        print 'killThread'
        self.disconnect(self.timer,SIGNAL('timeout()'),self.progressbar_update)
        self.disconnect(self.thread,SIGNAL('finished()'),self.dataobj_finished)
        self.disconnect(self.thread,SIGNAL('progressbar_update(int)'),self.progressbar_update)
        self.thread._kill = True
        self.progressbar.close()
        #self.progressbar.close
#        self.thread.wait()
#        print 'killed'

    def read_cax(self,filename):
        msg = "Continue?"""
        msgBox = QMessageBox()
        ret = msgBox.information(self, "Importing data", msg.strip(),
                                 QMessageBox.Yes|QMessageBox.Cancel)
        # ret = msgBox.question(self,"Importing data",msg.strip(),
        # QMessageBox.Yes|QMessageBox.Cancel)
        self.statusBar().showMessage('Importing data from %s' % filename, 2000)
        self._filename = filename
        if ret == QMessageBox.Yes:

            print "importing data"
            
            self.bundle = Bundle()
            self.bundle.readinp(filename)
            self.bundle.readcax()  # readcax("all") reads the whole file content
            self.bundle.new_btf()

            print "init pinobjects"
            self.init_pinobjects()
            
            # Update case number list box
            ncases = len(self.bundle.cases)
            for i in range(1,ncases+1):
                self.case_cbox.addItem(str(i))
            self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'), 
                         self.fig_update)

            self.fig_update()
            #self.canvas.draw()
            #self.axes.clear()
            #self.draw_fuelmap()
            
            '''
            #self.progressbar = ProgressBar()

            #self.dataobj = casio()
            self.thread = dataThread(self)
            self.connect(self.thread,SIGNAL('finished()'),self.dataobj_finished)
            self.connect(self.thread,SIGNAL('progressbar_update(int)'),self.progressbar_update)
            self.thread.start()

            self.progressbar = ProgressBar()
            xpos = self.pos().x() + self.width()/2 - self.progressbar.width()/2
            ypos = self.pos().y() + self.height()/2 - self.progressbar.height()/2
            self.progressbar.move(xpos,ypos)
            self.progressbar.show()
            self.progressbar.button.setEnabled(False)
            self.progressbar.button.clicked.connect(self.killThread)
            #self.progressbar.button.clicked.connect(self.progressbar.close)

            self.timer = QTimer()
            self.connect(self.timer,SIGNAL('timeout()'),self.progressbar_update)
            self.progressbar._value = 1
            self.timer.start(500)

            #time.sleep(20)
            #self.thread.terminate()
            #pyqt_trace()

            #print self.dataobj.data.caxfiles

            #self.dataobj = casio()
            #self.dataobj.readinp(filename)
            #self.dataobj.readcax()

            #self.dataobj.calcbtf()
            #fuetype = 'SVEA-96'
            #self.dataobj.btf = btf(self.dataobj,fuetype)

            #self.setpincoords()
            #self.draw_fuelmap()
            #self.set_pinvalues()
            #self.dataobj.savecas()
            '''
        else:
            return

    def saveData(self):
        file_choices = "Data files (*.p)"
        filename = unicode(QFileDialog.getSaveFileName(self, 'Open file', '', file_choices))
        self.dataobj.savepic(filename)

    def plotWin(self):
        #print "Open plot window"
        if hasattr(self,'bundle'):
            plotwin = PlotWin(self)
            plotwin.show()
        else:
            msg = "There is no data to plot."
            msgBox = QMessageBox()
            msgBox.information(self,"No data",msg.strip(),QMessageBox.Close)

    def get_colormap(self, num_enr_levels):
        cvec = ["#FF00FF", "#CC00FF", "#AA00FF", "#0000FF", "#0066FF",
                "#00AAFF", "#00CCFF", "#00FFFF", "#00FFCC", "#00FFAA",
                "#00FF66", "#00FF00", "#AAFF00", "#CCFF00", "#FFFF00",
                "#FFCC00", "#FFAA00", "#FF9900", "#FF5500", "#FF0000"]
        ic = np.linspace(0, len(cvec)-1, num_enr_levels).astype(int).tolist()
        cmap = [cvec[i] for i in ic]
        return cmap

    def init_pinobjects(self):
        self.pinobjects = []
        self.enrpinlist = []
        ncases = len(self.bundle.cases)
        
        for case_num in range(ncases):
            LFU = self.bundle.cases[case_num].states[-1].LFU
            ENR = self.bundle.cases[case_num].states[-1].ENR
            BA = self.bundle.cases[case_num].states[-1].BA
            
            pinlist = []
            for i in range(LFU.shape[0]):
                for j in range(LFU.shape[1]):
                    if LFU[i,j] > 0:
                        pinobj = cpin(self.axes)
                        pinobj.pos = [i,j]
                        pinobj.ENR = ENR[i,j]
                        pinobj.BA = BA[i,j]
                        pinobj.LFU = LFU[i,j]
                        pinlist.append(pinobj)
            self.pinobjects.append(pinlist)
        
            enrlist = []
            FUE = self.bundle.cases[case_num].states[-1].FUE
            enr_dens = FUE[:, 1]
            enr_levels = FUE[:, 2]
            enr_baindex = FUE[:, 3]
            enr_ba = FUE[:, 4]
            cmap = self.get_colormap(enr_levels.size)
            for i in range(enr_levels.size):
                enrobj = cpin(self.axes)
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

        enrobj = cpin(self.axes)
        enrobj.facecolor = self.enrpinlist[case_num][ipin].facecolor
        enrobj.DENS = self.enrpinlist[case_num][ipin].DENS
        enrobj.ENR = self.enr_dlg.enr
        if self.enr_dlg.ba < 0.00001:
            enrobj.BA = np.nan
            enrobj.BAindex = np.nan
        else:
            enrobj.BA = self.enr_dlg.ba
            enrobj.BAindex = 7300  # Gd
            
        self.enrpinlist[case_num].append(enrobj)
        
        #if enrobj.ENR > self.enrpinlist[case_num][-1].ENR:
        #    self.enrpinlist[case_num].append(enrobj)
        #else:
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

        # first update fue pins
        for pin in self.pinobjects[case_num]:
            if pin.LFU == ipin + 1:
                pin.ENR = self.enr_dlg.enr
                pin.BA = self.enr_dlg.ba
        
        # second update enr level pin
        self.enrpinlist[case_num][ipin].ENR = self.enr_dlg.enr
        if self.enr_dlg.ba < 0.00001:
            self.enrpinlist[case_num][ipin].BA = np.nan
        else:
            self.enrpinlist[case_num][ipin].BA = self.enr_dlg.ba
        self.fig_update()

    def enrpin_remove(self):
        """Remove enr level pin"""
        msgBox = QMessageBox()
        ret = msgBox.information(self, "Remove enrichment", "Are you sure?",
                                 QMessageBox.Yes|QMessageBox.Cancel)
        if ret == QMessageBox.Cancel:
            return

        case_num = int(self.case_cbox.currentIndex())
        ipin = self.pinselection_index  # index of enr level pin to be removed

        del self.enrpinlist[case_num][ipin]  # remove the selected pin

        if ipin >= len(self.enrpinlist[case_num]):
            j = len(self.enrpinlist[case_num]) - 1
        else:
            j = ipin
            
        for i, pin in enumerate(self.pinobjects[case_num]):
            if pin.LFU == ipin + 1:
                pin.ENR = self.enrpinlist[case_num][j].ENR
                if np.isnan(self.enrpinlist[case_num][j].BA):
                    pin.BA = 0.0
                else:
                    pin.BA = self.enrpinlist[case_num][j].BA
        self.fig_update()
    
    def set_pinvalues(self):
        """Update values"""

        param_str = str(self.param_cbox.currentText())
        case_num = int(self.case_cbox.currentIndex())
        point_num = int(self.point_sbox.value())
        state_num = -1

        state = self.bundle.cases[case_num].states[state_num]
        
        ENR = state.ENR
        EXP = state.statepoints[point_num].EXP
        FINT = state.statepoints[point_num].POW
        
        burnup = state.statepoints[point_num].burnup
        btf_burnpoints = self.bundle.states[state_num].btf.burnpoints
        
        index_array = np.where(btf_burnpoints == burnup)[0]
        if len(index_array) > 0:  # is BTF calculated for the specific burnup?
            btf_num = index_array[0]
            BTF = self.bundle.states[state_num].btf.DOX[btf_num,:,:]
        else:
            BTF = np.zeros(np.shape(self.bundle.states[state_num].btf.DOX)[1:])
            BTF.fill(np.nan)
        
        npst = self.bundle.cases[case_num].states[0].npst
        LFU = state.LFU
        #BA = state.BA
        BA = self.bundle.cases[case_num].states[0].BA  # only for testing

        # Sorting table column 0 in ascending order
        self.table.sortItems(0,Qt.AscendingOrder)
        self.setpincoords()
        
        k = 0
        for i in range(npst):
            for j in range(npst):
                if LFU[i,j] > 0:
                    self.pinobjects[case_num][k].EXP = EXP[i,j]
                    self.pinobjects[case_num][k].FINT = FINT[i,j]
                    self.pinobjects[case_num][k].BTF = BTF[i,j]
                    
                    expItem = QTableWidgetItem()
                    expItem.setData(Qt.EditRole,
                                    QVariant(float(np.round(EXP[i,j],3))))
                    fintItem = QTableWidgetItem()
                    fintItem.setData(Qt.EditRole,
                                     QVariant(float(np.round(FINT[i,j],3))))
                    btfItem = QTableWidgetItem()
                    btfItem.setData(Qt.EditRole,
                                    QVariant(float(np.round(BTF[i,j],3))))    

                    self.table.setItem(k,1,expItem)
                    self.table.setItem(k,2,fintItem)
                    self.table.setItem(k,3,btfItem)
                    k += 1
        
        statepoint = state.statepoints[point_num]
        burnup = statepoint.burnup
        voi = statepoint.voi
        vhi = statepoint.vhi
        kinf = statepoint.kinf
        fint = statepoint.fint
        btf = BTF.max()
        tfu = statepoint.tfu
        tmo = statepoint.tmo
        
        self.statusBar().showMessage("""Burnup=%.3f : VOI=%.0f : VHI=%.0f : 
Kinf=%.5f : Fint=%.3f : BTF=%.4f : TFU=%.0f : TMO=%.0f"""
                                     % (burnup, voi, vhi, kinf, fint, btf,
                                        tfu, tmo))
        
        npins = len(self.pinobjects[case_num])
        
        for i in xrange(npins):
            
            if self.pinobjects[case_num][i].BA < 0.00001:
                j = next(j for j,enrpin in enumerate(self.enrpinlist[case_num]) 
                         if enrpin.ENR == self.pinobjects[case_num][i].ENR)
            else:
                j = next(j for j, enrpin in enumerate(self.enrpinlist[case_num])
                         if enrpin.BA == self.pinobjects[case_num][i].BA 
                         and enrpin.ENR == self.pinobjects[case_num][i].ENR)
            self.pinobjects[case_num][i].LFU = j + 1
            fc = self.enrpinlist[case_num][j].circle.get_facecolor()
            self.pinobjects[case_num][i].circle.set_facecolor(fc)

            if param_str == "ENR":
                text = self.enrpinlist[case_num][j].text.get_text()
                
            elif param_str == "BTF":
                btf_ratio = self.pinobjects[case_num][i].BTF/btf*1000
                if int(btf_ratio) == 1000:
                    text =  "1e3"
                else:
                    text =  ('%.0f' % (btf_ratio))
                
            elif param_str == "EXP":
                if self.pinobjects[case_num][i].EXP < 10:
                    text =  ('%.1f' % (self.pinobjects[case_num][i].EXP))
                else:
                    text =  ('%.0f' % (self.pinobjects[case_num][i].EXP))

            elif param_str == "FINT":
                text =  ('%.0f' % (self.pinobjects[case_num][i].FINT*100))

            self.pinobjects[case_num][i].text.remove()
            self.pinobjects[case_num][i].set_text(text) 

        self.canvas.draw()

    def setpincoords(self):
        """Update table with pin coordinates"""

        self.table.clearContents()
        case_num = int(self.case_cbox.currentIndex())
        npin = len(self.pinobjects[case_num])
        self.table.setRowCount(npin)
        
        for i,pinobj in enumerate(self.pinobjects[case_num]):
            coord_item = QTableWidgetItem(pinobj.coord)
            self.table.setVerticalHeaderItem(i,coord_item)
            i_item = QTableWidgetItem()
            i_item.setData(Qt.EditRole, QVariant(int(i)))
            self.table.setItem(i,0,i_item)

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """Greenbird version X.X.X"""
        QMessageBox.about(self, "About the software", msg.strip())

    def tableHeaderSort(self):
        #print "Sort header"
        case_num = int(self.case_cbox.currentIndex())
        for i,pinobj in enumerate(self.pinobjects[case_num]):
            #for i,pinobj in enumerate(self.circlelist):
            #item = QTableWidgetItem(str(self.table.item(i,0).text()))
            index = int(self.table.item(i,0).text())
            item = QTableWidgetItem(str(self.pinobjects[case_num][index].coord))
            #item = QTableWidgetItem(str(self.circlelist[index].coord))
            self.table.setVerticalHeaderItem(i,item)

    def tableSelectRow(self,i):
        index = next(j for j in range(self.table.rowCount()) 
                     if int(self.table.item(j,0).text()) == i)
        self.table.selectRow(index)

    def pinSelect(self,i):
        index = int(self.table.item(i,0).text())
        self.mark_pin(index)

    def on_click(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 

        #print event.x,event.y
        #if qApp.keyboardModifiers() & Qt.ControlModifier: # ctrl+click
        #    remove = False
        #else:
        #    remove = True
        case_num = int(self.case_cbox.currentIndex())
        i = np.nan
        if event.button is 1:  # left mouse click
            # print event.xdata, event.ydata
            #i = np.nan
            try:  # check if any pin is selected and return the index
                i = next(i for i, cobj in enumerate(self.pinobjects[case_num])
                         if cobj.is_clicked(event.xdata, event.ydata))
            except:
                pass
            if i >= 0:  # A pin is selected
                self.tableSelectRow(i)
                self.mark_pin(i)
                self.pinselection_index = i
                #j = self.halfsym_pin(i)

        elif event.button is 3:  # right mouse click
            try:  # check if enr level pin is clicked
                i = next(i for i, cobj in enumerate(self.enrpinlist[case_num])
                         if cobj.is_clicked(event.xdata, event.ydata))
            except:
                pass
            if i >= 0:  # An enr level pin is selected
                self.pinselection_index = i
                    #self.mark_enrpin(i)
                    #print self.pinselection_index
                
                self.popMenu = QMenu(self)
                self.popMenu.addAction("Add...", self.enrpin_add)
                self.popMenu.addAction("Edit...", self.enrpin_edit)
                self.popMenu.addAction("Remove", self.enrpin_remove)
                
                    #action = self.popMenu.addAction("Remove")
                    #action.triggered.connect(self.printhello)
                    #print event.xdata, event.ydata
                    #mouse_cursor = QCursor()
                self.popMenu.exec_(QCursor.pos())
                    #self.popMenu.exec_(QPoint(event.xdata, event.ydata))
                    #qtrace()

                    
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

    def mark_pin(self,i):
        case_num = int(self.case_cbox.currentIndex())
        d = self.pinobjects[case_num][i].circle.get_radius()*2*1.25
        x = self.pinobjects[case_num][i].x-d/2
        y = self.pinobjects[case_num][i].y-d/2

        if hasattr(self, 'clickpatch'):  # Remove any previously selected pins
            try:
                self.clickpatch.remove()
            except:
                pass
        #self.clickrect = mpatches.Rectangle((x,y), d, d,hatch='.',
        #                                    fc=(1,1,1),alpha=1.0,ec=(1, 0, 0))
        #self.clickrect = mpatches.Rectangle((x,y), d, d,
        #                                    fc=(1,1,1),Fill=False,ec=(0, 0, 0))
        r = self.pinobjects[case_num][i].circle.get_radius()*1.3
        x = self.pinobjects[case_num][i].x
        y = self.pinobjects[case_num][i].y

        self.clickpatch = mpatches.Circle((x,y), r, fc=(1,1,1), alpha=1.0, 
                                          ec=(0.2, 0.2, 0.2))
        self.clickpatch.set_linestyle('solid')
        self.clickpatch.set_fill(False)
        self.clickpatch.set_linewidth(2.0)
        self.axes.add_patch(self.clickpatch)
        self.canvas.draw()

    def enr_add(self):

        if self.enr_case_cb.isChecked():  # update all cases
            ncases = len(self.pinobjects)
            for case_num in range(ncases):
                self.enr_modify("add", case_num)
        else:
            case_num = int(self.case_cbox.currentIndex())
            self.enr_modify("add", case_num)

        self.canvas.draw()
        self.enr_update()  # Update info fields
        
    def enr_sub(self):

        if self.enr_case_cb.isChecked():
            ncases = len(self.pinobjects)
            for case_num in range(ncases):
                self.enr_modify("sub", case_num)
        else:
            case_num = int(self.case_cbox.currentIndex())
            self.enr_modify("sub", case_num)
        
        self.canvas.draw()
        self.enr_update()  # Update info fields

        #self.enrpin_remove()  # only for testing. should be removed
        #enrArray = [x.ENR for x in self.enrpinlist][::-1] # Reverse order

    def enr_update(self):
        '''Update enr value in info fields'''

        case_num = int(self.case_cbox.currentIndex())
        LFU = self.__lfumap(case_num)
        FUE = self.__fuemap(case_num)
        self.bundle.cases[case_num].ave_enr(LFU, FUE)  # must take inargs
        ave_enr = self.bundle.cases[case_num].states[-1].ave_enr
        self.ave_enr_text.setText("%.5f" % ave_enr)

        self.bundle.ave_enr()
        bundle_enr = self.bundle.states[-1].ave_enr
        self.bundle_enr_text.setText("%.5f" % bundle_enr)

    def enr_modify(self, mod, case_num=None, ipin=None):
        halfsym = True
        if case_num is None:
            case_num = int(self.case_cbox.currentIndex())
        ivec = []
        #ipin = self.pinselection_index
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
            #print "Increase enrichment for pin " + str(i)
            pinEnr = self.pinobjects[case_num][i].ENR
            pinBA = self.pinobjects[case_num][i].BA
            
            for j, x in enumerate(self.enrpinlist[case_num]):
                if np.isnan(x.BA):
                    x.BA = 0.0
                if x.ENR == pinEnr and x.BA == pinBA:
                    break
            if mod == "add":
                if j < len(self.enrpinlist[case_num])-1:
                    self.__pinenr_update(i, j+1, case_num)
            elif mod == "sub":
                if j > 0:
                    self.__pinenr_update(i, j-1, case_num)

    def __pinenr_update(self, i, j, case_num=None):
        #i = self.pinselection_index
        if case_num is None:
            case_num = int(self.case_cbox.currentIndex())
        
        self.pinobjects[case_num][i].LFU = j + 1
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
        
        #self.bundle.cases[case_num].states[-1].LFU = self.__lfumap(case_num)
        #self.dataobj.cases[case_num].qcalc[0].LFU = self.__lfumap(case_num)
        #self.canvas.draw()


    def __lfumap(self, case_num):
        """Creating LFU map from pinobjects"""
        
        #print "Creating LFU map"
        #case_num = int(self.case_cbox.currentIndex())
        
        # Initialize new LFU map and fill with zeros
        LFU_old = self.bundle.cases[case_num].states[-1].LFU
        # LFU_old = self.dataobj.cases[case_num].data.LFU
        # LFU = np.zeros((LFU_old.shape[0],LFU_old.shape[1]));
        LFU = np.zeros(LFU_old.shape).astype(int)
        
        k = 0
        for i in range(LFU.shape[0]):
            for j in range(LFU.shape[1]):
                if LFU_old[i,j] > 0:
                    LFU[i,j] = self.pinobjects[case_num][k].LFU
                    k += 1
        return LFU

    def __fuemap(self, case_num):
        """Creating FUE map from enr level pins"""

        FUE_old = self.bundle.cases[case_num].states[-1].FUE
        nfue = len(self.enrpinlist[case_num])
        FUE = np.zeros((nfue, FUE_old.shape[1])).astype(float)
        for i in range(nfue):
            FUE[i, 0] = i + 1
            FUE[i, 1] = self.enrpinlist[case_num][i].DENS
            FUE[i, 2] = self.enrpinlist[case_num][i].ENR
            FUE[i, 3] = self.enrpinlist[case_num][i].BAindex
            FUE[i, 4] = self.enrpinlist[case_num][i].BA
        return FUE

    #def quick_calc(self,case_num):
    def quick_calc(self):
        print "Performing quick calculation..."
        
        for case_num in xrange(len(self.bundle.cases)):
            LFU = self.__lfumap(case_num)
            FUE = self.bundle.cases[case_num].states[-1].FUE  # Only for testing
            voi = None
            self.bundle.cases[case_num].add_state(LFU, FUE, voi)

        self.bundle.new_calc()
        self.bundle.new_btf()
        #qtrace()
        #self.dataobj.cases[case_num].qcalc[0].LFU = LFU
        #self.dataobj.cases[case_num].quickcalc()
        
#       case_num = int(self.case_cbox.currentIndex())        
#        self.dataobj.cases[case_num].pertcalc()


    def fig_update(self):
        """ Redraw figure and update values
        """
        ##self.on_draw()
        self.axes.clear()
        self.draw_fuelmap()
        self.set_pinvalues()

        # Update info field
        case_num = int(self.case_cbox.currentIndex())
        sim = self.bundle.cases[case_num].states[0].sim
        text = sim.replace("SIM", "").replace("'", "").strip()
        self.sim_text.setText(text)

        self.enr_update()

    def on_draw(self):
        """ Setup the figure axis"""

        # clear the axes and redraw the plot anew
        #
        #self.fig.clf()
        self.axes.clear()
        self.axes.axis('equal')
        #self.axes.set_xlim(0,1)
        #self.axes.set_ylim(0,1)
        #self.axes.axis('equal')
        
        #self.axes.set_position([0,0,1,1])
        #self.axes.set_xlim(0,1.2)
        #self.axes.set_ylim(0,1)
        self.axes.set_position([0,0,1,1])
        #self.axes.set_visible(False)
        self.axes.set_frame_on(False)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        #Tracer()()
        #self.axes.grid(self.grid_cb.isChecked())

        #xmax = self.slider.value()
        #self.axes.set_xlim(0,xmax)

        #self.axes.axis('equal')

        #Tracer()()
        
        #self.canvas.draw()

    def draw_fuelmap(self):
        """Draw fuel map"""

        from map_s96 import s96o2
        from map_a10 import a10xm

        self.fig.set_facecolor((1, 1, 0.8784))
        # Draw outer rectangle
        rect = mpatches.Rectangle((0.035,0.035), 0.935, 0.935, 
                                  fc=(0.8,0.898,1), ec=(0.3, 0.3, 0.3))
        self.axes.add_patch(rect)
        
        # Draw control rods
        rodrect_v = mpatches.Rectangle((0.011,0.13), 0.045, 0.77, 
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

        rodrect_h = mpatches.Rectangle((0.1,0.95), 0.77, 0.045, 
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
        p_fancy = mpatches.FancyBboxPatch((0.12, 0.12),
                                          0.77, 0.77,
                                          boxstyle="round,pad=0.04",
                                          #fc=(0.85,1,1),
                                          fc=(1,1,1),
                                          ec=(0.3, 0.3, 0.3))
        p_fancy.set_linewidth(4.0)
        self.axes.add_patch(p_fancy)
        
        if self.bundle.data.fuetype == 'OPT2':
            s96o2(self)
        elif self.bundle.data.fuetype == 'OPT3':
            s96o2(self)
        elif self.bundle.data.fuetype == 'A10XM':
            a10xm(self)
        elif self.bundle.data.fuetype == 'A10B':
            a10xm(self)
        
        # Draw symmetry line
        #pp = [[0.035, 0.965], [0.965, 0.035]]
        #poly = mpatches.Polygon(pp)
        #poly.set_closed(False)
        #self.axes.add_patch(poly)

        
    def startpoint(self,case_id):
        voi_val = int(self.voi_cbox.currentText())
        vhi_val = int(self.vhi_cbox.currentText())
        type_val = str(self.type_cbox.currentText())

        case = self.cas.cases[case_id]
        if type_val == 'CCl':
            idx0 = case.findpoint(tfu=293)
            voi = case.statepts[idx0].voi
            vhi = case.statepts[idx0].vhi
            voi_index = [i for i,v in enumerate(self.voilist) if int(v) == voi][0]
            vhi_index = [i for i,v in enumerate(self.vhilist) if int(v) == vhi][0]
            self.voi_cbox.setCurrentIndex(voi_index)
            self.vhi_cbox.setCurrentIndex(vhi_index)
        else:
            idx0 = case.findpoint(voi=voi_val,vhi=vhi_val)
        return idx0



    def create_main_frame(self):
        self.main_frame = QWidget()

        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((6, 5), dpi=self.dpi, facecolor=None)
        #self.fig = Figure((6, 5), dpi=self.dpi, facecolor=(1,1,1))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('button_press_event',self.on_click)
        self.canvas.setParent(self.main_frame)
        self.canvas.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.canvas.setMinimumWidth(500)
        self.canvas.setMinimumHeight(416)
        
        cvbox = QVBoxLayout()
        cvbox.addWidget(self.canvas)
        canvasGbox = QGroupBox()
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
        #self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        #self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        # 
        #self.textbox = QLineEdit()
        #self.textbox.setMinimumWidth(200)
        #self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)

                
        #self.draw_button = QPushButton("Draw")
        #self.connect(self.draw_button, SIGNAL('clicked()'), self.on_plot)
        
        #self.grid_cb = QCheckBox("Show Grid")
        #self.grid_cb.setChecked(True)
        #self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        #slider_label = QLabel('X-max:')
        #self.slider = QSlider(Qt.Horizontal)
        #self.slider.setRange(1, 75)
        #self.slider.setValue(65)
        #self.slider.setTracking(True)
        #self.slider.setTickPosition(QSlider.TicksBothSides)
        #self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)
 
        param_label = QLabel('Parameter:')
        self.param_cbox = QComboBox()
        paramlist = ['ENR','FINT','EXP','BTF','BTFP','XFL1','XFL2','ROD','LOCK']
        for i in paramlist:
            self.param_cbox.addItem(i)
        #self.connect(self.param_cbox, SIGNAL('currentIndexChanged(int)'), self.on_plot)
        param_hbox = QHBoxLayout()
        param_hbox.addWidget(param_label)
        param_hbox.addWidget(self.param_cbox)
        self.connect(self.param_cbox, SIGNAL('currentIndexChanged(int)'), self.set_pinvalues)

        case_label = QLabel('Case number:')
        self.case_cbox = QComboBox()
        #caselist = ['1', '2', '3']
        #for i in caselist:
        #    self.case_cbox.addItem(i)
        case_hbox = QHBoxLayout()
        case_hbox.addWidget(case_label)
        case_hbox.addWidget(self.case_cbox)
        #self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'), self.set_pinvalues)
        #self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'), self.fig_update)

        point_label = QLabel('Point number:')
        self.point_sbox = QSpinBox()
        self.point_sbox.setMinimum(0)
        self.point_sbox.setMaximum(10000)
        point_hbox = QHBoxLayout()
        point_hbox.addWidget(point_label)
        point_hbox.addWidget(self.point_sbox)
        self.connect(self.point_sbox, SIGNAL('valueChanged(int)'), self.set_pinvalues)

        self.enr_plus_button = QPushButton("+ enr")
        self.enr_minus_button = QPushButton("- enr")
        enr_hbox = QHBoxLayout()
        enr_hbox.addWidget(self.enr_minus_button)
        enr_hbox.addWidget(self.enr_plus_button)
        self.connect(self.enr_plus_button, SIGNAL('clicked()'), self.enr_add)
        self.connect(self.enr_minus_button, SIGNAL('clicked()'), self.enr_sub)
        self.enr_case_cb = QCheckBox("All cases")
        self.enr_case_cb.setChecked(False)
        enr_case_hbox = QHBoxLayout()
        enr_case_hbox.addWidget(self.enr_case_cb)

        self.calc_quick_button = QPushButton("Quick calc")
        self.calc_full_button = QPushButton("Full calc")
        calc_hbox = QHBoxLayout()
        calc_hbox.addWidget(self.calc_quick_button)
        calc_hbox.addWidget(self.calc_full_button)
        self.connect(self.calc_quick_button, SIGNAL('clicked()'), self.quick_calc)

        type_label = QLabel('Type:')
        self.type_cbox = QComboBox()
        typelist = ['Hot', 'HCr', 'CCl', 'CCr']
        for i in typelist:
            self.type_cbox.addItem(i)
        #self.connect(self.type_cbox, SIGNAL('currentIndexChanged(int)'), self.on_index)

        voi_label = QLabel('VOI:')
        self.voi_cbox = QComboBox()
        self.voilist = ['0', '40', '80']
        for i in self.voilist:
            self.voi_cbox.addItem(i)
        # Determine voi index
        #voi = self.cas.cases[self.case_id_current].statepts[0].voi
        #voi_index = [i for i,v in enumerate(self.voilist) if int(v) == voi]
        #voi_index = voi_index[0]
        #self.voi_cbox.setCurrentIndex(voi_index)
        #self.connect(self.voi_cbox, SIGNAL('currentIndexChanged(int)'), self.on_plot)

        vhi_label = QLabel('VHI:')
        self.vhi_cbox = QComboBox()
        self.vhilist = ['0', '40', '80']
        for i in self.vhilist:
            self.vhi_cbox.addItem(i)
        # Determine vhi index
        #vhi = self.cas.cases[self.case_id_current].statepts[0].vhi
        #vhi_index = [i for i,v in enumerate(self.vhilist) if int(v) == vhi]
        #vhi_index = vhi_index[0]
        #self.vhi_cbox.setCurrentIndex(vhi_index)
        #self.connect(self.vhi_cbox, SIGNAL('currentIndexChanged(int)'), self.on_plot)


        #self.case_cbox.setWhatsThis("What is this?")

        #self.connect(self.case_cbox, SIGNAL('activated(QString)'), self.on_case)
        #self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'), self.on_plot)
        
        # Info form layout
        info_flo = QFormLayout()
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        #sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.ave_enr_text.sizePolicy().hasHeightForWidth())
        self.sim_text = QLineEdit()
        self.sim_text.setSizePolicy(sizePolicy)
        self.sim_text.setReadOnly(True)
        #text = self.bundle.cases[0].states[0].sim
        #self.sim_text.setText(text)
        info_flo.addRow("SIM", self.sim_text)

        self.rod_types_text = QLineEdit()
        self.rod_types_text.setSizePolicy(sizePolicy)
        self.rod_types_text.setReadOnly(True)
        info_flo.addRow("Rod types", self.rod_types_text)
        
        self.ave_enr_text = QLineEdit()
        self.ave_enr_text.setSizePolicy(sizePolicy)
        self.ave_enr_text.setReadOnly(True)
        info_flo.addRow("Segment %U-235", self.ave_enr_text)
        
        self.bundle_enr_text = QLineEdit()
        self.bundle_enr_text.setSizePolicy(sizePolicy)
        self.bundle_enr_text.setReadOnly(True)
        info_flo.addRow("Bundle %U-235", self.bundle_enr_text)
        #self.bundle_enr_text.setText('2.818')
        
        # Define table widget
        self.table = QTableWidget()
        self.table.setRowCount(100)
        self.table.setColumnCount(4)
        #self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.table.setMinimumWidth(180)
        self.table.setHorizontalHeaderLabels(('Index','EXP','FINT','BTF'))
        self.table.setSortingEnabled(True)
        self.table.setColumnHidden(0,True)
        
        #self.connect(self.table.horizontalHeader(),SIGNAL('QHeaderView.sortIndicatorChanged(int)'),self.openFile)
        self.connect(self.table.horizontalHeader(),SIGNAL('sectionClicked(int)'),self.tableHeaderSort)
        self.connect(self.table.verticalHeader(),SIGNAL('sectionClicked(int)'),self.pinSelect)
        #self.connect(self.table,SIGNAL('cellClicked(int,int)'),self.pinSelect)
        #self.connect(self.table,SIGNAL('currentChanged(int)'),self.pinSelect)
        #Tracer()()
        self.table.cellActivated.connect(self.pinSelect)
        self.table.cellClicked.connect(self.pinSelect)
        #self.table.selectionModel().selectionChanged.connect(self.pinSelect)

        tvbox = QVBoxLayout()
        tvbox.addWidget(self.table)
        tableGbox = QGroupBox()
        tableGbox.setStyleSheet("QGroupBox { background-color: rgb(200, 200,\
        200); border:1px solid gray; border-radius:5px;}")
        tableGbox.setLayout(tvbox)
        
        #self.hview = QHeaderView

       #self.tableview = QTableView()
        #self.connect(self.table.horizontalHeader().sectionClicked(), SIGNAL('logicalIndex(int)'),self.openFile)
        #self.connect(QHeaderView.sortIndicatorChanged(), SIGNAL('logicalIndex(int)'),self.openFile)
        

        #self.setpincoords()
        self.table.resizeColumnsToContents()
        #Tracer()()

        #
        # Layout with box sizers
        # 
        vbox = QVBoxLayout()
        vbox.addLayout(param_hbox)
        vbox.addLayout(case_hbox)
        vbox.addLayout(point_hbox)
        vbox.addLayout(enr_hbox)
        vbox.addLayout(enr_case_hbox)
        vbox.addLayout(calc_hbox)
        

        #spacerItem = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Minimum)
        #vbox.addItem(spacerItem)
        vbox.addStretch(1)
        vbox.addLayout(info_flo)
        
        groupbox = QGroupBox()
        groupbox.setStyleSheet("QGroupBox { background-color: rgb(200, 200,\
        200); border:1px solid gray; border-radius:5px;}")
        groupbox.setLayout(vbox)

        #for w in [  self.textbox, self.draw_button, self.grid_cb,
        #            slider_label, self.slider]:
        
        #for w in [  type_label, self.type_cbox, voi_label, self.voi_cbox,
        #            vhi_label, self.vhi_cbox]:
        #
        #    vbox.addWidget(w)
        #    vbox.setAlignment(w, Qt.AlignHCenter)
        

        #self.bundle = Bundle()
        #self.bundle.setParent(self.main_frame)
        #Tracer()()

        hbox = QHBoxLayout()

        #hbox.addWidget(self.bundle)
        #vbox.addLayout(hbox)
        #vbox.addWidget(self.canvas)
        #hbox2.addWidget(self.mpl_toolbar)
        
        spacerItemH = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        #hbox.addLayout(vbox)
        hbox.addWidget(groupbox)
        #hbox.addItem(spacerItemH)
        #hbox.addWidget(self.canvas)
        hbox.addWidget(canvasGbox)
        #hbox.addItem(spacerItemH)
        hbox.addWidget(tableGbox)
        #hbox.addWidget(self.table)
        #hbox.addItem(spacerItemH)

        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)
        #Tracer()()
    
    def create_status_bar(self):
        self.status_text = QLabel("Main window")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        save_settings_action = self.create_action("&Save settings...",
            shortcut="Ctrl+E", slot=self.save_plot, 
            tip="Save settings")
        quit_action = self.create_action("&Quit", slot=self.close, 
                                         shortcut="Ctrl+Q", tip="Close the application")
        
        open_file_action = self.create_action("&Open file...", slot=self.openFile,
                                              shortcut="Ctrl+L", tip="Open file")

        save_data_action = self.create_action("&Save data...", slot=self.saveData,
                                              shortcut="Ctrl+S", tip="Save data to file")

        self.add_actions(self.file_menu, 
            (open_file_action, save_data_action, save_settings_action, None, quit_action))


        self.edit_menu = self.menuBar().addMenu("&Edit") 
        preferences = self.create_action("Preferences...", tip="Preferences...")        
        self.add_actions(self.edit_menu, (None, preferences))

        self.tools_menu = self.menuBar().addMenu("&Tools")
        plot_action = self.create_action("Plot...", tip="Plot...", slot=self.plotWin)
        btf_action = self.create_action("BTF...", tip="BTF...")
        casmo_action = self.create_action("CASMO...", tip="CASMO...")
        data_action = self.create_action("Fuel data...", tip="Fuel data...")
        table_action = self.create_action("Point table...", tip="Point table...")
        optim_action = self.create_action("Optimization...", tip="BTF optimization...")
        egv_action = self.create_action("EGV...", tip="EGV...")
        self.add_actions(self.tools_menu, 
                         (plot_action, btf_action, casmo_action, data_action,
                          table_action, optim_action, egv_action))
        
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def create_toolbar(self):
        exitAction = QAction(QIcon('icons/exit-icon_32x32.png'), 'Exit', self)
        #exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        fileAction = QAction(QIcon('icons/open-file-icon_32x32.png'), 'Open file', self)
        fileAction.setStatusTip('Open file')
        fileAction.triggered.connect(self.openFile)

        settingsAction = QAction(QIcon('icons/preferences-icon_32x32.png'), 'Settings', self)
        settingsAction.setStatusTip('Settings')

        plotAction = QAction(QIcon('icons/diagram-icon_32x32.png'), 'Plot', self)
        plotAction.setStatusTip('Open plot window')
        plotAction.triggered.connect(self.plotWin)

        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(fileAction)
        toolbar.addAction(settingsAction)
        toolbar.addAction(plotAction)
        toolbar.addAction(exitAction)

        toolbar.setMovable(False)
        toolbar.setFloatable(True)
        toolbar.setAutoFillBackground(False)


    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def closeEvent(self, event):
        # Write window size and position to config file
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("size", QVariant(self.size()))
        self.settings.setValue("pos", QVariant(self.pos()))
        self.settings.endGroup()
        print "Good bye!"
        

def main():
    app = QApplication(sys.argv)
    window = MainWin()
    window.show()
    #app.exec_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
