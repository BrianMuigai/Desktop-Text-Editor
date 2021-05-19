import sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

def main():
    app = QApplication(sys.argv)
    import config
    config.m.show()
    config.m.raise_()
    app.exec_()

if __name__ == '__main__':
    main()
