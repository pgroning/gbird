#!/usr/bin/python
#
################################################################
#                                                              #
# Program: Greenbird                                           #
#                                                              #
# Description: A graphical tool to optimize the enrichment and #
# BA design of BWR-fuel.                                       #
#                                                              #
#                                                              #
################################################################

import sys
from PyQt4 import QtGui

from mainwin import MainWin


def main():  # initiate main window
    appversion = "1.0.0T"
    app = QtGui.QApplication(sys.argv)
    if len(sys.argv) > 1:  # check for input argument
        window = MainWin(appversion, sys.argv[1])
    else:
        window = MainWin(appversion)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
