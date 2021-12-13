import sys
from typing import Dict, List

from Globals import Style
from Items import OverlayGraphicsItem, OverlayListWidgetItem
from Models import OverlayItemProxy
from Widgets import EGraphicsView, OverlayItemListWidget, OverlayItemPropertiesWidget, OverlayPreviewWidget

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QApplication, QGraphicsView, QHBoxLayout, QLayout, QMainWindow, QSplitter, QWidget
from PySide6.QtGui import QAction, QCloseEvent

class EWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.setCentralWidget(QWidget(self))
        QHBoxLayout(self.centralWidget())

    def innerLayout(self) -> QLayout:
        
        return self.centralWidget().layout()

class ElayvateOverlayWindow(EWindow):

    def __init__(self):

        super().__init__()
        
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_AlwaysStackOnTop, True)

        view = EGraphicsView(self.centralWidget())
        view.setStyleSheet('background: transparent')
        self.innerLayout().addWidget(view)

class ElayvateWindow(EWindow):
    
    items: List[OverlayItemProxy] = []

    def __init__(self, overlay: ElayvateOverlayWindow):
        
        super().__init__()
        self.overlayWindow = overlay
        self.hSplitter = QSplitter(Qt.Orientation.Horizontal)
        self.vSplitter = QSplitter(Qt.Orientation.Vertical)

        self.setWindowTitle('Elayvate')
        self.createMenuBar()
        self.createItemsBox()
        self.createOverlayBox()

        self.hSplitter.setSizes([5, 500])
        self.innerLayout().setContentsMargins(Style.NoMargins)
        self.innerLayout().setSpacing(0)
        self.innerLayout().addWidget(self.hSplitter)
        
        self.resize(
            
            self.screen().size().width() // 3, 
            self.screen().size().height() // 3
        )
        self.setMinimumSize(300, 100)

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
        
        self.itemList = OverlayItemListWidget(self.centralWidget())
        self.itemProps = OverlayItemPropertiesWidget(self.centralWidget())

        self.itemList.itemAdded.connect(self.onListItemAdded)
        self.itemList.itemDeleted.connect(self.onListItemDeleted)
        self.itemList.itemSelected.connect(self.onListItemSelected)

        self.vSplitter.addWidget(self.itemList)
        self.vSplitter.addWidget(self.itemProps)
        self.hSplitter.addWidget(self.vSplitter)

    def createOverlayBox(self):

        self.overlayFrame = OverlayPreviewWidget(self.centralWidget())

        self.overlayFrame.itemAdded.connect(self.onSceneItemAdded)
        self.overlayFrame.itemDeleted.connect(self.onSceneItemDeleted)
        self.overlayFrame.itemChanged.connect(self.onSceneItemChanged)
        self.overlayFrame.itemSelected.connect(self.onSceneItemSelected)

        self.hSplitter.addWidget(self.overlayFrame)

    def getProxy(self, object):

        for i, proxy in enumerate(self.items):

            if proxy.widget is object \
                or proxy.graphics is object: return i, proxy

        return -1, None

    @Slot(OverlayGraphicsItem)
    def onSceneItemAdded(self, object: OverlayGraphicsItem):
        
        proxy = OverlayItemProxy()
        proxy.graphics = object

        self.itemList.addItem(proxy=proxy)
        self.items.append(proxy)

    @Slot(OverlayListWidgetItem)
    def onListItemAdded(self, object: OverlayListWidgetItem):
        
        proxy = OverlayItemProxy()
        proxy.widget = object 

        self.overlayFrame.addItem(proxy=proxy)
        self.items.append(proxy)

    @Slot(OverlayGraphicsItem)
    def onSceneItemDeleted(self, object: OverlayGraphicsItem):

        _, proxy = self.getProxy(object)
        if proxy is None: return 
        
        self.itemList.deleteItem(proxy=proxy)
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
        
        self.itemProps.setItem(proxy=proxy)
        self.items[i] = proxy

    @Slot(OverlayListWidgetItem)
    def onListItemChanged(self, object: OverlayListWidgetItem):

        i, proxy = self.getProxy(object)
        if proxy is None: return 
        
        self.itemProps.setItem(proxy=proxy)
        self.items[i] = proxy

    @Slot(OverlayGraphicsItem, bool)
    def onSceneItemSelected(self, object: OverlayGraphicsItem, selected: bool):

        i, proxy = self.getProxy(object)
        if proxy is None: return 

        if selected: self.itemProps.setItem(proxy=proxy)
        else: self.itemProps.setItem(proxy=None)

        self.itemList.selectItem(selected, proxy=proxy)
        self.items[i] = proxy 

    @Slot(OverlayListWidgetItem, bool)
    def onListItemSelected(self, object: OverlayListWidgetItem, selected: bool):

        i, proxy = self.getProxy(object)
        if proxy is None: return 
        
        if selected: self.itemProps.setItem(proxy=proxy)
        else: self.itemProps.setItem(proxy=None)

        self.overlayFrame.selectItem(selected, proxy=proxy)
        self.items[i] = proxy

    def closeEvent(self, event:QCloseEvent):
        
        #overlay.showFullScreen()
        super().closeEvent(event)


if __name__ == '__main__':

    app = QApplication([])
    overlay = ElayvateOverlayWindow()
    window = ElayvateWindow(overlay=overlay)
    app.setStyleSheet(Style.QApplication)
    window.show()
    sys.exit(app.exec())