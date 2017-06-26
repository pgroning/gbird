from pyqt_trace import pyqt_trace as qtrace

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg \
    as FigureCanvas
from matplotlib.figure import Figure


class InfoLabel(QtGui.QLabel):
    def __init__(self, parent=None, width=100):
        QtGui.QLabel.__init__(self)
        self.setStyleSheet("""QLabel {background-color : rgb(245, 245, 245); 
                              color : black;}""")
        self.setFrameStyle(QtGui.QFrame.Panel | 
                           QtGui.QFrame.Sunken)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setFixedHeight(20)
        self.setFixedWidth(width)


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
        
        case_num = int(self.parent.ui.case_cbox.currentIndex())
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


class Ui_MainWindow(object):
    """Creates ui widgets and menus in main frame"""

    def __init__(self, parent=None):
        pass

    def setup(self, parent):
        self.parent = parent
        self.create_statusbar()
        self.create_menu()
        self.create_toolbar()
        self.create_main_frame()

    def create_statusbar(self):
        status_text = QtGui.QLabel("Main window")
        self.parent.statusBar().addWidget(status_text, 1)

    def create_menu(self):
        parent = self.parent

        self.menu_actions = []

        menubar = QtGui.QMenuBar()

        # --- File menu ---
        file_menu = menubar.addMenu("&File")

        new_icon = "new-icon_32x32"
        text = "&New..."
        tip = "Create new bundle"
        shortcut = "Ctrl+N"
        args = (text, new_icon, tip, parent.open_bundle_dlg, shortcut)
        self.new_action = self.__create_action(*args)
        file_menu.addAction(self.new_action)

        file_icon = "open-file-icon_32x32"
        text = "&Open..."
        tip = "Open file"
        shortcut = "Ctrl+O"
        args = (text, file_icon, tip, parent.openFile, shortcut)
        self.file_action = self.__create_action(*args)
        file_menu.addAction(self.file_action)

        save_icon = "save-icon_32x32"
        text = "&Save project..."
        tip = "Save data to file"
        args = (text, save_icon, tip, parent.saveData)
        self.save_action = self.__create_action(*args)
        file_menu.addAction(self.save_action)
        self.menu_actions.append(self.save_action)

        delete_icon = "delete-icon_32x32"
        text = "&Clear project..."
        tip = "Clear current project"
        args = (text, delete_icon, tip, parent.clear_project)
        clear_action = self.__create_action(*args)
        file_menu.addAction(clear_action)
        self.menu_actions.append(clear_action)

        export_icon = "export-icon_32x32"
        text = "&Export to ascii..."
        tip = "Export data to file"
        args = (text, export_icon, tip, parent.export_to_ascii)
        save_file_action = self.__create_action(*args)
        file_menu.addAction(save_file_action)
        self.menu_actions.append(save_file_action)

        export_icon = "export-icon_32x32"
        text = "&Export Figure..."
        tip = "Export fuel map to file"
        args = (text, export_icon, tip, parent.saveFigure)
        save_figure_action = self.__create_action(*args)
        file_menu.addAction(save_figure_action)
        self.menu_actions.append(save_figure_action)

        file_menu.addSeparator()

        quit_icon = "exit-icon_32x32"
        text = "&Quit"
        tip = "Exit application"
        shortcut = "Ctrl+Q"
        args = (text, quit_icon, tip, parent.close, shortcut)
        self.quit_action = self.__create_action(*args)
        file_menu.addAction(self.quit_action)

        # --- Edit menu ---
        edit_menu = menubar.addMenu("&Edit")

        back_icon = "arrow-undo-icon_32x32"
        text = "Back"
        tip = "Back to previous"
        args = (text, back_icon, tip, parent.back_state)
        self.back_action = self.__create_action(*args)
        edit_menu.addAction(self.back_action)
        self.menu_actions.append(self.back_action)

        forward_icon = "arrow-redo-icon_32x32"
        text = "Forward"
        tip = "Forward to next"
        args = (text, forward_icon, tip, parent.forward_state)
        self.forward_action = self.__create_action(*args)
        edit_menu.addAction(self.forward_action)
        self.menu_actions.append(self.forward_action)

        edit_menu.addSeparator()

        plus_icon = "add-icon_32x32"
        text = "Increase enr"
        tip = "Increase enrichment"
        shortcut = QtCore.Qt.Key_Plus
        args = (text, plus_icon, tip, parent.enr_add, shortcut)
        self.increase_enr_action = self.__create_action(*args)
        edit_menu.addAction(self.increase_enr_action)
        self.menu_actions.append(self.increase_enr_action)
        
        minus_icon = "remove-icon_32x32"
        text = "Decrease enr"
        tip = "Decrease enrichment"
        shortcut = QtCore.Qt.Key_Minus
        args = (text, minus_icon, tip, parent.enr_sub, shortcut)
        self.decrease_enr_action = self.__create_action(*args)
        edit_menu.addAction(self.decrease_enr_action)
        self.menu_actions.append(self.decrease_enr_action)

        edit_menu.addSeparator()

        layers_icon = "layers-icon_32x32"
        text = "Segments..."
        tip = "Edit segment heights..."
        args = (text, layers_icon, tip, parent.open_segment_dlg)
        segment_action = self.__create_action(*args)
        edit_menu.addAction(segment_action)
        self.menu_actions.append(segment_action)

        icon = "table-icon_32x32"
        text = "Enrichments..."
        tip = "Edit enrichment levels..."
        args = (text, icon, tip, parent.open_enrichment_dlg)
        enrichment_action = self.__create_action(*args)
        edit_menu.addAction(enrichment_action)
        self.menu_actions.append(enrichment_action)

        icon = "flame-red-icon_32x32"
        text = "Quick calc..."
        tip = "Quick calculation settings..."
        args = (text, icon, tip, parent.open_pert_dlg)
        quickcalc_action = self.__create_action(*args)
        edit_menu.addAction(quickcalc_action)
        self.menu_actions.append(quickcalc_action)

        edit_menu.addSeparator()

        icon = "original-icon_32x32"
        text = "Replace original..."
        tip = "Replace original design..."
        args = (text, icon, tip, parent.replace_original_design)
        replace_action = self.__create_action(*args)
        edit_menu.addAction(replace_action)
        self.menu_actions.append(replace_action)

        icon = "undo-icon_32x32"
        text = "Reset..."
        tip = "Reset all changes..."
        args = (text, icon, tip, parent.reset_state)
        reset_action = self.__create_action(*args)
        edit_menu.addAction(reset_action)
        self.menu_actions.append(reset_action)

        icon = "preferences-icon_32x32"
        text = "Preferences..."
        tip = text
        args = (text, icon, tip)
        self.preferences_action = self.__create_action(*args)
        edit_menu.addAction(self.preferences_action)

        # --- Tools menu ---
        tools_menu = menubar.addMenu("&Tools")

        icon = "diagram-icon_32x32"
        text = "Plot..."
        tip = text
        args = (text, icon, tip, parent.open_plotwin)
        self.plot_action = self.__create_action(*args)
        tools_menu.addAction(self.plot_action)
        self.menu_actions.append(self.plot_action)
        
        icon = "grid-icon_32x32"
        text = "CASMO..."
        tip = text
        args = (text, icon, tip, parent.open_cas_dlg)
        casmo_action = self.__create_action(*args)
        tools_menu.addAction(casmo_action)
        self.menu_actions.append(casmo_action)

        icon = "write-icon_32x32"
        text = "Generate inp files"
        tip = "Generate CASMO input files..."
        args = (text, icon, tip, parent.generate_inpfiles)
        casinp_action = self.__create_action(*args)
        tools_menu.addAction(casinp_action)
        self.menu_actions.append(casinp_action)

        icon = "document-icon_32x32"
        text = "Report..."
        tip = "Fuel report..."
        args = (text, icon, tip, parent.open_report_dlg)
        report_action = self.__create_action(*args)
        tools_menu.addAction(report_action)
        self.menu_actions.append(report_action)

        icon = "binoculars-icon_32x32"
        text = "Find point..."
        tip = "Find state point..."
        args = (text, icon, tip, parent.open_findpoint_dlg)
        self.find_action = self.__create_action(*args)
        tools_menu.addAction(self.find_action)
        self.menu_actions.append(self.find_action)

        icon = "letter-e-icon_32x32"
        text = "EGV..."
        tip = text
        args = (text, icon, tip, parent.open_egv_dlg)
        egv_action = self.__create_action(*args)
        tools_menu.addAction(egv_action)
        self.menu_actions.append(egv_action)

        icon = None
        text = "Show color map"
        tip = "Show background color map"
        checkable = True
        args = (text, icon, tip, parent.toggle_pin_bgcolors, None, checkable)
        parent.show_cmap = self.__create_action(*args)
        tools_menu.addAction(parent.show_cmap)
        self.menu_actions.append(parent.show_cmap)

        icon = None
        text = "Track max pins"
        tip = "Mark pins with highest value"
        checkable = True
        args = (text, icon, tip, parent.toggle_maxpins, None, checkable)
        parent.track_maxpin = self.__create_action(*args)
        tools_menu.addAction(parent.track_maxpin)
        self.menu_actions.append(parent.track_maxpin)

        # -- Run menu ---
        run_menu = menubar.addMenu("&Run")

        icon = "flame-red-icon_32x32"
        text = "&Quick calc"
        tip = "Run quick calc"
        shortcut = "F9"
        args = (text, icon, tip, parent.quick_calc, shortcut)
        self.quickcalc_action = self.__create_action(*args)
        self.quickcalc_action.setEnabled(False)
        run_menu.addAction(self.quickcalc_action)

        # --- Help menu ---
        help_menu = menubar.addMenu("&Help")

        icon = "help-about-icon_32x32"
        text = "&About"
        tip = "About"
        args = (text, icon, tip, parent.on_about)
        about_action = self.__create_action(*args)
        help_menu.addAction(about_action)
        
        self.parent.setMenuBar(menubar)

    def create_toolbar(self):

        toolbar = QtGui.QToolBar()
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.file_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.quickcalc_action)              
        toolbar.addAction(self.preferences_action)

        color_icon = "color-icon_32x32"
        text = "Show color map"
        args = (text, color_icon, text, self.parent.toggle_cmap, False, True)
        self.parent.colorAction = self.__create_action(*args)
        self.menu_actions.append(self.parent.colorAction)
        toolbar.addAction(self.parent.colorAction)

        toolbar.addAction(self.plot_action)
        toolbar.addAction(self.find_action)
        toolbar.addAction(self.back_action)
        toolbar.addAction(self.forward_action)
        toolbar.addAction(self.decrease_enr_action)
        toolbar.addAction(self.increase_enr_action)
        toolbar.addAction(self.quit_action)
        
        toolbar.setMovable(False)
        toolbar.setFloatable(True)
        toolbar.setAutoFillBackground(False)

        self.parent.addToolBar(toolbar)
        
    def __create_action(self, text, icon=None, tip=None, slot=None,
                        shortcut=None, checkable=False):
        
        action = QtGui.QAction(text, self.parent)
        if icon is not None:
            action.setIcon(QtGui.QIcon(
                    self.parent.appdir + "icons/%s.png" % icon))
            action.setIconVisibleInMenu(True)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)

        return action


    def create_main_frame(self):
        parent = self.parent

        main_frame = QtGui.QWidget()

        # Create the mpl Figure and FigCanvas objects.
        r = 1.0  # resolution factor
        self.dpi = 100 * r
        self.fig = Figure((6 / r, 5 / r), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('button_press_event', parent.on_click)
        self.canvas.setParent(main_frame)
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

        self.__axes_setup()

        # Other GUI controls
        sim_hbox = QtGui.QHBoxLayout()
        self.sim_info_field = InfoLabel(width=210)
        sim_hbox.addWidget(self.sim_info_field)

        param_label = QtGui.QLabel('Parameter:')
        self.param_cbox = QtGui.QComboBox()
        paramlist = ['ENR', 'FINT', 'EXP', 'BTF']
        self.param_cbox.addItems(QtCore.QStringList(paramlist))
        
        param_hbox = QtGui.QHBoxLayout()
        param_hbox.addWidget(param_label)
        param_hbox.addWidget(self.param_cbox)
        parent.connect(self.param_cbox,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     parent.set_pinvalues)

        case_label = QtGui.QLabel('Segment:')
        self.case_cbox = QtGui.QComboBox()
        case_hbox = QtGui.QHBoxLayout()
        case_hbox.addWidget(case_label)
        case_hbox.addWidget(self.case_cbox)
        parent.connect(self.case_cbox, 
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     parent.fig_update)

        point_label = QtGui.QLabel('Point number:')
        self.point_sbox = QtGui.QSpinBox()
        self.point_sbox.setMinimum(0)
        self.point_sbox.setMaximum(10000)
        point_hbox = QtGui.QHBoxLayout()
        point_hbox.addWidget(point_label)
        point_hbox.addWidget(self.point_sbox)
        parent.connect(self.point_sbox, QtCore.SIGNAL('valueChanged(int)'),
                     parent.set_pinvalues)

        chanbow_hbox = QtGui.QHBoxLayout()
        self.chanbow_sbox = QtGui.QDoubleSpinBox()
        self.chanbow_sbox.setRange(-3, 3)
        self.chanbow_sbox.setSingleStep(0.25)
        self.chanbow_sbox.setSuffix(" mm")
        chanbow_hbox.addWidget(QtGui.QLabel("Channel bow:"))
        chanbow_hbox.addWidget(self.chanbow_sbox)

        # Info form layout
        info_flo = QtGui.QFormLayout()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Minimum)

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
        info_flo.addRow("VOI / VHI", self.voi_vhi_text)

        self.tfu_tmo_text = InfoLabel()
        self.tfu_tmo_text.setSizePolicy(sizePolicy)
        info_flo.addRow("TFU / TMO", self.tfu_tmo_text)

        self.rod_types_text = InfoLabel()
        self.rod_types_text.setSizePolicy(sizePolicy)
        info_flo.addRow("Rod types", self.rod_types_text)

        self.ave_enr_text = InfoLabel()
        self.ave_enr_text.setSizePolicy(sizePolicy)
        info_flo.addRow("Segment w/o U-235", self.ave_enr_text)

        self.bundle_enr_text = InfoLabel()
        self.bundle_enr_text.setSizePolicy(sizePolicy)
        info_flo.addRow("Bundle w/o U-235", self.bundle_enr_text)

        # Construct table widget instance
        self.table = PinTableWidget(parent)
        
        tvbox = QtGui.QVBoxLayout()
        tvbox.addWidget(self.table)
        tableGbox = QtGui.QGroupBox()
        tableGbox.setStyleSheet("QGroupBox { background-color: rgb(200, 200,\
        200); border:1px solid gray; border-radius:5px;}")
        tableGbox.setLayout(tvbox)
        self.table.resizeColumnsToContents()

        # Layout with box sizers
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(sim_hbox)
        vbox.addLayout(case_hbox)
        vbox.addLayout(param_hbox)
        vbox.addLayout(chanbow_hbox)
        vbox.addStretch(1)
        vbox.addLayout(point_hbox)
        vbox.addLayout(info_flo)

        groupbox = QtGui.QGroupBox()
        groupbox.setStyleSheet("QGroupBox { background-color: rgb(200, 200,\
        200); border:1px solid gray; border-radius:5px;}")
        groupbox.setLayout(vbox)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(groupbox)
        hbox.addWidget(canvasGbox)
        hbox.addWidget(tableGbox)

        main_frame.setLayout(hbox)
        parent.setCentralWidget(main_frame)

    def __axes_setup(self):
        """Setup the figure axes"""
        
        self.axes = self.fig.add_subplot(111)

        # clear the axes and redraw the plot
        self.axes.clear()
        self.axes.axis('equal')
        
        self.axes.set_position([0, 0, 1, 1])
        self.axes.set_frame_on(False)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

    def on_resize(self, event):
        self.axes.set_xlim(0, 1.2)
        self.axes.set_ylim(0, 1)
