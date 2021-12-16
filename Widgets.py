from types import NoneType
from typing import Callable, Dict, List
from Items import OverlayPreviewGraphicsItem, OverlayListWidgetItem, ScreenPreviewItem
from Globals import Colors, Math, Style
from Models import OverlayItemProxy, CallableActionProxy

from PySide6.QtCore import QEvent, QPoint, Qt, Signal
from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGridLayout, QLabel, QLineEdit, QListWidget, QMenu, QVBoxLayout, QWidget
from PySide6.QtGui import QAction, QContextMenuEvent, QKeyEvent, QMouseEvent, QResizeEvent

class PropertyLineEdit(QLineEdit):
    
    def __init__(self, value = ''):

        super().__init__(value)
        self.setContextMenuPolicy(Qt.NoContextMenu)

class ClickableLineEdit(QLineEdit):
    
    clicked = Signal(QEvent)

    def __init__(self, value = ''):

        super().__init__(value)
        self.setReadOnly(True)
        
        self.__actions: List[CallableActionProxy] = []

        copy = QAction('Copy')
        copy.setShortcut('Ctrl+C')

        self.addAction(copy, lambda _: QApplication.clipboard().setText(self.text()))
        self.addSeperator()

    def mousePressEvent(self, event: QMouseEvent):

        if event.button() is Qt.MouseButton.LeftButton: self.clicked.emit(event)
        super().mousePressEvent(event)

    def getCallableAction(self, action: QAction) -> CallableActionProxy:

        if action is None: return None

        for proxy in self.__actions: 
            if proxy.action() is action: return proxy
        
        return None 

    def addSeperator(self):

        self.__actions.append(CallableActionProxy(None, None))

    def addAction(self, action: QAction, func: Callable):

        self.__actions.append(CallableActionProxy(action, func))

    def removeAction(self, action: QAction):

        proxy = self.getCallableAction(action)
        self.__actions.remove(proxy)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:

        contextMenu = QMenu()

        for proxy in self.__actions:

            if proxy.action() is None: contextMenu.addSeparator()
            else: contextMenu.addAction(proxy.action())

        action = contextMenu.exec(self.mapToGlobal(event.pos()))
        callableAction = self.getCallableAction(action)

        if callableAction is not None: callableAction.callable()(event)

class BrowseLineEdit(ClickableLineEdit):
    
    def __init__(self, value = ''):

        super().__init__(value)
        self.addAction(QAction('Browse...'), self.clicked.emit)
        self.setToolTip('Left-click to change the source. \nRight-click for more actions.')

class EGraphicsView(QGraphicsView):

        def __init__(self, parent: QWidget):

            super().__init__(parent)
            scene = QGraphicsScene()
            self.setScene(scene)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setFrameShape(QFrame.NoFrame)

            screen = QGraphicsRectItem(0, 0, self.screen().size().width(), self.screen().size().height())
            screen.setBrush(Qt.NoBrush)
            screen.setPen(Qt.NoPen)
            self.scene().addItem(screen)

class OverlayWidget(QWidget):

    # Signals
    itemAdded = Signal(object)
    itemDeleted = Signal(object)
    itemChanged = Signal(object)
    itemSelected = Signal(object, bool)

    def __init__(self, parent: QWidget):

        super().__init__(parent)

