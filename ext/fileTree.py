import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Tree(QWidget):
    """ File tree widget for Codex"""
    def __init__(self, parent = None):
        super(Tree, self).__init__(parent)
        # if len(config.docList) == 0:
        #     config.docList.append(config.getWorkingDir())
        # print('File Tree:--> doc list: ', config.docList)
        self.initUI()

    def initUI(self):
        self.fsModel = QFileSystemModel()
        self.sModel = QItemSelectionModel(self.fsModel)
        # If the user entered a project directory, use that.
        # If not, go two levels up from the current file
        if config.proDir != "":
            self.fsIndex = self.fsModel.setRootPath(config.proDir)
        else:
            try:
                self.fsIndex = self.fsModel.setRootPath(os.path.dirname(os.path.dirname(config.docList[config.m.tab.currentIndex()])))
            except:
                self.fsIndex = self.fsModel.setRootPath(os.path.dirname(os.path.dirname(config.getWorkingDir())))
        self.treeView = QTreeView(self)
        self.treeView.setModel(self.fsModel)
        self.treeView.setSelectionModel(self.sModel)
        self.treeView.setDragEnabled(True)
        self.treeView.setDragDropMode(QAbstractItemView.InternalMove)
        self.treeView.setRootIndex(self.fsIndex)
        self.treeView.setAnimated(True)
        self.treeView.setHeaderHidden(True)
        self.treeView.hideColumn(1)
        self.treeView.hideColumn(2)
        self.treeView.hideColumn(3)
        self.treeView.resize(250,620) #TODO: abstract this
        self.treeView.clicked.connect(self.clicked)

    def clicked(self):
        config.m.file = self.fsModel.filePath(self.sModel.selectedIndexes()[0])
        try:
            if str(config.m.file) in config.docList:
                return
            config.docList.apppend(str(config.m.file))
            config.m.open()
        except AttributeError:
            if str(config.m.file) in config.docList:
                return
            config.docList.append(str(config.m.file))
            try:
                config.m.open()
            except:
                config.docList.remove(str(config.m.file))
        # print(config.docList)
