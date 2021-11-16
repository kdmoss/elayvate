import sys
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QListView, QMainWindow, QGroupBox, QSizePolicy, QWidget
from PyQt6.QtGui import QAction, QResizeEvent, QStandardItem, QStandardItemModel

class PyCrossWindow(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        self._layout = QGridLayout()

        self.setWindowFlags
        (
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.FramelessWindowHint  |
            QtCore.Qt.WindowType.WindowSystemMenuHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint
        )
        self.setLayout(self._layout)
        self.setCentralWidget(QWidget(self))
        self.setWindowTitle('PyCross')
        self.createMenuBar()
        self.createItemsBox()
        self.setMinimumSize(1200, 600)
        
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
        
        self.itemsGroupBox = QGroupBox('Items', self.centralWidget())    
        self.itemsListView = QListView(self.itemsGroupBox)
        self.itemsListModel = QStandardItemModel()        
        self.entries = ['image', 'billboard']

        self.itemsGroupBox.setMinimumSize(300, self.minimumHeight() - 10)
        self.itemsListView.setMinimumSize(280, self.minimumHeight() - 10)

        self.itemsListView.setModel(self.itemsListModel)
        for entry in self.entries: self.itemsListModel.appendRow(QStandardItem(entry))
        self._layout.addWidget(self.itemsGroupBox)
    
    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        self.itemsGroupBox.setGeometry(10, 10, 300, self.height() - 40)
        self.itemsListView.setGeometry(10, 20, 280, self.height() - 70)



if __name__ == '__main__':

    app = QApplication([])
    window = PyCrossWindow()

    window.show()
    sys.exit(app.exec())