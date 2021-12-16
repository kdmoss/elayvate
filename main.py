import sys
from typing import List
from Dialogs import HotkeyMapperDialog

from Globals import Style
from Items import OverlayPreviewGraphicsItem, OverlayListWidgetItem
from Models import OverlayItemProxy
from Widgets import EGraphicsView, OverlayItemListWidget, OverlayItemPropertiesWidget, OverlayPreviewWidget

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QApplication, QGraphicsRectItem, QHBoxLayout, QLayout, QMainWindow, QSplitter, QWidget
from PySide6.QtGui import QAction, QCloseEvent, QKeyEvent, QResizeEvent

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

        self.view = EGraphicsView(self.centralWidget())
        
        self.view.setStyleSheet('background: transparent')
        self.view.setFixedSize(self.screen().size())

        self.innerLayout().setContentsMargins(0, 0, 0, 0)
        self.innerLayout().addWidget(self.view)

    def addItem(self, proxy: OverlayItemProxy):

        self.view.scene().addItem(proxy.finalGraphicsItem())

    def keyPressEvent(self, event: QKeyEvent):
        
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_P:
            
            self.view.setVisible(not self.view.isVisible())

class ElayvateWindow(EWindow):
    
    proxies: List[OverlayItemProxy] = []

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

        hotkeyMapperAction.triggered.connect(self.openHotkeyDialog)

    def openHotkeyDialog(self):

        dialog = HotkeyMapperDialog(self)
        dialog.show()

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

        self.overlayFrame.itemAdded.connect(self.onPreviewItemAdded)
        self.overlayFrame.itemDeleted.connect(self.onPreviewItemDeleted)
        self.overlayFrame.itemChanged.connect(self.onPreviewItemChanged)
        self.overlayFrame.itemSelected.connect(self.onPreviewItemSelected)

        self.hSplitter.addWidget(self.overlayFrame)

    def getProxy(self, object):

        for i, proxy in enumerate(self.proxies):

            if proxy.listWidgetItem() is object \
                or proxy.previewGraphicsItem() is object: return i, proxy

        return -1, None

    @Slot(OverlayPreviewGraphicsItem)
    def onPreviewItemAdded(self, object: OverlayPreviewGraphicsItem):
        
        proxy = OverlayItemProxy()
        proxy.setpreviewGraphicsItem(object)

        self.itemList.addItem(proxy=proxy)
        self.overlayWindow.addItem(proxy=proxy)
        self.proxies.append(proxy)

    @Slot(OverlayListWidgetItem)
    def onListItemAdded(self, object: OverlayListWidgetItem):
        
        proxy = OverlayItemProxy()
        proxy.setListWidgetItem(object) 

        self.overlayFrame.addItem(proxy=proxy)
        self.overlayWindow.addItem(proxy=proxy)
        self.proxies.append(proxy)

    @Slot(OverlayPreviewGraphicsItem)
    def onPreviewItemDeleted(self, object: OverlayPreviewGraphicsItem):

        _, proxy = self.getProxy(object)
        if proxy is None: return 
        
        self.itemList.deleteItem(proxy=proxy)
        self.proxies.remove(proxy)

    @Slot(OverlayListWidgetItem)
    def onListItemDeleted(self, object: OverlayListWidgetItem):

        _, proxy = self.getProxy(object)
        if proxy is None: return 
        
        self.overlayFrame.deleteItem(proxy=proxy)
        self.proxies.remove(proxy)

    @Slot(OverlayPreviewGraphicsItem)
    def onPreviewItemChanged(self, object: OverlayPreviewGraphicsItem):

        i, proxy = self.getProxy(object)
        if proxy is None: return 
        
        self.itemProps.setItem(proxy=proxy)
        self.proxies[i] = proxy

    @Slot(OverlayListWidgetItem)
    def onListItemChanged(self, object: OverlayListWidgetItem):

        i, proxy = self.getProxy(object)
        if proxy is None: return 
        
        self.itemProps.setItem(proxy=proxy)
        self.proxies[i] = proxy

    @Slot(OverlayPreviewGraphicsItem, bool)
    def onPreviewItemSelected(self, object: OverlayPreviewGraphicsItem, selected: bool):

        i, proxy = self.getProxy(object)
        if proxy is None: return 

        if selected: self.itemProps.setItem(proxy=proxy)
        else: self.itemProps.setItem(proxy=None)

        self.itemList.selectItem(selected, proxy=proxy)
        self.proxies[i] = proxy 

    @Slot(OverlayListWidgetItem, bool)
    def onListItemSelected(self, object: OverlayListWidgetItem, selected: bool):

        i, proxy = self.getProxy(object)
        if proxy is None: return 
        
        if selected: self.itemProps.setItem(proxy=proxy)
        else: self.itemProps.setItem(proxy=None)

        self.overlayFrame.selectItem(selected, proxy=proxy)
        self.proxies[i] = proxy

    def closeEvent(self, event: QCloseEvent):
        
        overlay.showFullScreen()
        super().closeEvent(event)


if __name__ == '__main__':

    app = QApplication([])
    overlay = ElayvateOverlayWindow()
    window = ElayvateWindow(overlay=overlay)

    app.setStyleSheet(Style.QApplication)
    window.show()
    sys.exit(app.exec())