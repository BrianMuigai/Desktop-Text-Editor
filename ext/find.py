# Adapted from Peter Goldsborough at
# https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-3/147
import sys, os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re, config
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.Qsci import *
from PyQt5.QtWidgets import *

class Find(QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        # Initialize varaibles
        self.re = False
        self.cs = None
        self.wo = None

        # Case Sensitivity option
        self.caseSens = QCheckBox("Case sensitive",self)
        if self.caseSens.isChecked():
            self.cs = True
        else:
            self.cs = False

        # Whole Words option
        self.wholeWords = QCheckBox("Whole words",self)
        if self.wholeWords.isChecked():
            self.wo = True
        else:
            self.wo = False

        # Button to search the document for something
        findButton = QPushButton("Find",self)
        findButton.clicked.connect(self.find)

        # Button to replace the last finding
        replaceButton = QPushButton("Replace",self)
        replaceButton.clicked.connect(self.replace)

        # Button to remove all findings
        allButton = QPushButton("Replace all",self)
        allButton.clicked.connect(self.replaceAll)

        # The field into which to type the query
        self.findField = QTextEdit(self)
        self.findField.resize(250,50)

         # Normal mode - radio button
        self.normalRadio = QRadioButton("Normal",self)
        self.normalRadio.toggled.connect(self.normalMode)
        # Normal mode is default setting
        self.normalRadio.setChecked(True)

        # Regular Expression Mode - radio button
        self.regexRadio = QRadioButton("RegEx",self)
        self.regexRadio.toggled.connect(self.regexMode)

        # The field into which to type the text to replace the
        # queried text
        self.replaceField = QTextEdit(self)
        self.replaceField.resize(250,50)

        optionsLabel = QLabel("Options: ",self)

        # Layout the objects on the screen
        layout = QGridLayout()

        layout.addWidget(self.findField,1,0,1,4)
        layout.addWidget(self.normalRadio,2,2)
        layout.addWidget(self.regexRadio,2,3)
        layout.addWidget(findButton,2,0,1,2)
        layout.addWidget(self.replaceField,3,0,1,4)
        layout.addWidget(replaceButton,4,0,1,2)
        layout.addWidget(allButton,4,2,1,2)

        # Add some spacing
        spacer = QWidget(self)

        spacer.setFixedSize(0,10)

        layout.addWidget(spacer,5,0)

        layout.addWidget(optionsLabel,6,0)
        layout.addWidget(self.caseSens,6,1)
        layout.addWidget(self.wholeWords,6,2)

        self.setGeometry(300,300,360,250)
        self.setWindowTitle("Find and Replace")
        self.setLayout(layout)

    def getCurrentEditor(self):
        return self.parent.getEditor(self.parent.tab.currentIndex()+1)

    def regexMode(self):
        # Uncheck and then disable case sensitive/whole words in regex mode
        self.caseSens.setChecked(False)
        self.wholeWords.setChecked(False)

        self.caseSens.setEnabled(False)
        self.wholeWords.setEnabled(False)

        self.re = True

    def normalMode(self):
        # Enable case sensitive/whole words
        self.caseSens.setEnabled(True)
        self.wholeWords.setEnabled(True)

        self.re = False

    def find(self):
        # Get the text to find
        self.expr = self.findField.toPlainText()
        # Use QScintilla's built in find method for this
        self.getCurrentEditor().findFirst(self.expr, self.re, self.cs, self.wo, True)

    def replace(self):
        self.replaceStr = self.replaceField.toPlainText()
        self.find()
        self.getCurrentEditor().replace(self.replaceStr)

    def replaceAll(self):
        self.replaceStr = self.replaceField.toPlainText()
        self.find()
        while self.getCurrentEditor().findNext():
            self.getCurrentEditor().findNext()
            self.getCurrentEditor().replace(self.replaceStr)
