"""
This is the 2D plot window
This window embeds a matplotlib (mpl) plot into a PyQt4 GUI application
"""

from IPython.core.debugger import Tracer  # Set tracepoints
# Set a tracepoint that works with Qt
from pyqt_trace import pyqt_trace as qtrace

import sys
import os
import numpy as np

from PyQt4 import QtGui, QtCore

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as \
    FigureCanvas
try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as \
        NavigationToolbar
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as \
        NavigationToolbar
from matplotlib.figure import Figure

from bundle import Bundle


class PlotWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(PlotWin, self).__init__(parent)
        self.parent = parent
        # QMainWindow.__init__(self, parent)
        self.setWindowTitle('Plot Window')
        # self.move(600,300)

        self.settings = QtCore.QSettings("greenbird")
        self.settings.beginGroup("PlotWindow")
        self.resize(self.settings.value("size", QtCore.QVariant(QtCore.QSize(800, 650))).toSize())
        self.move(self.settings.value("pos", QtCore.QVariant(QtCore.QPoint(600, 300))).toPoint())
        self.settings.endGroup()
                
        self.create_menu()
        self.create_main_frame()
        #self.create_status_bar()
        
        # self.textbox.setText('1 2 3 4')
        # self.data_init()
        
        # self.case_cbox.setCurrentIndex(0) # Set default plot case
        # self.case_id_current = 0
        self.on_plot()  # Init plot

    def get_xy(self, segment, parameter):
        ipoint = self.parent.point_sbox.value()
        voi = segment.statepoints[ipoint].voi
        vhi = segment.statepoints[ipoint].vhi
        tfu = segment.statepoints[ipoint].tfu
        print voi, vhi, tfu
        print " "
        statepoints = segment.get_statepoints(voi, vhi, tfu)
        x = [s.burnup for s in statepoints]
        if parameter == "KINF":
            y = [s.kinf for s in statepoints]
        if parameter == "FINT":
            y = [s.fint for s in statepoints]
        return x, y

    def plot_kinf(self, segment, voi, vhi, tfu, linestyle="-"):
        """Plot kinf as a function of burnup"""
        
        statepoints = segment.get_statepoints(voi, vhi, tfu)
        x = [s.burnup for s in statepoints]
        y = [s.kinf for s in statepoints]
        
        labstr = segment.data.sim
        labstr = labstr.replace("SIM", "").replace("'", "").strip()
        
        self.axes.plot(x, y, label=labstr, linestyle=linestyle)
        self.axes.set_xlabel('Burnup (MWd/kgU)')
        self.axes.set_ylabel('K-inf')
        self.axes.legend(loc='best', prop={'size': 8})
        self.on_draw()

    def plot_fint(self, segment, voi, vhi, tfu, linestyle="-"):

        statepoints = segment.get_statepoints(voi, vhi, tfu)
        x = [s.burnup for s in statepoints]
        y = [s.fint for s in statepoints]

        labstr = segment.data.sim
        labstr = labstr.replace("SIM", "").replace("'", "").strip()
        
        self.axes.plot(x, y, label=labstr, linestyle=linestyle)
        self.axes.set_xlabel('Burnup (MWd/kgU)')
        self.axes.set_ylabel('Fint')
        self.axes.legend(loc='best', prop={'size': 8})
        self.on_draw()

    def plot_btf(self, bundle, linestyle="-"):

        x = bundle.btf.burnpoints
        DOX = bundle.btf.DOX
        y = [e.max() for e in DOX]
                
        self.axes.plot(x, y, linestyle=linestyle)
        self.axes.set_xlabel('Burnup (MWd/kgU)')
        self.axes.set_ylabel('BTF')
        self.on_draw()

    def save_figure(self):
        """save figure"""

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
    
    def on_about(self):
        msg = """Greenbird plot window"""
        QtGui.QMessageBox.about(self, "About the window", msg.strip())
    
    def on_pick(self, event):
        # matplotlib.backend_bases.PickEvent
        #
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QtGui.QMessageBox.information(self, "Click!", msg)
    
    def on_draw(self):
        """ Redraws the figure
        """
        # str = unicode(self.textbox.text())
        # self.data = map(int, str.split())
        # self.data = np.array(map(int, str.split()))

        # x = range(len(self.data))
        # x = np.arange(len(self.data))

        # clear the axes and redraw the plot anew
        #
        # self.axes.clear()        
        self.axes.grid(self.grid_cb.isChecked())

        xmax = self.slider.value()
        self.axes.set_xlim(0, xmax)

        # self.axes.plot(x,x**2,'r')
        # self.axes.bar(
        #    left=x, 
        #    height=self.data, 
        #    width=self.slider.value() / 100.0, 
        #    align='center', 
        #    alpha=0.44,
        #    picker=5)
        
        self.canvas.draw()

    def startpoint(self, iseg, istate):
        voi_val = int(self.voi_cbox.currentText())
        vhi_val = int(self.vhi_cbox.currentText())
        type_val = str(self.type_cbox.currentText())
        
        segment = self.parent.bunlist[istate].segments[iseg]
        
        if type_val == 'CCl':
            idx0 = segment.findpoint(tfu=293)
            voi = segment.statepts[idx0].voi
            vhi = segment.statepts[idx0].vhi
            voi_index = [i for i, v in enumerate(self.voilist)
                         if int(v) == voi][0]
            vhi_index = [i for i, v in enumerate(self.vhilist)
                         if int(v) == vhi][0]
            self.voi_cbox.setCurrentIndex(voi_index)
            self.vhi_cbox.setCurrentIndex(vhi_index)
        else:
            idx0 = segment.findpoint(voi=voi_val, vhi=vhi_val)
        return idx0

    def on_plot(self):

        case_id = int(self.parent.case_cbox.currentIndex())
        case_id_max = len(self.parent.bunlist[-1].segments)
        
        param = self.param_cbox.currentText()
        ibundle = self.parent.ibundle

        ipoint = self.parent.point_sbox.value()
        statepoint = (self.parent.bunlist[ibundle]
                      .segments[case_id].statepoints[ipoint])
        voi = statepoint.voi
        vhi = statepoint.vhi
        tfu = statepoint.tfu
        tmo = statepoint.tmo
        fmtstr = ("VOI={0:.0f} : VHI={1:.0f} : TFU={2:.0f} : TMO={3:.0f}"
                  .format(voi, vhi, tfu, tmo))
        self.statusBar().showMessage(fmtstr)
        
        self.axes.clear()

        if param == "KINF":
            if self.case_cb.isChecked():
                for iseg in range(case_id_max):
                    segment = self.parent.bunlist[ibundle].segments[iseg]
                    self.plot_kinf(segment, voi=voi, vhi=vhi, tfu=tfu)
            else:
                segment = self.parent.bunlist[ibundle].segments[case_id]
                self.plot_kinf(segment, voi=voi, vhi=vhi, tfu=tfu)
                if ibundle > 0:
                    if self.original_cb.isChecked():
                        segment = self.parent.bunlist[0].segments[case_id]
                        self.plot_kinf(segment, voi=voi, vhi=vhi, tfu=tfu,
                                       linestyle="--")
                    if self.previous_cb.isChecked():
                        segment = self.parent.bunlist[ibundle-1].segments[case_id]
                        self.plot_kinf(segment, voi=voi, vhi=vhi, tfu=tfu,
                                       linestyle="--")

        elif param == "FINT":
            if self.case_cb.isChecked():
                for iseg in range(case_id_max):
                    segment = self.parent.bunlist[ibundle].segments[iseg]
                    self.plot_fint(segment, voi=voi, vhi=vhi, tfu=tfu)
            else:
                segment = self.parent.bunlist[ibundle].segments[case_id]
                self.plot_fint(segment, voi=voi, vhi=vhi, tfu=tfu)
                if self.original_cb.isChecked():
                    segment = self.parent.bunlist[0].segments[case_id]
                    self.plot_fint(segment, voi=voi, vhi=vhi, tfu=tfu,
                                   linestyle="--")

        elif param == 'BTF':
            bundle = self.parent.bunlist[ibundle]
            self.plot_btf(bundle)
            if self.original_cb.isChecked():
                bundle = self.parent.bunlist[0]
                self.plot_btf(bundle, linestyle="--")
 
    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((7, 5), dpi=self.dpi)
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                                  QtGui.QSizePolicy.Expanding)

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
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        # 
        # self.textbox = QLineEdit()
        # self.textbox.setMinimumWidth(200)
        # self.connect(self.textbox, SIGNAL('editingFinished ()'),
        # self.on_draw)
        
        self.draw_button = QtGui.QPushButton("Update")
        self.connect(self.draw_button, QtCore.SIGNAL('clicked()'), 
                     self.on_plot)
        
        self.grid_cb = QtGui.QCheckBox("Show Grid")
        self.grid_cb.setChecked(True)
        self.connect(self.grid_cb, QtCore.SIGNAL('stateChanged(int)'), 
                     self.on_draw)
        
        slider_label = QtGui.QLabel('X-max:')
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(1, 75)
        self.slider.setValue(65)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), 
                     self.on_draw)
        
        param_label = QtGui.QLabel('Param:')
        self.param_cbox = QtGui.QComboBox()
        paramlist = ["KINF", "FINT", "BTF"]
        for i in paramlist:
            self.param_cbox.addItem(i)

        parent_param = str(self.parent.param_cbox.currentText())
        if parent_param in paramlist:
            i = paramlist.index(parent_param)
            self.param_cbox.setCurrentIndex(i)
        else:
            self.param_cbox.setCurrentIndex(0)
        
        self.connect(self.param_cbox,
                     QtCore.SIGNAL('currentIndexChanged(int)'), self.on_plot)
        
        # case_label = QLabel('All cases:')
        self.case_cb = QtGui.QCheckBox("Plot all seg.")
        self.case_cb.setChecked(False)
        self.connect(self.case_cb, QtCore.SIGNAL('stateChanged(int)'), 
                     self.on_plot)
        
        self.original_cb = QtGui.QCheckBox("Show original")
        self.original_cb.setChecked(False)
        self.connect(self.original_cb, QtCore.SIGNAL('stateChanged(int)'),
                     self.on_plot)

        self.previous_cb = QtGui.QCheckBox("Show previous")
        self.previous_cb.setChecked(False)
        self.connect(self.previous_cb, QtCore.SIGNAL('stateChanged(int)'),
                     self.on_plot)

        #type_label = QtGui.QLabel('Type:')
        #self.type_cbox = QtGui.QComboBox()
        #typelist = ['Hot', 'HCr', 'CCl', 'CCr']
        #for i in typelist:
        #    self.type_cbox.addItem(i)
        # self.connect(self.type_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_index)

        #voi_label = QtGui.QLabel('VOI:')
        #self.voi_cbox = QtGui.QComboBox()
        ## self.voilist = ['0', '40', '80']
        #iseg = int(self.parent.case_cbox.currentIndex())
        ##iseg = self.case_id_current
        #self.voilist = (self.parent.bunlist[-1].segments[iseg].data.voilist)

        #self.voilist = (self.parent.bundle.cases[self.case_id_current]
        #                .states[-1].voivec)
        # self.voilist = map(str, self.voilist)
        
        #for v in self.voilist:
        #    self.voi_cbox.addItem(str(v))
        # Determine voi index
        #voi = self.parent.bunlist[-1].segments[iseg].statepoints[0].voi
        #voi = (self.parent.bundle.cases[self.case_id_current].states[-1]
        #       .statepoints[0].voi)
        # voi = self.cas.cases[self.case_id_current].statepts[0].voi
        #voi_index = [i for i, v in enumerate(self.voilist) if int(v) == voi]
        #voi_index = voi_index[0]
        #self.voi_cbox.setCurrentIndex(voi_index)
        # self.connect(self.voi_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)
        #vhi_label = QtGui.QLabel('VHI:')
        #self.vhi_cbox = QtGui.QComboBox()
        # self.vhilist = ['0', '40', '80']
        #self.vhilist = self.voilist
        #for v in self.vhilist:
        #    self.vhi_cbox.addItem(str(v))
        
        ## Determine vhi index
        #vhi = self.parent.bunlist[-1].segments[iseg].statepoints[0].vhi
        #vhi = (self.parent.bundle.cases[self.case_id_current].states[-1]
        #       .statepoints[0].vhi)
        #vhi_index = [i for i, v in enumerate(self.vhilist) if int(v) == vhi]
        #vhi_index = vhi_index[0]
        #self.vhi_cbox.setCurrentIndex(vhi_index)
        # self.connect(self.vhi_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)
        
        # tfu_label = QLabel('TFU:')
        # self.tfu_cbox = QComboBox()
        # tfulist = ['293', '333', '372', '423', '483', '539']
        # for i in tfulist:
        #    self.tfu_cbox.addItem(i)
        # Determine tfu index

        # self.case_cbox.setWhatsThis("What is this?")
        # self.connect(self.case_cbox, SIGNAL('activated(QString)'),
        # self.on_case)
        # self.connect(self.case_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)

        #
        # Layout with box sizers
        #

        param_flo = QtGui.QFormLayout()
        param_flo.addRow("Param:", self.param_cbox)
 
        hbox = QtGui.QHBoxLayout()
        
        # for w in [  self.textbox, self.draw_button, self.grid_cb,
        #            slider_label, self.slider]:
        
        #for w in [self.draw_button, self.grid_cb, slider_label, self.slider,
        #          self.case_cb, self.original_cb, param_label,
        #          self.param_cbox]:
        for w in [self.grid_cb, self.case_cb, self.original_cb, 
                  self.previous_cb]:
            hbox.addWidget(w)
            #hbox.setAlignment(w, QtCore.Qt.AlignVCenter)
            #hbox.setAlignment(w, QtCore.Qt.AlignHCenter)
        hbox.addStretch(1)
        hbox.addLayout(param_flo)

        vbox = QtGui.QVBoxLayout()
        # vbox.addLayout(hbox)
        # vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        vbox.addWidget(self.canvas)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    #def create_status_bar(self):
    #    self.status_text = QtGui.QLabel("Plot window")
    #    self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        save_file_action = self.create_action("&Save Figure As...",
                                              shortcut="Ctrl+S",
                                              slot=self.save_figure,
                                              tip="Save figure...")
        quit_action = self.create_action("&Close", slot=self.close,
                                         shortcut="Ctrl+W",
                                         tip="Close the application")
        
        export_action = self.create_action("&Export to ascii",
                                           tip="Export data to ascii file")

        self.add_actions(self.file_menu,
                         (export_action, save_file_action, None, quit_action))

        self.edit_menu = self.menuBar().addMenu("&Edit") 
        preferences = self.create_action("Preferences...",
                                         tip="Preferences...")        
        self.add_actions(self.edit_menu, (None, preferences))

        self.tools_menu = self.menuBar().addMenu("&Tools") 
        options = self.create_action("Options...", tip="Options...")        
        self.add_actions(self.tools_menu, (options,))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", shortcut='F1',
                                          slot=self.on_about,
                                          tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, 
                      icon=None, tip=None, checkable=False, 
                      signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
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

    def closeEvent(self, event):
        """This method is called before closing the window"""

        self.settings.beginGroup("PlotWindow")
        self.settings.setValue("size", QtCore.QVariant(self.size()))
        self.settings.setValue("pos", QtCore.QVariant(self.pos()))
        self.settings.endGroup()

        del self.parent.plotwin  # delete parent attr that holds the object

def main():
    app = QApplication(sys.argv)
    window = PlotWin()
    window.show()
    # app.exec_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
