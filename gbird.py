#!/usr/bin/python

import sys
from PyQt4 import QtGui

from mainwin import MainWin


def main():  # initiate main window
    app = QtGui.QApplication(sys.argv)
    if len(sys.argv) > 1:  # check for input argument
        window = MainWin(sys.argv[1])
    else:
        window = MainWin()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