class OverlayPreviewWidget(OverlayWidget):

    # Constants
    ZOOM_FACTOR = 1.25

    def __init__(self, parent: QWidget):

        super().__init__(parent)

        self.isMoving = False
        self.view = EGraphicsView(self)

        self.view.viewport().installEventFilter(self)
        self.setStyleSheet('background: {}'.format(Colors.MenuDark))
        self.drawScreenPreview()
        
    def eventFilter(self, source, e: QEvent) -> bool:

        if   e.type() == QEvent.Type.MouseButtonPress: self.mousePressEvent(e)
        elif e.type() == QEvent.Type.MouseButtonRelease: self.mouseReleaseEvent(e)
        elif e.type() == QEvent.Type.MouseMove: self.mouseMoveEvent(e)

        return super().eventFilter(source, e)

    def resizeEvent(self, e: QResizeEvent):

        super().resizeEvent(e)
        self.view.setFixedSize(self.width(), self.height())

    def keyPressEvent(self, e: QKeyEvent):
        
        super().keyPressEvent(e)

        # Zoom
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier:

            if   e.key() == Qt.Key.Key_Equal: self.zoomIn()
            elif e.key() == Qt.Key.Key_Minus: self.zoomOut()
            elif e.key() == Qt.Key.Key_0:     self.fitScreen()

    def contextMenuEvent(self, e: QContextMenuEvent):
        
        super().contextMenuEvent(e)

        contextMenu = QMenu(self)
        newMenu = contextMenu.addMenu('New')
        viewMenu = contextMenu.addMenu('View')

        newImage = newMenu.addAction('Image')
        zoomIn = viewMenu.addAction('Zoom In')
        zoomOut = viewMenu.addAction('Zoom Out')
        fillWindow = viewMenu.addAction('Fill Window')

        zoomIn.setShortcut('Ctrl++')
        zoomOut.setShortcut('Ctrl+-')
        fillWindow.setShortcut('Ctrl+0')
        
        action = contextMenu.exec(self.mapToGlobal(e.pos()))
        
        if   action is newImage: self.addItem(position=e.pos())
        elif action is zoomIn: self.zoomIn()
        elif action is zoomOut: self.zoomOut()
        elif action is fillWindow: self.fitScreen()

    def mousePressEvent(self, e: QMouseEvent):
        
        super().mousePressEvent(e)
        if e.button() != Qt.MouseButton.MiddleButton: return 

        self.__previousMousePosition = e.pos()
        self.isMoving = True

        QApplication.instance().setOverrideCursor(Qt.SizeAllCursor)
        
    def mouseReleaseEvent(self, e: QMouseEvent):
        
        super().mouseReleaseEvent(e)
        self.isMoving = False
        QApplication.instance().restoreOverrideCursor()

    def mouseMoveEvent(self, e: QMouseEvent):

        super().mouseMoveEvent(e)
        if not self.isMoving: return 

        offset: QPoint = self.__previousMousePosition - e.pos()
        self.__previousMousePosition = e.pos()

        vertSB = self.view.verticalScrollBar()
        horiSB = self.view.horizontalScrollBar()

        vertSB.setValue(vertSB.value() + offset.y())
        horiSB.setValue(horiSB.value() + offset.x())

    def drawScreenPreview(self):

        width = self.screen().size().width()
        height = self.screen().size().height()
        self.cellSize = Math.toCellSize(width + height)
        self.screenPreviewItem = ScreenPreviewItem(width, height, self.cellSize)
        self.view.scene().addItem(self.screenPreviewItem)

    def zoomIn(self):

        self.view.scale(self.ZOOM_FACTOR, self.ZOOM_FACTOR)

    def zoomOut(self):

        self.view.scale(1 / self.ZOOM_FACTOR, 1 / self.ZOOM_FACTOR)

    def fitScreen(self):

        self.view.fitInView(

            self.screenPreviewItem.boundingRect(), 
            Qt.AspectRatioMode.KeepAspectRatio
        )

    def addItem(self, proxy: OverlayItemProxy = None, position: QPoint = None):

        preview = OverlayPreviewGraphicsItem(self, 0, 0, self.cellSize * 10, self.cellSize * 10)

        if position is not None: 

            position = self.view.mapToScene(position)
            position = Math.gridSnap(position.x(), position.y(), self.cellSize)
            preview.setPos(position)

        self.view.scene().addItem(preview)
        if proxy is None: self.itemAdded.emit(preview)
        else: proxy.setpreviewGraphicsItem(preview)

    def deleteItem(self, proxy: OverlayItemProxy = None, graphics: OverlayPreviewGraphicsItem = None):

        if graphics is not None: 
            
            self.view.scene().removeItem(graphics)
            self.itemDeleted.emit(graphics)
        
        elif proxy is not None: self.view.scene().removeItem(proxy.previewGraphicsItem())

    def updateItem(self, proxy: OverlayItemProxy = None, graphics: OverlayPreviewGraphicsItem = None):

        if graphics is not None: self.itemChanged.emit(graphics)

    def selectItem(self, selected: bool, proxy: OverlayItemProxy = None, graphics: OverlayPreviewGraphicsItem = None):

        if graphics is not None: self.itemSelected.emit(graphics, selected)
        elif proxy is not None: proxy.previewGraphicsItem().setSelected(selected)

