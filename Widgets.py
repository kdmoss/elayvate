from Items import OverlayGraphicsItem, OverlayListWidgetItem, ScreenPreviewItem
from Globals import Colors, Math, Style
from Models import OverlayItem, OverlayItemProxy

from PySide6.QtCore import QEvent, QMargins, QPoint, QRect, QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGridLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMenu, QPushButton, QSplitter, QVBoxLayout, QWidget
from PySide6.QtGui import QContextMenuEvent, QKeyEvent, QMouseEvent, QResizeEvent, QTextBlock

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
        
        if action is newImage: self.addItem(position=e.pos())
        if action is zoomIn: self.zoomIn()
        if action is zoomOut: self.zoomOut()
        if action is fillWindow: self.fitScreen()

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

        width = self.screen().size().width() // 2
        height = self.screen().size().height() // 2

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

        preview = OverlayGraphicsItem(self, 0, 0, self.cellSize * 4, self.cellSize * 4)

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

        if action is newImage: self.addItem()
        if action is deleteItem: self.deleteItem(widget=self.list.currentItem())

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
            else: self.list.clearSelection()

    def onCurrentItemChanged(self, current: OverlayListWidgetItem, previous: OverlayListWidgetItem):

        if previous is not None: self.selectItem(False, widget=previous)
        if current is not None: self.selectItem(True, widget=current)
        
class OverlayItemPropertiesWidget(OverlayWidget):

    def __init__(self, parent: QWidget):

        super().__init__(parent)
        QGridLayout(self)

        self.item = None 
        self.label = QLabel('Properties')
        self.xEdit = QLineEdit()
        self.yEdit = QLineEdit()
        self.wEdit = QLineEdit()
        self.hEdit = QLineEdit()
        self.sourceEdit = QLineEdit()

        self.sourceEdit.setReadOnly(True)

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
        self.layout().addWidget(self.sourceEdit,   3, 1, 1, 3)
        self.layout().setRowStretch(4, 1)
        self.stylize()

    def openFileBrowser(self, _):

        fname, _ = QFileDialog.getOpenFileName(filter='Images (*.jpg, *.png)')
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

    def blockAllSignals(self, block: bool):

        self.xEdit.blockSignals(block)
        self.yEdit.blockSignals(block)
        self.wEdit.blockSignals(block)
        self.yEdit.blockSignals(block)

    def setItem(self, proxy: OverlayItemProxy):

        self.item = proxy 
        if proxy is None: 
            
            self.xEdit.setText('')
            self.yEdit.setText('')
            self.wEdit.setText('')
            self.hEdit.setText('')
            self.sourceEdit.setText('')

            self.xEdit.textChanged.disconnect()
            self.yEdit.textChanged.disconnect()
            self.wEdit.textChanged.disconnect()
            self.hEdit.textChanged.disconnect()
            return 

        self.blockAllSignals(True)
        self.xEdit.setText(str(proxy.graphics.x()))
        self.yEdit.setText(str(proxy.graphics.y()))
        self.wEdit.setText(str(proxy.graphics.boundingRect().width()))
        self.hEdit.setText(str(proxy.graphics.boundingRect().height()))
        self.sourceEdit.setText(proxy.widget.text())
        self.blockAllSignals(False)

        self.xEdit.textChanged.connect(self.updateItem)
        self.yEdit.textChanged.connect(self.updateItem)
        self.wEdit.textChanged.connect(self.updateItem)
        self.hEdit.textChanged.connect(self.updateItem)

    def updateItem(self):

        if self.item is None: return


        self.item.graphics.setRect(QRect(

            float(self.xEdit.text()),
            float(self.yEdit.text()),
            float(self.wEdit.text()),
            float(self.hEdit.text())
        ))


