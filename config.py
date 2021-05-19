"""
File that contains global variables
"""
import sys, os
from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from lexers.TextLexer import QsciLexerText

LEXERS = {
        'PHP': QsciLexerHTML(),
        'Python': QsciLexerPython(),
    }

docList = []
if sys.platform.startswith("linux"):
    font = QFont("DejaVu Sans Mono", 10, 50)
elif sys.platform.startswith("darwin"):
    font = QFont("Menlo", 10, 50)
elif sys.platform.startswith("win"):
    font = QFont("Courier New", 10, 50)
lexer = QsciLexerText()
proDir = ""

def getWorkingDir():
    return os.getcwd()

from window import mainWindow
m = mainWindow()
