from Items import OverlayGraphicsItem, OverlayListWidgetItem, ScreenPreviewItem
from Globals import Colors, Math, Style
from Models import OverlayItem, OverlayItemProxy

from PySide6.QtCore import QEvent, QMargins, QPoint, QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QFileDialog, QFrame, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGridLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMenu, QPushButton, QVBoxLayout, QWidget
from PySide6.QtGui import QContextMenuEvent, QKeyEvent, QMouseEvent, QResizeEvent, QTextBlock

class OverlayWidget(QWidget):

    # Signals
    itemAdded = Signal(object)
    itemDeleted = Signal(object)
    itemRenamed = Signal(object)

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

        self.scene.addItem(preview)
        if proxy is None: self.itemAdded.emit(preview)
        else: proxy.graphics = preview

    def deleteItem(self, proxy: OverlayItemProxy = None, graphics: QGraphicsRectItem = None):

        if graphics is not None: 
            
            self.scene.removeItem(graphics)
            self.itemDeleted.emit(graphics)
            return 

        if proxy is not None: self.scene.removeItem(proxy.graphics)

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
        self.props = OverlayItemPropertiesWidget(self)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.list)
        self.layout().addWidget(self.props)
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
        if action is deleteItem: self.deleteItem(widget=self.list.currentItem())

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

    def addItem(self, proxy: OverlayItemProxy = None):

        widget = OverlayListWidgetItem(self, 'Image')
        self.list.addItem(widget)

        if proxy is None: self.itemAdded.emit(widget)
        else: proxy.widget = widget

    def deleteItem(self, proxy: OverlayItemProxy = None, widget: OverlayListWidgetItem = None):

        if proxy is not None: self.list.takeItem(self.list.row(proxy.widget))
        elif widget is not None: self.itemDeleted.emit(self.list.takeItem(self.list.row(widget)))

class OverlayItemPropertiesWidget(OverlayWidget):

    # Constants
    MARGINS = QMargins(0, 0, 0, 0)
    SPACING = 0

    # Children Constants
    LABEL_HEIGHT = 30
    CHILD_MARGINS = QMargins(5, 5, 5, 5)

    def __init__(self, parent: QWidget):

        super().__init__(parent)
        QGridLayout(self)

        self.label = QLabel('Properties')
        self.xEdit = QLineEdit()
        self.yEdit = QLineEdit()
        self.wEdit = QLineEdit()
        self.hEdit = QLineEdit()
        self.sourceEdit = QPushButton()

        self.sourceEdit.clicked.connect(self.openFileBrowser)

        self.layout().addWidget(self.label, 0, 0, 1, 4)
        self.layout().addWidget(QLabel('X:'), 1, 0)
        self.layout().addWidget(self.xEdit, 1, 1)
        self.layout().addWidget(QLabel('Y:'), 1, 2)
        self.layout().addWidget(self.yEdit, 1, 3)
        self.layout().addWidget(QLabel('W:'), 2, 0)
        self.layout().addWidget(self.wEdit, 2, 1)
        self.layout().addWidget(QLabel('H:'), 2, 2)
        self.layout().addWidget(self.hEdit, 2, 3)
        self.layout().addWidget(QLabel('Source:'), 3, 0, 1, 1)
        self.layout().addWidget(self.sourceEdit, 3, 1, 1, 3)

    def openFileBrowser(self, _):

        fname, _ = QFileDialog.getOpenFileName(filter='Images (*.jpg, *.png)')
        self.sourceEdit.setText(fname)

    def stylize(self):

        self.setStyleSheet(Style.OverlayItemsWidget)

        # Label
        self.label.setFixedHeight(self.LABEL_HEIGHT)
        self.label.setContentsMargins(self.CHILD_MARGINS)

