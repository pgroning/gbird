from PyQt4 import QtGui, QtCore


class Ui_MainWindow(object):
    """Creates ui widgets and menus in main frame"""

    def __init__(self, parent=None):
        #super(Ui, self).__init__(parent)
        #self.parent = parent
        pass

    def setup(self, parent):
        self.parent = parent
        self.create_statusbar()
        self.create_menu()
        self.create_toolbar()

    def create_statusbar(self):
        status_text = QtGui.QLabel("Main window")
        self.parent.statusBar().addWidget(status_text, 1)

    def create_menu(self):
        parent = self.parent

        parent.menu_actions = []

        # --- File menu ---
        parent.file_menu = parent.menuBar().addMenu("&File")

        new_icon = "new-icon_32x32"
        text = "&New..."
        tip = "Create new bundle"
        args = (text, new_icon, tip, parent.open_bundle_dlg)
        self.new_action = self.__create_action(*args)
        parent.file_menu.addAction(self.new_action)
        #parent.menu_actions.append(new_action)

        file_icon = "open-file-icon_32x32"
        text = "&Open..."
        tip = "Open file"
        args = (text, file_icon, tip, parent.openFile)
        self.file_action = self.__create_action(*args)
        parent.file_menu.addAction(self.file_action)
        #parent.menu_actions.append(file_action)

        save_icon = "save-icon_32x32"
        text = "&Save project..."
        tip = "Save data to file"
        args = (text, save_icon, tip, parent.saveData)
        self.save_action = self.__create_action(*args)
        parent.file_menu.addAction(self.save_action)
        parent.menu_actions.append(self.save_action)

        delete_icon = "delete-icon_32x32"
        text = "&Clear project..."
        tip = "Clear current project"
        args = (text, delete_icon, tip, parent.clear_project)
        clear_action = self.__create_action(*args)
        parent.file_menu.addAction(clear_action)
        parent.menu_actions.append(clear_action)

        export_icon = "export-icon_32x32"
        text = "&Export to ascii..."
        tip = "Export data to file"
        args = (text, export_icon, tip, parent.export_to_ascii)
        save_file_action = self.__create_action(*args)
        parent.file_menu.addAction(save_file_action)
        parent.menu_actions.append(save_file_action)

        export_icon = "export-icon_32x32"
        text = "&Export Figure..."
        tip = "Export fuel map to file"
        args = (text, export_icon, tip, parent.saveFigure)
        save_figure_action = self.__create_action(*args)
        parent.file_menu.addAction(save_figure_action)
        parent.menu_actions.append(save_figure_action)

        parent.file_menu.addSeparator()

        quit_icon = "exit-icon_32x32"
        text = "&Quit"
        tip = "Exit application"
        shortcut = "Ctrl+Q"
        args = (text, quit_icon, tip, parent.close, False, shortcut)
        self.quit_action = self.__create_action(*args)
        parent.file_menu.addAction(self.quit_action)
        #parent.menu_actions.append(quit_action)

        #for action in parent.menu_actions:
        #    if action is None:
        #        parent.file_menu.addSeparator()
        #    else:
        #        parent.file_menu.addAction(action)

        # --- Edit menu ---
        parent.edit_menu = parent.menuBar().addMenu("&Edit")

        back_icon = "arrow-undo-icon_32x32"
        text = "Back"
        tip = "Back to previous"
        args = (text, back_icon, tip, parent.back_state)
        back_action = self.__create_action(*args)
        parent.edit_menu.addAction(back_action)
        parent.menu_actions.append(back_action)

        forward_icon = "arrow-redo-icon_32x32"
        text = "Forward"
        tip = "Forward to next"
        args = (text, forward_icon, tip, parent.forward_state)
        forward_action = self.__create_action(*args)
        parent.edit_menu.addAction(forward_action)
        parent.menu_actions.append(forward_action)

        parent.edit_menu.addSeparator()

        plus_icon = "add-icon_32x32"
        text = "Increase enr"
        tip = "Increase enrichment"
        shortcut = QtCore.Qt.Key_Plus
        args = (text, plus_icon, tip, parent.enr_add, False, shortcut)
        increase_enr_action = self.__create_action(*args)
        parent.edit_menu.addAction(increase_enr_action)
        parent.menu_actions.append(increase_enr_action)
        
        minus_icon = "remove-icon_32x32"
        text = "Decrease enr"
        tip = "Decrease enrichment"
        shortcut = QtCore.Qt.Key_Minus
        args = (text, minus_icon, tip, parent.enr_sub, False, shortcut)
        decrease_enr_action = self.__create_action(*args)
        parent.edit_menu.addAction(decrease_enr_action)
        parent.menu_actions.append(decrease_enr_action)

        parent.edit_menu.addSeparator()

        layers_icon = "layers-icon_32x32"
        text = "Segments..."
        tip = "Edit segment heights..."
        args = (text, layers_icon, tip, parent.open_segment_dlg)
        segment_action = self.__create_action(*args)
        parent.edit_menu.addAction(segment_action)
        parent.menu_actions.append(segment_action)

        icon = "table-icon_32x32"
        text = "Enrichments..."
        tip = "Edit enrichment levels..."
        args = (text, icon, tip, parent.open_enrichment_dlg)
        segment_action = self.__create_action(*args)
        parent.edit_menu.addAction(segment_action)
        parent.menu_actions.append(segment_action)

        icon = "flame-red-icon_32x32"
        text = "Quick calc..."
        tip = "Quick calculation settings..."
        args = (text, icon, tip, parent.open_pert_dlg)
        quickcalc_action = self.__create_action(*args)
        parent.edit_menu.addAction(quickcalc_action)
        parent.menu_actions.append(quickcalc_action)

        parent.edit_menu.addSeparator()

        icon = "original-icon_32x32"
        text = "Replace original..."
        tip = "Replace original design..."
        args = (text, icon, tip, parent.replace_original_design)
        replace_action = self.__create_action(*args)
        parent.edit_menu.addAction(replace_action)
        parent.menu_actions.append(replace_action)

        icon = "undo-icon_32x32"
        text = "Reset..."
        tip = "Reset all changes..."
        args = (text, icon, tip, parent.reset_state)
        reset_action = self.__create_action(*args)
        parent.edit_menu.addAction(reset_action)
        parent.menu_actions.append(reset_action)

        icon = "preferences-icon_32x32"
        text = "Preferences..."
        tip = text
        args = (text, icon, tip)
        self.preferences_action = self.__create_action(*args)
        parent.edit_menu.addAction(self.preferences_action)
        #parent.menu_actions.append(self.preferences_action)

        # --- Tools menu ---
        parent.tools_menu = parent.menuBar().addMenu("&Tools")

        icon = "diagram-icon_32x32"
        text = "Plot..."
        tip = text
        args = (text, icon, tip, parent.open_plotwin)
        self.plot_action = self.__create_action(*args)
        parent.tools_menu.addAction(self.plot_action)
        parent.menu_actions.append(self.plot_action)
        
        icon = "grid-icon_32x32"
        text = "CASMO..."
        tip = text
        args = (text, icon, tip, parent.open_cas_dlg)
        casmo_action = self.__create_action(*args)
        parent.tools_menu.addAction(casmo_action)
        parent.menu_actions.append(casmo_action)

        icon = "write-icon_32x32"
        text = "Generate inp files"
        tip = "Generate CASMO input files..."
        args = (text, icon, tip, parent.generate_inpfiles)
        casinp_action = self.__create_action(*args)
        parent.tools_menu.addAction(casinp_action)
        parent.menu_actions.append(casinp_action)

        icon = "document-icon_32x32"
        text = "Report..."
        tip = "Fuel report..."
        args = (text, icon, tip, parent.open_report_dlg)
        report_action = self.__create_action(*args)
        parent.tools_menu.addAction(report_action)
        parent.menu_actions.append(report_action)

        icon = "binoculars-icon_32x32"
        text = "Find point..."
        tip = "Find state point..."
        args = (text, icon, tip, parent.open_findpoint_dlg)
        self.find_action = self.__create_action(*args)
        parent.tools_menu.addAction(self.find_action)
        parent.menu_actions.append(self.find_action)

        icon = "letter-e-icon_32x32"
        text = "EGV..."
        tip = text
        args = (text, icon, tip, parent.open_egv_dlg)
        egv_action = self.__create_action(*args)
        parent.tools_menu.addAction(egv_action)
        parent.menu_actions.append(egv_action)

        icon = None
        text = "Show color map"
        tip = "Show background color map"
        checkable = True
        args = (text, icon, tip, parent.toggle_pin_bgcolors, checkable)
        parent.show_cmap = self.__create_action(*args)
        parent.tools_menu.addAction(parent.show_cmap)
        parent.menu_actions.append(parent.show_cmap)

        icon = None
        text = "Track max pins"
        tip = "Mark pins with highest value"
        checkable = True
        args = (text, icon, tip, parent.toggle_maxpins, checkable)
        parent.track_maxpin = self.__create_action(*args)
        parent.tools_menu.addAction(parent.track_maxpin)
        parent.menu_actions.append(parent.track_maxpin)

        # -- Run menu ---
        parent.run_menu = parent.menuBar().addMenu("&Run")

        icon = "flame-red-icon_32x32"
        text = "&Quick calc"
        tip = "Run quick calc"
        shortcut = "F9"
        args = (text, icon, tip, parent.quick_calc, False, shortcut)
        parent.quickcalc_action = self.__create_action(*args)
        parent.run_menu.addAction(parent.quickcalc_action)
        parent.menu_actions.append(parent.quickcalc_action)

        # --- Help menu ---
        parent.help_menu = parent.menuBar().addMenu("&Help")

        icon = "help-about-icon_32x32"
        text = "&About"
        tip = "About"
        args = (text, icon, tip, parent.on_about)
        about_action = self.__create_action(*args)
        parent.help_menu.addAction(about_action)
        parent.menu_actions.append(about_action)
        

    def create_toolbar(self):
        parent = self.parent
        parent.toolbar_actions = []

        toolbar = parent.addToolBar("Toolbar")

        #new_icon = "new-icon_32x32"
        #text = "Create new bundle"
        #args = (text, new_icon, text, parent.open_bundle_dlg)
        #new_action = self.__create_action(*args)
        #parent.toolbar_actions.append(self.new_action)
        toolbar.addAction(self.new_action)

        #file_icon = "open-file-icon_32x32"
        #text = "Open file"
        #args = (text, file_icon, text, parent.openFile)
        #file_action = self.__create_action(*args)
        #parent.toolbar_actions.append(file_action)
        toolbar.addAction(self.file_action)

        #save_icon = "save-icon_32x32"
        #text = "Save to file"
        #args = (text, save_icon, text, parent.saveData)
        #save_action = self.__create_action(*args)
        #parent.toolbar_actions.append(save_action)
        toolbar.addAction(self.save_action)

        #calc_icon = "flame-red-icon_32x32"
        #text = "Run quick calc"
        #args = (text, calc_icon, text, parent.quick_calc)
        #parent.calcAction = self.__create_action(*args)
        #parent.toolbar_actions.append(parent.calcAction)
        toolbar.addAction(parent.quickcalc_action)
                                                         
        #pref_icon = "preferences-icon_32x32"
        #text = "Settings"
        #args = (text, pref_icon, text)
        #pref_action = self.__create_action(*args)
        #parent.toolbar_actions.append(pref_action)
        toolbar.addAction(self.preferences_action)

        color_icon = "color-icon_32x32"
        text = "Show color map"
        args = (text, color_icon, text, parent.toggle_cmap, True)
        parent.colorAction = self.__create_action(*args)
        parent.toolbar_actions.append(parent.colorAction)
        toolbar.addAction(parent.colorAction)

        #plot_icon = "diagram-icon_32x32"
        #text = "Plot"
        #tip = "Open plot window"
        #args = (text, plot_icon, tip, parent.open_plotwin)
        #plot_action = self.__create_action(*args)
        #parent.toolbar_actions.append(plot_action)
        toolbar.addAction(self.plot_action)

        #find_icon = "binoculars-icon_32x32"
        #text = "Find state point"
        #args = (text, find_icon, text, parent.open_findpoint_dlg)
        #find_action = self.__create_action(*args)
        #parent.toolbar_actions.append(find_action)
        toolbar.addAction(self.find_action)

        arrow_undo_icon = "arrow-undo-icon_32x32"
        text = "Back to previous design"
        args = (text, arrow_undo_icon, text, parent.back_state)
        back_action = self.__create_action(*args)
        parent.toolbar_actions.append(back_action)
        

        arrow_redo_icon = "arrow-redo-icon_32x32"
        text = "Forward to next design"
        args = (text, arrow_redo_icon, text, parent.forward_state)
        forward_action = self.__create_action(*args)
        parent.toolbar_actions.append(forward_action)

        minus_icon = "remove-icon_32x32"
        text = "Decrease enrichment"
        tip = text
        args = (text, minus_icon, tip, parent.enr_sub)
        decrease_enr_action = self.__create_action(*args)
        parent.toolbar_actions.append(decrease_enr_action)

        plus_icon = "add-icon_32x32"
        text = "Increase enrichment"
        tip = text
        args = (text, plus_icon, tip, parent.enr_add)
        increase_enr_action = self.__create_action(*args)
        parent.toolbar_actions.append(increase_enr_action)

        exit_icon = "exit-icon_32x32"
        text = "Exit"
        tip = "Exit application"
        args = (text, exit_icon, tip, parent.close)
        exit_action = self.__create_action(*args)
        parent.toolbar_actions.append(exit_action)
        #parent.toolbar_actions.append(self.quit_action)

        #toolbar = parent.addToolBar("Toolbar")
        #for action in parent.toolbar_actions:
        #    toolbar.addAction(action)
        
        toolbar.setMovable(False)
        toolbar.setFloatable(True)
        toolbar.setAutoFillBackground(False)
        
        #parent.toolbar_actions = [save_action, parent.colorAction]
        
    def __create_action(self, text, icon=None, tip=None, slot=None,
                                checkable=False, shortcut=None):
        
        action = QtGui.QAction(text, self.parent)
        if icon is not None:
            #action.setIcon(QtGui.QIcon(icon))
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
