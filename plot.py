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
        
        # Retrieve initial data
        # self.parent = parent
        # self.data_init()
        
        self.case_id_current = int(self.parent.case_cbox.currentIndex())
        
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        # self.textbox.setText('1 2 3 4')
        # self.data_init()
        
        # self.case_cbox.setCurrentIndex(0) # Set default plot case
        # self.case_id_current = 0
        self.on_plot()  # Init plot

        # self.on_draw()

    # def data_init(self):
    #    self.bundle = self.parent.bundle
    #    #self.cas = casio()
    #    #self.cas.loadpic('caxfiles.p')

    def plot_kinf(self, case_id, state_num=-1, linestyle="-"):
        
        # case = self.cas.cases[case_id]
        case = self.parent.bundle.cases[case_id]
        idx0 = self.startpoint(case_id)
        # statepts = case.statepts[idx0:]
        statepoints = case.states[state_num].statepoints[idx0:]
        
        burnup_old = 0.0
        for idx, p in enumerate(statepoints):
            if p.burnup < burnup_old:
                break
            burnup_old = p.burnup
        
        x = [statepoints[i].burnup for i in range(idx)]
        y = [statepoints[i].kinf for i in range(idx)]
        
        labstr = case.states[0].sim
        labstr = labstr.replace("SIM", "").replace("'", "").strip()
        # labstr = case.states[0].caxfile
        # labstr = os.path.split(labstr)[1]
        # labstr = os.path.splitext(labstr)[0]
        
        self.axes.plot(x, y, label=labstr, linestyle=linestyle)
        self.axes.set_xlabel('Burnup (MWd/kgU)')
        self.axes.set_ylabel('K-inf')
        self.axes.legend(loc='best', prop={'size': 8})
        self.canvas.draw()
        self.on_draw()

    def plot_fint(self, case_id, state_num=-1, linestyle="-"):

        case = self.parent.bundle.cases[case_id]
        idx0 = self.startpoint(case_id)
        statepoints = case.states[state_num].statepoints[idx0:]

        burnup_old = 0.0
        for idx, p in enumerate(statepoints):
            if p.burnup < burnup_old:
                break
            burnup_old = p.burnup

        x = [statepoints[i].burnup for i in range(idx)]
        y = [statepoints[i].fint for i in range(idx)]

        labstr = case.states[0].sim
        labstr = labstr.replace("SIM", "").replace("'", "").strip()
        # labstr = case.states[-1].caxfile
        # labstr = os.path.split(labstr)[1]
        # labstr = os.path.splitext(labstr)[0]
        
        self.axes.plot(x, y, label=labstr, linestyle=linestyle)
        self.axes.set_xlabel('Burnup (MWd/kgU)')
        self.axes.set_ylabel('Fint')
        self.axes.legend(loc='best', prop={'size': 8})
        self.canvas.draw()
        self.on_draw()

    def plot_btf(self, case_id, state_num=-1, linestyle="-"):
        
        # x = self.cas.btf.burnpoints
        x = self.parent.bundle.states[state_num].btf.burnpoints
        # DOX = self.cas.btf.DOX
        DOX = self.parent.bundle.states[state_num].btf.DOX
        y = [elem.max() for elem in DOX]
        self.axes.plot(x, y, linestyle=linestyle)
        
        self.axes.set_xlabel('Burnup (MWd/kgU)')
        self.axes.set_ylabel('BTF')
        self.on_draw()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 'Save file', '',
                                                   file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
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

    def startpoint(self, case_id):
        voi_val = int(self.voi_cbox.currentText())
        vhi_val = int(self.vhi_cbox.currentText())
        type_val = str(self.type_cbox.currentText())
        
        # case = self.cas.cases[case_id]
        case = self.parent.bundle.cases[case_id]
        
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

    def on_plot(self):
        
        case_id = self.case_id_current
        # case_id_max = len(self.cas.cases)
        case_id_max = len(self.parent.bundle.cases)
        param = self.param_cbox.currentText()
        
        self.axes.clear()
        if param == 'Kinf':
            if self.case_cb.isChecked():
                for i in range(case_id_max):
                    # idx0 = self.startpoint(i)
                    self.plot_kinf(i)
            else:
                # idx0 = self.startpoint(case_id)
                self.plot_kinf(case_id)
                if self.original_cb.isChecked():
                    self.plot_kinf(case_id, state_num=0, linestyle="--")

        elif param == 'Fint':
            if self.case_cb.isChecked():
                for i in range(case_id_max):
                    self.plot_fint(i)
            else:
                self.plot_fint(case_id)
                if self.original_cb.isChecked():
                    self.plot_fint(case_id, state_num=0, linestyle="--")

        elif param == 'BTF':
            if self.case_cb.isChecked():
                for i in range(case_id_max):
                    self.plot_btf(i)
            else:
                self.plot_btf(case_id)
                if self.original_cb.isChecked():
                    self.plot_btf(case_id, state_num=0, linestyle="--")
 