class OverlayItemListWidget(OverlayWidget):

    def __init__(self, parent: QWidget):
    
        super().__init__(parent)
        QVBoxLayout(self)

        self.label = QLabel('Items')
        self.list = QListWidget()

        self.list.currentItemChanged.connect(self.onCurrentItemChanged)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.list)
        self.stylize()

    def contextMenuEvent(self, e: QContextMenuEvent):
        
        super().contextMenuEvent(e)
        contextMenu = QMenu(self)
        newMenu = contextMenu.addMenu('New')
        newImage = newMenu.addAction('Image')

        contextMenu.addSeparator()

        deleteItem = contextMenu.addAction('Delete')
        renameItem = contextMenu.addAction('Rename')

        deleteItem.setShortcut('Delete')

        if self.list.currentItem() is None: 

            deleteItem.setVisible(False)
            renameItem.setVisible(False)

        action = contextMenu.exec(self.mapToGlobal(e.pos()))

        if   action is newImage: self.addItem()
        elif action is deleteItem: self.deleteItem(widget=self.list.currentItem())

    def stylize(self):

        self.setStyleSheet(Style.OverlayItemListWidget)
        self.layout().setContentsMargins(Style.NoMargins)
        self.layout().setSpacing(0)

        # Label
        self.label.setStyleSheet(Style.OverlayItemBoxTitle)
        self.label.setContentsMargins(Style.SmallMargins)

        # List
        self.list.setContentsMargins(Style.SmallMargins)

    def addItem(self, proxy: OverlayItemProxy = None):

        widget = OverlayListWidgetItem(self, 'Image')
        self.list.addItem(widget)

        if proxy is None: self.itemAdded.emit(widget)
        else: proxy.setListWidgetItem(widget)

    def deleteItem(self, proxy: OverlayItemProxy = None, widget: OverlayListWidgetItem = None):

        if widget is not None: self.itemDeleted.emit(self.list.takeItem(self.list.row(widget)))
        elif proxy is not None: self.list.takeItem(self.list.row(proxy.listWidgetItem()))


    def selectItem(self, selected: bool, proxy: OverlayItemProxy = None, widget: OverlayListWidgetItem = None):

        if widget is not None: self.itemSelected.emit(widget, selected)

        elif proxy is not None: 
            
            if selected: self.list.setCurrentItem(proxy.listWidgetItem())
            else: self.list.setCurrentItem(None)

    def onCurrentItemChanged(self, current: OverlayListWidgetItem, previous: OverlayListWidgetItem):

        if previous is not None: self.selectItem(False, widget=previous)
        if current is not None: self.selectItem(True, widget=current)

