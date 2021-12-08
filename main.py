import sys
from typing import Dict, List

from Globals import Style
from Items import OverlayGraphicsItem, OverlayListWidgetItem
from Models import OverlayItemProxy
from Widgets import OverlayItemsWidget, OverlayPreviewWidget

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSplitter, QWidget
from PySide6.QtGui import QAction

class ElayvateWindow(QMainWindow):
    
    items: List[OverlayItemProxy] = []

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

        self.itemsFrame.itemAdded.connect(self.onListItemAdded)
        self.itemsFrame.itemDeleted.connect(self.onListItemDeleted)
        self.splitter.addWidget(self.itemsFrame)

    def createOverlayBox(self):

        self.overlayFrame = OverlayPreviewWidget(self.centralWidget())

        self.overlayFrame.itemAdded.connect(self.onSceneItemAdded)
        self.overlayFrame.itemDeleted.connect(self.onSceneItemDeleted)
        self.splitter.addWidget(self.overlayFrame)

    def getProxy(self, object):

        for i, proxy in enumerate(self.items):

            if proxy.widget is object \
                or proxy.graphics is object \
                or proxy.item is object: return i, proxy

        return -1, None

    @Slot(OverlayGraphicsItem)
    def onSceneItemAdded(self, object: OverlayGraphicsItem):
        
        proxy = OverlayItemProxy()
        proxy.item.x = object.x()
        proxy.item.y = object.y()
        proxy.item.width = object.boundingRect().width()
        proxy.item.height = object.boundingRect().height()
        proxy.graphics = object

        self.itemsFrame.addItem(proxy=proxy)
        self.items.append(proxy)

    @Slot(OverlayListWidgetItem)
    def onListItemAdded(self, object: OverlayListWidgetItem):
        
        proxy = OverlayItemProxy()
        proxy.item.name = object.text()
        proxy.widget = object 

        self.overlayFrame.addItem(proxy=proxy)
        self.items.append(proxy)

    @Slot(OverlayGraphicsItem)
    def onSceneItemDeleted(self, object: OverlayGraphicsItem):

        _, proxy = self.getProxy(object)
        if proxy is None: return 
        
        self.itemsFrame.deleteItem(proxy=proxy)
        self.items.remove(proxy)

    @Slot(OverlayListWidgetItem)
    def onListItemDeleted(self, object: OverlayListWidgetItem):

        _, proxy = self.getProxy(object)
        if proxy is None: return 
        
        self.overlayFrame.deleteItem(proxy=proxy)
        self.items.remove(proxy)

    @Slot(OverlayGraphicsItem)
    def onSceneItemChanged(self, object: OverlayGraphicsItem):

       i, proxy = self.getProxy(object)
       if proxy is None: return 

       self.itemsFrame.renameItem(proxy=proxy)
       self.items[i] = proxy 

    @Slot(OverlayListWidgetItem)
    def onListItemChanged(self, object: OverlayListWidgetItem):

        i, proxy = self.getProxy(object)
        if proxy is None: return 
        
        proxy.item.name = object.text()
        self.items[i] = proxy


if __name__ == '__main__':

    app = QApplication([])
    window = ElayvateWindow()
    app.setStyleSheet(Style.QApplication)
    window.show()
    sys.exit(app.exec())