#    def on_index(self):
#        print "Find index"
#        case_id = self.case_id_current
#        case = self.cas.cases[case_id]
#        burnup = None
#        voi_val = int(self.voi_cbox.currentText())
#        vhi_val = int(self.vhi_cbox.currentText())
#        type_val = str(self.type_cbox.currentText())
#        print type_val,voi_val,vhi_val
#        
#       index = self.cas.findpoint(case,burnup,vhi,voi)
#       index = self.cas.findpoint(case,vhi=vhi_val,voi=voi_val)
#        index = self.cas.findpoint(case,voi=voi_val,vhi=vhi_val)
#        idx0 = case.findpoint(voi=voi_val,vhi=vhi_val)
#
#        if type_val == 'CCl':
#            idx0 = case.findpoint(tfu=293)
#            print idx0

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
        
        self.draw_button = QtGui.QPushButton("Redraw")
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
        paramlist = ['Kinf', 'Fint', 'BTF']
        for i in paramlist:
            self.param_cbox.addItem(i)
        # self.connect(self.param_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)
        
        # case_label = QLabel('All cases:')
        self.case_cb = QtGui.QCheckBox("All seg.")
        self.case_cb.setChecked(False)
        self.connect(self.case_cb, QtCore.SIGNAL('stateChanged(int)'), 
                     self.on_plot)
#       self.case_cbox = QComboBox()
#       caselist = ['1','2','3','All']
#       for i in caselist:
#            self.case_cbox.addItem(i)
        
        self.original_cb = QtGui.QCheckBox("Plot orig.")
        self.original_cb.setChecked(False)
        self.connect(self.original_cb, QtCore.SIGNAL('stateChanged(int)'),
                     self.on_plot)

        type_label = QtGui.QLabel('Type:')
        self.type_cbox = QtGui.QComboBox()
        typelist = ['Hot', 'HCr', 'CCl', 'CCr']
        for i in typelist:
            self.type_cbox.addItem(i)
        # self.connect(self.type_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_index)

        voi_label = QtGui.QLabel('VOI:')
        self.voi_cbox = QtGui.QComboBox()
        # self.voilist = ['0', '40', '80']
        self.voilist = (self.parent.bundle.cases[self.case_id_current]
                        .states[-1].voivec)
        # self.voilist = map(str, self.voilist)
        
        for v in self.voilist:
            self.voi_cbox.addItem(str(v))
        # Determine voi index
        voi = (self.parent.bundle.cases[self.case_id_current].states[-1]
               .statepoints[0].voi)
        # voi = self.cas.cases[self.case_id_current].statepts[0].voi
        voi_index = [i for i, v in enumerate(self.voilist) if int(v) == voi]
        
        voi_index = voi_index[0]
        self.voi_cbox.setCurrentIndex(voi_index)
        # self.connect(self.voi_cbox, SIGNAL('currentIndexChanged(int)'),
        # self.on_plot)
        vhi_label = QtGui.QLabel('VHI:')
        self.vhi_cbox = QtGui.QComboBox()
        # self.vhilist = ['0', '40', '80']
        self.vhilist = self.voilist
        for v in self.vhilist:
            self.vhi_cbox.addItem(str(v))
        
        # Determine vhi index
        # vhi = self.cas.cases[self.case_id_current].statepts[0].vhi
        vhi = (self.parent.bundle.cases[self.case_id_current].states[-1]
               .statepoints[0].vhi)
        vhi_index = [i for i, v in enumerate(self.vhilist) if int(v) == vhi]
        vhi_index = vhi_index[0]
        self.vhi_cbox.setCurrentIndex(vhi_index)
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
        hbox = QtGui.QHBoxLayout()
        
        # for w in [  self.textbox, self.draw_button, self.grid_cb,
        #            slider_label, self.slider]:
        
        for w in [self.draw_button, self.grid_cb, slider_label, self.slider,
                  self.case_cb, self.original_cb, param_label, self.param_cbox,
                  type_label, self.type_cbox, voi_label, self.voi_cbox,
                  vhi_label, self.vhi_cbox]:

            hbox.addWidget(w)
            hbox.setAlignment(w, QtCore.Qt.AlignVCenter)
        
        vbox = QtGui.QVBoxLayout()
        # vbox.addLayout(hbox)
        # vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        vbox.addWidget(self.canvas)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    def create_status_bar(self):
        self.status_text = QtGui.QLabel("Plot window")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        save_file_action = self.create_action("&Save plot", shortcut="Ctrl+S",
                                              slot=self.save_plot,
                                              tip="Save the plot")
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


def main():
    app = QApplication(sys.argv)
    window = PlotWin()
    window.show()
    # app.exec_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
