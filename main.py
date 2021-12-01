import sys

from PyQt6 import QtCore

from Globals import Style 
from Widgets import OverlayItemsWidget, OverlayPreviewWidget

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSplitter, QWidget
from PyQt6.QtGui import QAction

class ElayvateWindow(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        self.setCentralWidget(QWidget(self))
        QHBoxLayout(self.centralWidget())
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.setWindowTitle('Elayvate')
        self.createMenuBar()
        self.createItemsBox()
        self.createOverlayBox()
        self.innerLayout().setContentsMargins(0, 0, 0, 0)
        self.innerLayout().setSpacing(0)
        self.innerLayout().addWidget(self.splitter)
        self.resize(
            
            self.screen().size().width() // 3, 
            self.screen().size().height() // 3
        )
        self.setMinimumSize(300, 100)
        self.splitter.setSizes([5, 500])

    def innerLayout(self):
        return self.centralWidget().layout()

    def createMenuBar(self):
        
        self.createFileMenu()
        self.createSettingsMenu()
        self.createHelpMenu()

    def createFileMenu(self):

        newAction = QAction('&New', self)
        openAction = QAction('&Open...', self)
        saveAction = QAction('&Save', self)
        saveAsAction = QAction('&Save As...', self)
        exitAction = QAction('&Exit', self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')

        saveAction.setShortcut('Ctrl+S')
        exitAction.setShortcut('Alt+F4')
        exitAction.triggered.connect(self.close)

        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

    def createSettingsMenu(self):
        
        preferencesAction = QAction('&Preferences...', self)
        hotkeyMapperAction = QAction('&Hotkey Mapper...', self)

        menuBar = self.menuBar()
        settingsMenu = menuBar.addMenu('&Settings')
        
        settingsMenu.addAction(preferencesAction)
        settingsMenu.addAction(hotkeyMapperAction)

    def createHelpMenu(self):

        aboutAction = QAction('&About...', self)
        donateAction = QAction('&Donate...', self)
        
        menuBar = self.menuBar()
        helpMenu = menuBar.addMenu('&Help')

        aboutAction.setShortcut('F1')
        helpMenu.addAction(aboutAction)
        helpMenu.addAction(donateAction)

    def createItemsBox(self):
        
        self.itemsFrame = OverlayItemsWidget(self.centralWidget())
        self.splitter.addWidget(self.itemsFrame)

    def createOverlayBox(self):

        self.overlayFrame = OverlayPreviewWidget(self.centralWidget())
        self.splitter.addWidget(self.overlayFrame)


if __name__ == '__main__':

    app = QApplication([])
    window = ElayvateWindow()
    app.setStyleSheet(Style.QApplication)
    window.show()
    sys.exit(app.exec())