from Graphics import ImageItem, ScreenPreviewItem
from Globals import Colors, Math, Style

from PySide6.QtCore import QEvent, QMargins, QPoint, Qt, Signal
from PySide6.QtWidgets import QApplication, QFrame, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QLabel, QListWidget, QListWidgetItem, QMenu, QVBoxLayout, QWidget
from PySide6.QtGui import QContextMenuEvent, QKeyEvent, QMouseEvent, QResizeEvent

from Models import OverlayItem

class OverlayWidget(QWidget):

    # Signals
    itemAdded = Signal(object)

    def __init__(self, parent: QWidget):

        super().__init__(parent)

class OverlayPreviewWidget(OverlayWidget):

    # Constants
    ZOOM_FACTOR = 1.25

    def __init__(self, parent: QWidget):

        super().__init__(parent)

        self.isMoving = False
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)

        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setFrameShape(QFrame.Shape.NoFrame)

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
        if e.modifiers() is Qt.KeyboardModifier.ControlModifier:

            if   e.key() == Qt.Key.Key_Equal: self.zoomIn()
            elif e.key() == Qt.Key.Key_Minus: self.zoomOut()

    def contextMenuEvent(self, e: QContextMenuEvent):
        
        super().contextMenuEvent(e)

        contextMenu = QMenu(self)
        newMenu = contextMenu.addMenu('New')
        viewMenu = contextMenu.addMenu('View')

        newImage = newMenu.addAction('Image')
        zoomIn = viewMenu.addAction('Zoom In')
        zoomOut = viewMenu.addAction('Zoom Out')
        fillWindow = viewMenu.addAction('Fill Window')
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
        self.scene.addItem(self.screenPreviewItem)

    def addItem(self, item: OverlayItem = None, position: QPoint = None):

        preview = ImageItem(0, 0, 100, 100, self.cellSize)

        if position is not None: 

            position = self.view.mapToScene(position)
            position = Math.gridSnap(position.x(), position.y(), self.cellSize)
            preview = ImageItem(position.x(), position.y(), 100, 100, self.cellSize)

        if item is not None: preview = ImageItem(item.x, item.y, item.width, item.height, self.cellSize)

        preview.setBrush(Qt.GlobalColor.white)
        self.scene.addItem(preview)
        if item is None: self.itemAdded.emit(preview)

    def zoomIn(self):

        self.view.scale(self.ZOOM_FACTOR, self.ZOOM_FACTOR)

    def zoomOut(self):

        self.view.scale(1 / self.ZOOM_FACTOR, 1 / self.ZOOM_FACTOR)

    def fitScreen(self):

        self.view.fitInView(

            self.screenPreviewItem.boundingRect(), 
            Qt.AspectRatioMode.KeepAspectRatio
        )

class OverlayItemsWidget(OverlayWidget):
        
    # Constants
    MARGINS = QMargins(0, 0, 0, 0)
    SPACING = 0

    # Children Constants
    LABEL_HEIGHT = 30
    CHILD_MARGINS = QMargins(5, 5, 5, 5)

    def __init__(self, parent: QWidget):
    
        super().__init__(parent)
        QVBoxLayout(self)

        self.label = QLabel('Items')
        self.list = QListWidget()
        
        seperator = QFrame()
        seperator.setFrameShape(QFrame.Shape.HLine)
        seperator.setFrameShadow(QFrame.Shadow.Sunken)

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

        if self.list.currentItem() is None: 

            deleteItem.setVisible(False)
            renameItem.setVisible(False)

        action = contextMenu.exec(self.mapToGlobal(e.pos()))

        if action is newImage: self.addItem()

    def resizeEvent(self, e: QResizeEvent):
        
        super().resizeEvent(e)
        self.move(0, 0)

    def stylize(self):

        self.setStyleSheet(Style.OverlayItemsWidget)

        # Label
        self.label.setFixedHeight(self.LABEL_HEIGHT)
        self.label.setContentsMargins(self.CHILD_MARGINS)

        # List
        self.list.setContentsMargins(self.CHILD_MARGINS)
        self.layout().setContentsMargins(self.MARGINS)
        self.layout().setSpacing(self.SPACING)

    def addItem(self, item: OverlayItem = None):

        widget = QListWidgetItem('Image')
        if item is not None: widget = QListWidgetItem(item.name)

        self.list.addItem(widget)
        if item is None: self.itemAdded.emit(widget)