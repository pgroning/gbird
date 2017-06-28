"""
This is the 2D plot window
This window embeds a matplotlib plot into a PyQt4 GUI application
"""

from IPython.core.debugger import Tracer  # Set tracepoints
# Set a tracepoint that works with Qt
from pyqt_trace import pyqt_trace as qtrace

import sys
import os

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


class PlotWin(QtGui.QMainWindow):
    def __init__(self, parent=None, plotmode=None):
        super(PlotWin, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle('Plot Window')

        # Initial window size/pos last saved
        default_size = parent.config.plotwin_size
        default_pos = parent.config.plotwin_pos
        self.settings = QtCore.QSettings("greenbird")
        self.settings.beginGroup("PlotWindow")
        
        size = self.settings.value(
            "size", QtCore.QVariant(QtCore.QSize(*default_size))).toSize()
        self.resize(size)
        pos = self.settings.value(
            "pos", QtCore.QVariant(QtCore.QPoint(*default_pos))).toPoint()
        self.move(pos)
        self.settings.endGroup()
                
        self.create_menu()
        self.create_main_frame()
                
        if plotmode == "pin":  # plot single pin
            self.plotmode_cbox.setCurrentIndex(1)

        self.on_plot()  # Init plot

    def plot_xy(self, x, y, ylabel, legend, linestyle):
        self.axes.plot(x, y, label=legend, linestyle=linestyle)
        if legend:
            self.axes.legend(loc='best', prop={'size': 8})
        self.axes.set_xlabel('Burnup (MWd/kgU)')
        self.axes.set_ylabel(ylabel)
        self.on_draw()
        self.x_data = x
        self.y_data = y

    def plot_kinf(self, segment, voi, vhi, tfu, linestyle="-", label=None):
        """Plot kinf as a function of burnup"""
        
        statepoints = segment.get_statepoints(voi, vhi, tfu)
        x = [s.burnup for s in statepoints]
        y = [s.kinf for s in statepoints]
        
        if label == None:
            labstr = segment.data.sim
            labstr = labstr.replace("SIM", "").replace("'", "").strip()
        else:
            labstr = label
        self.plot_xy(x, y, "K-inf", labstr, linestyle)

    def plot_fint(self, segment, voi, vhi, tfu, linestyle="-", label=None):

        statepoints = segment.get_statepoints(voi, vhi, tfu)
        x = [s.burnup for s in statepoints]
        if self.plotmode_cbox.currentIndex() == 0:  # plot envelope
            y = [s.fint for s in statepoints]
        elif self.plotmode_cbox.currentIndex() == 1:  # plot specific pin
            if hasattr(self.parent, "pinselection_index"):
                ipin = self.parent.pinselection_index
            else:
                ipin = 0
            iseg = int(self.parent.ui.case_cbox.currentIndex())
            i, j = self.parent.pinobjects[iseg][ipin].pos
            y = [s.POW[i, j] for s in statepoints]

        if label == None:
            labstr = segment.data.sim
            labstr = labstr.replace("SIM", "").replace("'", "").strip()
            if self.plotmode_cbox.currentIndex() == 1:
                coordstr = self.parent.pinobjects[iseg][ipin].coord
                labstr = coordstr + ": " + labstr
        else:
            labstr = label
        self.plot_xy(x, y, "Fint", labstr, linestyle)

    def plot_btf(self, bundle, linestyle="-", label=None):

        x = bundle.btf.burnpoints
        DOX = bundle.btf.DOX
        if self.plotmode_cbox.currentIndex() == 0:  # plot envelope
            y = [e.max() for e in DOX]
        elif self.plotmode_cbox.currentIndex() == 1:  # plot pin
            if hasattr(self.parent, "pinselection_index"):
                ipin = self.parent.pinselection_index
            else:
                ipin = 0
            iseg = int(self.parent.ui.case_cbox.currentIndex())
            i, j = self.parent.pinobjects[iseg][ipin].pos
            y = [e[i, j] for e in DOX]
            label = self.parent.pinobjects[iseg][ipin].coord

        self.plot_xy(x, y, "BTF", label, linestyle)

    def export_to_ascii(self):
        """Write data to YAML format"""

        outfile = self.select_outfile()
        if not outfile:
            return
        print "Export data to file: " + outfile

        f = open(outfile, "w")
        f.write("x: [")
        for i, x in enumerate(self.x_data):
            if i == 0:
                f.write(str(x))
            else:
                f.write(", " + str(x))
        f.write("]")
        f.write("\n")
        f.write("y: [")
        for i, y in enumerate(self.y_data):
            if i == 0:
                f.write(str(y))
            else:
                f.write(", " + str(y))
        f.write("]")
        f.close()

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
        
    def on_draw(self):
        """ Redraws the figure"""

        self.axes.grid(self.grid_cb.isChecked())        
        self.canvas.draw()

    def on_plot(self):

        case_id = int(self.parent.ui.case_cbox.currentIndex())
        case_id_max = len(self.parent.bunlist[-1].segments)
        
        param = self.param_cbox.currentText()
        
        ibundle = self.parent.ibundle
        bunlist = self.parent.bunlist
        ipoint = self.parent.ui.point_sbox.value()
        
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
                    segment = bunlist[ibundle].segments[iseg]
                    self.plot_kinf(segment, voi=voi, vhi=vhi, tfu=tfu)
            else:
                segment = bunlist[ibundle].segments[case_id]
                self.plot_kinf(segment, voi=voi, vhi=vhi, tfu=tfu)
                if ibundle > 0:
                    if self.previous_cb.isChecked():
                        segment = bunlist[ibundle-1].segments[case_id]
                        self.plot_kinf(segment, voi=voi, vhi=vhi, tfu=tfu,
                                       linestyle="--", label="previous")
                    if self.original_cb.isChecked():
                        segment = bunlist[0].segments[case_id]
                        self.plot_kinf(segment, voi=voi, vhi=vhi, tfu=tfu,
                                       linestyle="--", label="original")

        elif param == "FINT":
            if self.case_cb.isChecked():
                for iseg in range(case_id_max):
                    segment = bunlist[ibundle].segments[iseg]
                    self.plot_fint(segment, voi=voi, vhi=vhi, tfu=tfu)
            else:
                segment = bunlist[ibundle].segments[case_id]
                self.plot_fint(segment, voi=voi, vhi=vhi, tfu=tfu)
                if ibundle > 0:
                    if self.previous_cb.isChecked():
                        segment = bunlist[ibundle-1].segments[case_id]
                        self.plot_fint(segment, voi=voi, vhi=vhi, tfu=tfu,
                                       linestyle="--", label="previous")
                    if self.original_cb.isChecked():
                        segment = bunlist[0].segments[case_id]
                        self.plot_fint(segment, voi=voi, vhi=vhi, tfu=tfu,
                                       linestyle="--", label="original")

        elif param == 'BTF':
            bundle = bunlist[ibundle]
            self.plot_btf(bundle)
            if ibundle > 0:
                if self.previous_cb.isChecked():
                    bundle = bunlist[ibundle-1]
                    self.plot_btf(bundle, linestyle="--", label="previous")
                if self.original_cb.isChecked():
                    bundle = bunlist[0]
                    self.plot_btf(bundle, linestyle="--", label="original")
 
    def create_main_frame(self):
        """Create the mpl Figure and FigCanvas objects"""

        self.main_frame = QtGui.QWidget()
        
        self.dpi = 100
        self.fig = Figure((7, 5), dpi=self.dpi)
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                                  QtGui.QSizePolicy.Expanding)

        self.axes = self.fig.add_subplot(111)
        
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls        
        self.draw_button = QtGui.QPushButton("Update")
        self.connect(self.draw_button, QtCore.SIGNAL('clicked()'), 
                     self.on_plot)
        
        self.grid_cb = QtGui.QCheckBox("Show Grid")
        self.grid_cb.setChecked(True)
        self.connect(self.grid_cb, QtCore.SIGNAL('stateChanged(int)'), 
                     self.on_draw)
                
        param_label = QtGui.QLabel('Param:')
        self.param_cbox = QtGui.QComboBox()
        paramlist = ["KINF", "FINT", "BTF"]
        for p in paramlist:
            self.param_cbox.addItem(p)

        parent_param = str(self.parent.ui.param_cbox.currentText())
        if parent_param in paramlist:
            i = paramlist.index(parent_param)
            self.param_cbox.setCurrentIndex(i)
        else:
            self.param_cbox.setCurrentIndex(0)
        
        self.connect(self.param_cbox,
                     QtCore.SIGNAL('currentIndexChanged(int)'), self.on_plot)
        
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

        self.plotmode_cbox = QtGui.QComboBox()
        modelist = ["Env.", "Pin"]
        for t in modelist:
            self.plotmode_cbox.addItem(t)

        self.connect(self.plotmode_cbox,
                     QtCore.SIGNAL('currentIndexChanged(int)'), self.on_plot)


        
        # Layout with sizers
        param_flo = QtGui.QFormLayout()
        param_flo.addRow("Param:", self.param_cbox)
 
        hbox = QtGui.QHBoxLayout()
        
        for w in [self.grid_cb, self.case_cb, self.original_cb, 
                  self.previous_cb]:
            hbox.addWidget(w)
            
        hbox.addStretch(1)
        hbox.addLayout(param_flo)
        hbox.addWidget(self.plotmode_cbox)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        vbox.addWidget(self.canvas)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
            
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        save_file_action = self.create_action("&Save Figure As...",
                                              shortcut="Ctrl+S",
                                              slot=self.save_figure,
                                              tip="Save figure...")
        quit_action = self.create_action("&Close", slot=self.close,
                                         shortcut="Ctrl+W",
                                         tip="Close the application")
        
        export_action = self.create_action("&Export to ascii...",
                                           slot=self.export_to_ascii,
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
        about_action = self.create_action("&About",
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

    def select_outfile(self):
        """Select a file to write data."""

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
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
