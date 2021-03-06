import sys, os, pickle, gzip, subprocess, config

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.Qsci import *

from ext.terminal import Terminal
from ext.find import Find
from ext.fileTree import Tree

from lexers.TextLexer import QsciLexerText
from editor import Editor

class mainWindow(QMainWindow):
    """Class for the main window that contains the tabs, editor, terminal, etc."""

    def __init__(self, parent = None):
        super(mainWindow, self).__init__(parent)
        config.filename = "Untitled"
        self.tabNum = 0
        self.treeVis = True
        self.termVis = False
        config.docList = []
        self.edit = Editor()
        self.editDict = {"edit1":self.edit}
        self.tab = QTabWidget(self)

        self.initUI()

    def writeSettings(self):
        settings = QSettings()
        font = settings.setValue("Editor/font", QVariant(config.font.toString()))
        term = settings.setValue("mainWindow/term", QVariant(self.termVis))
        tree = settings.setValue("mainWindow/tree", QVariant(self.treeVis))
        pDir = settings.setValue("fileTree/proDir", QVariant(config.proDir))

    def readSettings(self):
        # The default fonts represented as a toString() list
        DEFAULT_FONT = str(config.font.family())+",12,-1,5,50,0,0,0,0,0"
        settings = QSettings()
        if config.font.fromString(settings.value("Editor/font",
                                                QVariant(DEFAULT_FONT),type=str)):
            #config.lexer.setDefaultColor(QColor("Black"))
            config.lexer.setFont(config.font)
        self.termVis = settings.value("mainWindow/term", QVariant(False),type=bool)
        self.treeVis = settings.value("mainWindow/tree", QVariant(False),type=bool)
        config.proDir = settings.value("fileTree/proDir",type=str)

    def initActions(self):
        self.newAction = QAction("New Window",self)
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.triggered.connect(self.new)

        self.newTabAction = QAction("New File",self)
        self.newTabAction.setShortcut("Ctrl+T")
        self.newTabAction.triggered.connect(self.newTab)

        self.openAction = QAction("Open file",self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.openFile)

        self.saveAction = QAction("Save",self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.saveFile)

        self.saveasAction = QAction("Save As",self)
        self.saveasAction.setShortcut("Ctrl+Shift+S")
        self.saveasAction.triggered.connect(self.saveFileAs)

        self.cutAction = QAction("Cut",self)
        self.cutAction.setShortcut("Ctrl+X")
        self.cutAction.triggered.connect(lambda cut:
                                         self.getEditor(self.tab.currentIndex()).cut)

        self.copyAction = QAction("Copy",self)
        self.copyAction.setShortcut("Ctrl+C")
        self.copyAction.triggered.connect(lambda copy:
                                          self.getEditor(self.tab.currentIndex()).copy)

        self.pasteAction = QAction("Paste",self)
        self.pasteAction.setShortcut("Ctrl+V")
        self.pasteAction.triggered.connect(lambda paste:
                                           self.getEditor(self.tab.currentIndex()).paste)

        self.undoAction = QAction("Undo",self)
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(lambda undo:
                                          self.getEditor(self.tab.currentIndex()).undo)

        self.redoAction = QAction("Redo",self)
        self.redoAction.setShortcut("Ctrl+Y")
        self.redoAction.triggered.connect(lambda redo:
                                          self.getEditor(self.tab.currentIndex()).redo)

        self.aboutAction = QAction("About Desktop Text Editor",self)
        self.aboutAction.triggered.connect(self.about)

        self.noLexAct = QAction("Plain Text",self)
        self.noLexAct.triggered.connect(lambda noLex:
                                        self.getEditor(self.tab.currentIndex()).\
                                        setLexer(QsciLexerText()))

        self.termAct = QAction("Terminal",self)
        self.termAct.setCheckable(True)
        self.termAct.triggered.connect(self.toggleTerm)

        self.treeAct = QAction("File Tree",self)
        self.treeAct.setCheckable(True)
        self.treeAct.triggered.connect(self.toggleTree)

        self.toggleIntAct = QAction("Indentation Guides",self)
        self.toggleIntAct.triggered.connect(self.toggleIntGuide)
        self.toggleIntAct.setCheckable(True)
        self.toggleIntAct.setChecked(True)

        self.toggleLNAct = QAction("Line Numbers",self)
        self.toggleLNAct.triggered.connect(self.toggleLN)
        self.toggleLNAct.setCheckable(True)
        self.toggleLNAct.setChecked(True)

        self.FRAct = QAction("Find and Replace",self)
        self.FRAct.triggered.connect(self.fr)
        self.FRAct.setShortcut("Ctrl+F")

        self.fontAct = QAction("Choose Font",self)
        self.fontAct.triggered.connect(self.chooseFont)

        self.dirAct = QAction("Choose Project Directory",self)
        self.dirAct.triggered.connect(self.setProDir)

    def getEditor(self, index):
        if index == 0:
            return self.editDict.get("edit1")
        else:
            return self.editDict.get(("edit"+str(index)))

    def getCurrentFile(self):
        print('getCurrentFile: ', config.docList, ' config: ', self.tab.currentIndex())
        data = config.docList[self.tab.currentIndex()]
        if type(data) == tuple:
            return data[0] # returns tuple (?)
        else:
            return data

    def initMenubar(self):
        menubar = self.menuBar()

        file = menubar.addMenu("File")
        edit = menubar.addMenu("Edit")
        self.lang = menubar.addMenu("Languages")
        view = menubar.addMenu("View")
        about = menubar.addMenu("About")

        self.initLexers()

        file.addAction(self.newAction)
        file.addAction(self.newTabAction)
        file.addAction(self.openAction)
        file.addAction(self.saveAction)
        file.addAction(self.saveasAction)
        file.addSeparator()
        file.addAction(self.fontAct)
        file.addAction(self.dirAct)

        edit.addAction(self.undoAction)
        edit.addAction(self.redoAction)
        edit.addSeparator()
        edit.addAction(self.copyAction)
        edit.addAction(self.cutAction)
        edit.addAction(self.pasteAction)
        edit.addAction(self.FRAct)

        # view.addAction(self.termAct) #remove term temp
        view.addAction(self.toggleIntAct)
        view.addAction(self.toggleLNAct)
        view.addAction(self.treeAct)

        about.addAction(self.aboutAction)

    def lessTabs(self):
        self.tabNum = self.tabNum - 1
        try:
            #print config.docList
            config.docList.remove(config.docList[self.tab.currentIndex()-1])
        except:
            config.docList = []
            if self.tabNum < 1:
                self.newTab()
            else:
                self.tab.removeTab(self.tab.currentIndex()-1)
        
    def initTabs(self):
        # Set up the tabs
        self.tab.tabCloseRequested.connect(self.tab.removeTab)
        self.tab.tabCloseRequested.connect(self.lessTabs)
        self.tab.setMovable(True)
        # Needed for Mac
        self.tab.setDocumentMode(True)
        self.setUnifiedTitleAndToolBarOnMac(True)
        # Automatically make new tabs contain an editor widget
        self.tab.addTab(self.editDict.get("edit1"), config.filename)
        self.termSplit.addWidget(self.tab)
        self.tab.setTabsClosable(True)

    def initUI(self):
        # Create first qsplitter for sidebar
        self.treeSplit = QSplitter()
        self.treeSplit.setOrientation(Qt.Horizontal)
        # Create second qsplitter (Allows split screen for terminal)
        self.termSplit = QSplitter()
        self.termSplit.setOrientation(Qt.Vertical)
        # Add a termSplit to the treeSplit
        self.treeSplit.addWidget(self.termSplit)
        self.setCentralWidget(self.treeSplit)
        # Create everything else
        self.initTabs()
        self.initActions()
        self.initMenubar()
        # Create terminal widget 
        self.term = Terminal()
        #self.term.hide()
        # x and y coordinates on the screen, width, height
        self.setGeometry(100,100,800,630)
        self.setWindowTitle("Desktop Text Editor")
        # Move up to the parent directory and set the window icons.
        # Without os.path it will look for icons in src/
        self.setWindowIcon(QIcon(os.path.join(
        os.path.dirname(__file__)) + "/icons/256x256/logo.png"))
        # Open any documents that were open before closing and restore settings
        QTimer.singleShot(0,self.loadDocs)
        self.readSettings()
        # Show the terminal/tree if necessary.
        self.loadTermAndTree()
        # If there are no documents to load set the language as plain text
        # If there are documents to load guess lexers for them
        if len(config.docList) == 0:
            self.getEditor(self.tabNum).setLang(QsciLexerText())
            self.noLexAct.setChecked(True)
        else:
            self.guessLexer()
        # Set font
        self.getEditor(self.tab.currentIndex()).lexer.setFont(config.font)

    def initLexers(self):
        # Dict that maps lexer actions to their respective strings
        self.lexActs = {}
        langGrp = QActionGroup(self.lang)
        langGrp.setExclusive(True)
        self.lang.addAction(self.noLexAct)
        self.noLexAct.setCheckable(True)
        #self.noLexAct.setChecked(True)
        self.noLexAct.setActionGroup(langGrp)
        self.lang.addSeparator()
        languages = sorted(config.LEXERS.keys())
        for i in languages:
            langAct = self.lang.addAction(i)
            langAct.setCheckable(True)
            langAct.setActionGroup(langGrp)
            self.lexActs[langAct] = i
        langGrp.triggered.connect(lambda lex: self.getEditor(self.tabNum+1).setLang(self.lexActs.get(lex)))

    def guessLexer(self):
        try:
            x = config.docList[self.tab.currentIndex()+1]
            n, e = os.path.basename(x).lower().split(".")
            if e == "sh" or e == "bsh":
                self.getEditor(self.tabNum).setLang("Bash")
            elif e == "cmd" or e == "bat" or e == "btm" or e == "nt":
                self.getEditor(self.tabNum).setLang("Batch")
            elif e == "cmake" or e == "cmakelists":
                self.getEditor(self.tabNum).setLang("CMake")
            elif e == "cpp" or e == "cxx" or e == "cc" or e == "c" or e == "h"\
            or e == "hh" or e == "hpp":
                self.getEditor(self.tabNum).setLang("C++")
            elif e == "cs":
                self.getEditor(self.tabNum).setLang("C#")
            elif e == "css":
                self.getEditor(self.tabNum).setLang("CSS")
            elif e == "d":
                self.getEditor(self.tabNum).setLang("D")
            elif e == "diff" or e == "patch":
                self.getEditor(self.tabNum).setLang("Diff")
            elif e == "f90" or e == "f95" or e == "f2k" or e == "f03" or e == "f15":
                self.getEditor(self.tabNum).setLang("Fortran")
            elif e == "f" or e == "for":
                self.getEditor(self.tabNum).setLang("Fortran77")
            elif e == "html" or e == "htm":
                self.getEditor(self.tabNum).setLang("HTML")
            elif e == "java":
                self.getEditor(self.tabNum).setLang("Java")
            elif e == "js":
                self.getEditor(self.tabNum).setLang("JavaScript")
            elif e == "lua":
                self.getEditor(self.tabNum).setLang("Lua")
            elif e == "mak" or n == "gnumakefile" or n == "makefile":
                self.getEditor(self.tabNum).setLang("Makefile")
            elif e == "m":
                self.getEditor(self.tabNum).setLang("MATLAB")
            elif e == "pas" or e == "inc":
                self.getEditor(self.tabNum).setLang("Pascal")
            elif e == "ps":
                self.getEditor(self.tabNum).setLang("PostScript")
            elif e == "pov" or e == "tga":
                self.getEditor(self.tabNum).setLang("POV-Ray")
            elif e == "py" or e == "pyw":
                self.getEditor(self.tabNum).setLang("Python")
                #print "p"
            elif e == "rb" or e == "rbw":
                self.getEditor(self.tabNum).setLang("Ruby")
            elif e == "cir":
                self.getEditor(self.tabNum).setLang("Spice")
            elif e == "sql":
                self.getEditor(self.tabNum).setLang("SQL")
            elif e == "tcl":
                self.getEditor(self.tabNum).setLang("TCL")
            elif e == "tex":
                self.getEditor(self.tabNum).setLang("TeX")
            elif e == "v" or e == "sv" or e == "vh" or e == "svh":
                self.getEditor(self.tabNum).setLang("Verilog")
            elif e == "vhd" or e == "vhdl":
                self.getEditor(self.tabNum).setLang("VHDL")
            elif e == "xml" or e == "xsl" or e == "xsml" or e == "xsd" or \
            e == "kml" or e == "wsdl" or e == "xlf" or e == "xliff":
                self.getEditor(self.tabNum).setLang("XML")
            elif e == "yml":
                self.getEditor(self.tabNum).setLang("YML")
        except (ValueError, IndexError):
                self.lexer = QsciLexerText()
                self.lexer.setDefaultFont(config.font)
                self.lexer.setDefaultColor(QColor("Black"))
                self.getEditor(self.tabNum).setLexer(self.lexer)
                self.noLexAct.setChecked(True)

    def new(self):
        main = mainWindow()
        main.show()

    def open(self):
        index = self.tab.currentIndex()
        if(self.file != ('', '')):
            with open(self.file, "rt") as f:
                if self.tabNum >= 1:
                    self.newEditor()
                    #print "t"
                    self.tab.setTabText(index+1, os.path.basename(str(self.file)))
                    self.getEditor(self.tabNum).setText(f.read())
                    self.tab.setCurrentIndex(index+1)
                if self.tabNum == 0:
                    self.tabNum = 1
                    self.tab.setTabText(index, os.path.basename(str(self.file)))
                    #print(self.tabNum)
                    self.getEditor(self.tabNum).setText(f.read())
                    self.tab.setCurrentIndex(index+1)
        # Try to guess the lexer based on extension
        self.guessLexer()
        # Not really sure where else to put this
        self.getEditor(self.tab.currentIndex()+1).setModified(False)
        self.getEditor(self.tabNum).textChanged.connect(self.unsaved)

    def newEditor(self):
        self.tabNum+=1
        # Add a new entry to the dict and map it an editor object
        self.editDict["edit"+str(self.tabNum)] = Editor()
        self.tab.addTab(self.getEditor(self.tabNum),
                        os.path.basename(str(self.file)))
        #print "o"

    def openFile(self):
        self.file = QFileDialog.getOpenFileName(self, 'Open File',".")[0]
        try:
            config.docList.append(str(self.file))
            #print "k"
            self.open()
        except AttributeError:
            config.docList.append(str(self.file))
            self.open()
            #print "h"

    def loadDocs(self):
        fh = None
        if not os.access(".open.p", os.F_OK):
            return
        else:
            try:
                fh = gzip.open(".open.p", "rb")
                config.docList = pickle.load(fh)
                for x in config.docList:
                    self.file = x[0]
                    self.open()
            except (IOError, OSError):
                #print e
                return
            finally:
                if fh is not None:
                    fh.close()

    def save(self):
        # Save the file as plain text
        with open(self.getCurrentFile(), "wt") as file:
            file.write(self.getEditor(self.tab.currentIndex()+1).text())
        # Note that changes to the document are saved
        self.edit.setModified(False)
        # Set the tab title to filename
        self.tab.setTabText(self.tab.currentIndex(),
                            os.path.basename(str(self.getCurrentFile())))

    def saveDocs(self):
        try:
            fh = gzip.open(".open.p", "wb")
            pickle.dump(config.docList, fh, 2)
        except (IOError, OSError) as e:
            raise e
        finally:
            if fh:
                fh.close()

    def saveFile(self):
        # Only open if it hasn't previously been saved
        if len(config.docList) != 0:
            if self.getCurrentFile() == 'Untitled':                
                config.docList[self.tab.currentIndex()] = \
                QFileDialog.getSaveFileName(self, 'Save File')
                print('current : ', config.docList[self.tab.currentIndex()], ' comparator: ', self.getCurrentFile())
                self.save()
            else:
                print('Current: ', config.docList[self.tab.currentIndex()], '----not equal', ' comparator: ', self.getCurrentFile())
                self.save()
        else:
            config.docList.append(QFileDialog.getSaveFileName
                                  (self, 'Save File'))
            self.save()

    def saveFileAs(self):
        config.filename = QFileDialog.getSaveFileName(self, 'Save File')
        self.save()

    def unsaved(self):
        if self.getEditor(self.tab.currentIndex()+1).isModified:
            self.tab.setTabText(self.tab.currentIndex(),
                                os.path.dirname(self.getCurrentFile()+"*"))

    def about(self):
        QMessageBox.about(self, "About Desktop Text Editor",
                                "<p>Desktop Text Editor is a sample task project in fulfilment of GeoproKe sample interview task " \
                                "made with PyQt5 and QScintilla.</p> <p>Core objectives</p>"\
                                "<li> Open new file</li>"\
                                "<li>Open existing file for editing</li>"\
                                "<li> Save file</li>"\
                                "<li> Save As functionality</li>"
                                )

    def toggleTabs(self):
        state = self.tab.isVisible()
        self.tab.setVisible(not state)

    def newTab(self):
        self.tabNum+=1
        # Add a new entry to the dict and map it to an editor object
        self.editDict["edit"+str(self.tabNum)] = Editor()
        self.tab.addTab(self.getEditor(self.tabNum),
                        "Untitled")
        config.docList.append("Untitled")
        self.guessLexer()
        try:
            self.getEditor(self.tab.currentIndex()+1).lexer.setFont(config.font)
        except:
            pass

    def showTerm(self):
        self.termVis = True
        self.termSplit.addWidget(self.term)
        self.term.resize(800,40)
        self.term.setFont(config.font)
        self.term.show()

    def hideTerm(self):
        self.termVis = False
        self.term.hide()

    def toggleTerm(self):
        self.hideTerm() if self.termVis else self.showTerm()

    def showTree(self):
        self.ftree = Tree(self)
        self.treeVis = True
        self.ftree.resize(80,430)
        self.treeSplit.addWidget(self.ftree)
        self.ftree.show()

    def hideTree(self):
        self.treeVis = False
        self.ftree.close()

    def toggleTree(self):
        self.hideTree() if self.treeVis else self.showTree()

    def loadTermAndTree(self):
        if self.treeVis:
            self.showTree()
            self.treeAct.setChecked(True)
        else:
            self.treeVis = False
            self.treeAct.setChecked(False)
        if self.termVis:
            self.showTerm()
            self.termAct.setChecked(True)
        else:
            self.termVis = False
            self.termAct.setChecked(False)

    def toggleIntGuide(self):
        state = self.edit.indentationGuides()
        self.edit.setIndentationGuides(not state)

    def toggleLN(self):
        state = self.edit.marginLineNumbers(0)
        self.edit.setMarginLineNumbers(0, not state)
        self.edit.setMarginWidth(0,0) if state == True else self.edit. \
                                setMarginWidth(0,self.edit.metrics.width("00000"))

    def fr(self):
        frwin = Find(self)
        frwin.show()

    def chooseFont(self):
        font, ok = QFontDialog.getFont()
        if ok:
            config.font = font
            try:
                self.getEditor(self.tab.currentIndex()).lexer().setFont(config.font)
            except AttributeError:
                self.getEditor(self.tab.currentIndex()).setLang(QsciLexerText())
                #print self.getEditor(self.tab.currentIndex()).lexer()
                self.getEditor(self.tab.currentIndex()).lexer().setFont(config.font)

    def setProDir(self):
        pdir, ok = QInputDialog.getText(self, "Set Project Directory", "Enter absolute path (i.e. "\
                                             "/home/brian/Documents)")
        if ok:
            config.proDir = pdir
            #print config.proDir


    # This method adapted from Peter Goldsborough's Writer.
    # Save settings and alerts the user if they are saving an edited file.
    def closeEvent(self,event):
        self.writeSettings()
        self.saveDocs()
        if not self.edit.isModified():
            event.accept()
        else:
            dialog = QMessageBox(self)
            dialog.setIcon(QMessageBox.Warning)
            dialog.setText(config.filename+" has unsaved changes.")
            dialog.setInformativeText("Do you want to save your changes?")
            dialog.setStandardButtons(QMessageBox.Save |
                                  QMessageBox.Cancel |
                                  QMessageBox.Discard)
            dialog.setDefaultButton(QMessageBox.Save)
            response = dialog.exec_()
            if response == QMessageBox.Save:
                self.save()
            elif response == QMessageBox.Discard:
                event.accept()
            else: event.ignore()

    def resizeEvent(self,event):
        # Don't try to resize a non-existant file tree
        try:
            self.ftree.treeView.resize(self.ftree.treeView.width(), self.height())
        except:
            pass
        try:
            self.term.resize(self.width(), self.term.height())
        except:
            pass

    def keyPressEvent(self,event):
        key = event.key() 
        if self.getEditor(self.tab.currentIndex()) == None:
            return
        if (self.getEditor(self.tab.currentIndex()).text() == "bee movie"):
            with open("bee_movie.txt", "r") as file:
                script = file.read()
            self.getEditor(self.tab.currentIndex()).setText(script)