class OverlayItemPropertiesWidget(OverlayWidget):

    currentEvent = None

    def __init__(self, parent: QWidget):

        super().__init__(parent)
        QGridLayout(self)

        self.proxy = None 
        self.label = QLabel('Properties')
        self.xEdit = PropertyLineEdit()
        self.yEdit = PropertyLineEdit()
        self.wEdit = PropertyLineEdit()
        self.hEdit = PropertyLineEdit()
        self.srcEdit = BrowseLineEdit()

        self.layout().addWidget(self.label,        0, 0, 1, 4)
        self.layout().addWidget(QLabel('X:'),      1, 0, 1, 1)
        self.layout().addWidget(self.xEdit,        1, 1, 1, 1)
        self.layout().addWidget(QLabel('Y:'),      1, 2, 1, 1)
        self.layout().addWidget(self.yEdit,        1, 3, 1, 1)
        self.layout().addWidget(QLabel('W:'),      2, 0, 1, 1)
        self.layout().addWidget(self.wEdit,        2, 1, 1, 1)
        self.layout().addWidget(QLabel('H:'),      2, 2, 1, 1)
        self.layout().addWidget(self.hEdit,        2, 3, 1, 1)
        self.layout().addWidget(QLabel('Source:'), 3, 0, 1, 1)
        self.layout().addWidget(self.srcEdit,      3, 1, 1, 3)
        self.layout().setRowStretch(4, 1)
        self.stylize()
        self.setItem()

    def openFileBrowser(self, _):

        fname, _ = QFileDialog.getOpenFileName(filter='Images (*.jpg, *.jpeg, *.png)')
        self.sourceEdit.setText(fname)

    def stylize(self):

        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(Style.OverlayItemPropertiesWidget)
        self.layout().setContentsMargins(Style.NoMargins)
        self.layout().setSpacing(5)

        # Label
        self.label.setStyleSheet(Style.OverlayItemBoxTitle)
        self.label.setContentsMargins(Style.SmallMargins)

    def clearLineEdits(self):

        self.xEdit.setText('')
        self.yEdit.setText('')
        self.wEdit.setText('')
        self.hEdit.setText('')
        self.srcEdit.setText('')

    def enableLineEdits(self, enable: bool):

        self.xEdit.setEnabled(enable)
        self.yEdit.setEnabled(enable)
        self.wEdit.setEnabled(enable)
        self.hEdit.setEnabled(enable)
        self.srcEdit.setEnabled(enable)

    def disconnectLineEdits(self):

        try:

            self.xEdit.editingFinished.disconnect()
            self.yEdit.editingFinished.disconnect()
            self.wEdit.editingFinished.disconnect()
            self.hEdit.editingFinished.disconnect()
            self.srcEdit.clicked.disconnect()
        
        except: pass

    def connectLineEdits(self):

        self.xEdit.editingFinished.connect(self.updateItemGraphics)
        self.yEdit.editingFinished.connect(self.updateItemGraphics)
        self.wEdit.editingFinished.connect(self.updateItemGraphics)
        self.hEdit.editingFinished.connect(self.updateItemGraphics)
        self.srcEdit.clicked.connect(self.updateItemSource)

    def linkLineEdits(self):

        self.xEdit.setText(str(self.proxy.x()))
        self.yEdit.setText(str(self.proxy.y()))
        self.wEdit.setText(str(self.proxy.width()))
        self.hEdit.setText(str(self.proxy.height()))
        self.srcEdit.setText(self.proxy.source())

    def setItem(self, proxy: OverlayItemProxy = None):

        self.proxy = proxy 
        if proxy is None: 
            
            self.disconnectLineEdits()
            self.clearLineEdits()
            self.enableLineEdits(False)
            return 

        self.disconnectLineEdits()
        self.linkLineEdits()
        self.connectLineEdits()
        self.enableLineEdits(True)

    def updateItemGraphics(self):

        if self.proxy is None: return

        self.proxy.setRect(

            float(self.xEdit.text()),
            float(self.yEdit.text()),
            float(self.wEdit.text()),
            float(self.hEdit.text())
        )

        # Quick and dirty way to format fields
        self.setItem(self.proxy)

    def updateItemSource(self, event: QEvent):

        if event is self.currentEvent: return 
        self.currentEvent = event

        fname, _ = QFileDialog.getOpenFileName(filter='All Images (*.jpg *.jpeg *.png *.gif)')
        self.srcEdit.setText(fname)
        self.proxy.setSource(fname)

