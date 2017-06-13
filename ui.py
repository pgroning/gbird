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

        parent.file_menu = parent.menuBar().addMenu("&File")

        new_icon = "new-icon_32x32"
        text = "&New..."
        tip = "Create new bundle"
        args = (text, new_icon, tip, parent.open_bundle_dlg)
        new_action = self.__create_action(*args)
        parent.menu_actions.append(new_action)

        file_icon = "open-file-icon_32x32"
        text = "&Open..."
        tip = "Open file"
        args = (text, file_icon, tip, parent.openFile)
        file_action = self.__create_action(*args)
        parent.menu_actions.append(file_action)

        save_icon = "save-icon_32x32"
        text = "&Save project..."
        tip = "Save data to file"
        args = (text, save_icon, tip, parent.saveData)
        save_action = self.__create_action(*args)
        parent.menu_actions.append(save_action)

        for action in parent.menu_actions:
            parent.file_menu.addAction(action)

    def create_toolbar(self):
        parent = self.parent
        parent.toolbar_actions = []

        new_icon = "new-icon_32x32"
        text = "Create new bundle"
        args = (text, new_icon, text, parent.open_bundle_dlg)
        new_action = self.__create_action(*args)
        parent.toolbar_actions.append(new_action)

        file_icon = "open-file-icon_32x32"
        text = "Open file"
        args = (text, file_icon, text, parent.openFile)
        file_action = self.__create_action(*args)
        parent.toolbar_actions.append(file_action)

        save_icon = "save-icon_32x32"
        text = "Save to file"
        args = (text, save_icon, text, parent.saveData)
        save_action = self.__create_action(*args)
        parent.toolbar_actions.append(save_action)

        calc_icon = "flame-red-icon_32x32"
        text = "Run quick calc"
        args = (text, calc_icon, text, parent.quick_calc)
        parent.calcAction = self.__create_action(*args)
        parent.toolbar_actions.append(parent.calcAction)
                                                         
        pref_icon = "preferences-icon_32x32"
        text = "Settings"
        args = (text, pref_icon, text)
        pref_action = self.__create_action(*args)
        parent.toolbar_actions.append(pref_action)

        color_icon = "color-icon_32x32"
        text = "Show color map"
        args = (text, color_icon, text, parent.toggle_cmap, True)
        parent.colorAction = self.__create_action(*args)
        parent.toolbar_actions.append(parent.colorAction)

        plot_icon = "diagram-icon_32x32"
        text = "Plot"
        tip = "Open plot window"
        args = (text, plot_icon, tip, parent.open_plotwin)
        plot_action = self.__create_action(*args)
        parent.toolbar_actions.append(plot_action)

        find_icon = "binoculars-icon_32x32"
        text = "Find state point"
        args = (text, find_icon, text, parent.open_findpoint_dlg)
        find_action = self.__create_action(*args)
        parent.toolbar_actions.append(find_action)

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

        toolbar = parent.addToolBar("Toolbar")
        for action in parent.toolbar_actions:
            toolbar.addAction(action)
        
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
            action.setShortCut(shortcut)
        if checkable:
            action.setCheckable(True)

        return action
