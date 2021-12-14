from Items import OverlayGraphicsItem, OverlayListWidgetItem, ScreenPreviewItem
from Globals import Colors, Math, Style
from Models import OverlayItem, OverlayItemProxy

from PySide6.QtCore import Property, QEvent, QMargins, QPoint, QRect, QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGridLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMenu, QPushButton, QSplitter, QVBoxLayout, QWidget
from PySide6.QtGui import QContextMenuEvent, QFocusEvent, QKeyEvent, QMouseEvent, QResizeEvent, QTextBlock

class EGraphicsView(QGraphicsView):

        def __init__(self, parent: QWidget):

            super().__init__(parent)
            self.setScene(QGraphicsScene())
            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setFrameShape(QFrame.Shape.NoFrame)

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
        self._previousMousePosition = e.pos()
        self.isMoving = True

        application: QApplication = QApplication.instance()
        application.setOverrideCursor(Qt.CursorShape.SizeAllCursor)
        
    def mouseReleaseEvent(self, e: QMouseEvent):
        
        super().mouseReleaseEvent(e)
        self.isMoving = False
        application: QApplication = QApplication.instance()
        application.restoreOverrideCursor()

    def mouseMoveEvent(self, e: QMouseEvent):

        super().mouseMoveEvent(e)
        if not self.isMoving: return 

        offset: QPoint = self._previousMousePosition - e.pos()
        self._previousMousePosition = e.pos()

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

        preview = OverlayGraphicsItem(self, 0, 0, self.cellSize * 10, self.cellSize * 10)

        if position is not None: 

            position = self.view.mapToScene(position)
            position = Math.gridSnap(position.x(), position.y(), self.cellSize)
            preview.setPos(position)

        self.view.scene().addItem(preview)
        if proxy is None: self.itemAdded.emit(preview)
        else: proxy.graphics = preview

    def deleteItem(self, proxy: OverlayItemProxy = None, graphics: OverlayGraphicsItem = None):

        if graphics is not None: 
            
            self.view.scene().removeItem(graphics)
            self.itemDeleted.emit(graphics)
            return 

        if proxy is not None: self.view.scene().removeItem(proxy.graphics)

    def updateItem(self, proxy: OverlayItemProxy = None, graphics: OverlayGraphicsItem = None):

        if graphics is not None: self.itemChanged.emit(graphics)

    def selectItem(self, selected: bool, proxy: OverlayItemProxy = None, graphics: OverlayGraphicsItem = None):

        if graphics is not None: self.itemSelected.emit(graphics, selected)
        elif proxy is not None: proxy.graphics.setSelected(selected)

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

    def resizeEvent(self, e: QResizeEvent):
        
        super().resizeEvent(e)
        self.move(0, 0)

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
        else: proxy.widget = widget

    def deleteItem(self, proxy: OverlayItemProxy = None, widget: OverlayListWidgetItem = None):

        if proxy is not None: self.list.takeItem(self.list.row(proxy.widget))
        elif widget is not None: self.itemDeleted.emit(self.list.takeItem(self.list.row(widget)))


    def selectItem(self, selected: bool, proxy: OverlayItemProxy = None, widget: OverlayListWidgetItem = None):

        if widget is not None: self.itemSelected.emit(widget, selected)
        elif proxy is not None: 
            
            if selected: self.list.setCurrentItem(proxy.widget)
            else: self.list.setCurrentItem(None)

    def onCurrentItemChanged(self, current: OverlayListWidgetItem, previous: OverlayListWidgetItem):

        if previous is not None: self.selectItem(False, widget=previous)
        if current is not None: self.selectItem(True, widget=current)

class PropertyLineEdit(QLineEdit):
    
    def __init__(self, value = ''):

        super().__init__(value)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

class BrowseLineEdit(QLineEdit):
    
    browse = Signal(QEvent)

    def __init__(self, value = ''):

        super().__init__(value)
        self.setToolTip('Left-click to change the source. \nRight-click for more actions.')

    def mousePressEvent(self, event: QMouseEvent):

        if event.button() is Qt.MouseButton.LeftButton: self.browse.emit(event)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        
        contextMenu = QMenu()
        copy = contextMenu.addAction('Copy')

        copy.setShortcut('Ctrl+C')
        contextMenu.addSeparator()

        browse = contextMenu.addAction('Browse...')
        action = contextMenu.exec(self.mapToGlobal(event.pos()))

        if   action is browse: self.browse.emit(event)
        elif action is copy: QApplication.clipboard().setText(self.text())

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

        self.srcEdit.setReadOnly(True)

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
            self.srcEdit.browse.disconnect()
        
        except: pass

    def connectLineEdits(self):

        self.xEdit.editingFinished.connect(self.updateItemGraphics)
        self.yEdit.editingFinished.connect(self.updateItemGraphics)
        self.wEdit.editingFinished.connect(self.updateItemGraphics)
        self.hEdit.editingFinished.connect(self.updateItemGraphics)
        self.srcEdit.browse.connect(self.updateItemSource)

    def linkLineEdits(self):

        self.xEdit.setText(str(self.proxy.graphics.x()))
        self.yEdit.setText(str(self.proxy.graphics.y()))
        self.wEdit.setText(str(self.proxy.graphics.boundingRect().width()))
        self.hEdit.setText(str(self.proxy.graphics.boundingRect().height()))
        self.srcEdit.setText(self.proxy.source)

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

        self.proxy.graphics.updateRect(

            float(self.xEdit.text()),
            float(self.yEdit.text()),
            float(self.wEdit.text()),
            float(self.hEdit.text())
        )

    def updateItemSource(self, event: QEvent):

        if event is self.currentEvent: return 
        self.currentEvent = event

        fname, _ = QFileDialog.getOpenFileName(filter='All Images (*.jpg *.jpeg *.png *.gif)')
        self.srcEdit.setText(fname)
        self.proxy.source = fname
        self.proxy.graphics.updateImage(fname)

