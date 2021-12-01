from Graphics import ScreenPreviewItem
from Globals import Colors, Style

from PyQt6.QtCore import QEvent, QMargins, QPoint, Qt
from PyQt6.QtWidgets import QApplication, QFrame, QGraphicsScene, QGraphicsView, QLabel, QListWidget, QListWidgetItem, QMenu, QVBoxLayout, QWidget
from PyQt6.QtGui import QContextMenuEvent, QKeyEvent, QMouseEvent, QResizeEvent

class OverlayPreviewWidget(QFrame):

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
        self.drawTest()

    def eventFilter(self, source, e: QEvent) -> bool:

        if e.type() == QEvent.Type.MouseButtonPress:
            self.mousePressEvent(e)
        if e.type() == QEvent.Type.MouseButtonRelease:
            self.mouseReleaseEvent(e)
        if e.type() == QEvent.Type.MouseMove:
            self.mouseMoveEvent(e)

        return super().eventFilter(source, e)

    def resizeEvent(self, e: QResizeEvent):

        super().resizeEvent(e)
        self.view.setFixedSize(self.width(), self.height())

    def keyPressEvent(self, e: QKeyEvent) -> None:
        
        super().keyPressEvent(e)

        # Zoom
        if e.modifiers() is Qt.KeyboardModifier.ControlModifier:

            if e.key() == Qt.Key.Key_Equal: self.zoomIn()
            elif e.key() == Qt.Key.Key_Minus: self.zoomOut()

    def contextMenuEvent(self, e: QContextMenuEvent):
        
        super().contextMenuEvent(e)

        contextMenu = QMenu(self)

        zoomIn = contextMenu.addAction('Zoom In')
        zoomOut = contextMenu.addAction('Zoom Out')
        resetZoom = contextMenu.addAction('Fill Window')
        action = contextMenu.exec(self.mapToGlobal(e.pos()))
        
        if action is zoomIn: self.zoomIn()
        if action is zoomOut: self.zoomOut()
        if action is resetZoom: self.fitScreen()

    def mousePressEvent(self, e: QMouseEvent):
        
        super().mousePressEvent(e)

        if e.button() != Qt.MouseButton.MiddleButton: return 
        self._previousMousePosition = e.pos()
        self.isMoving = True

        application: QApplication = QApplication.instance()
        application.setOverrideCursor(Qt.CursorShape.OpenHandCursor)
        
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

    def drawTest(self):

        width = self.screen().size().width() // 2
        height = self.screen().size().height() // 2
        self.screenPreviewItem = ScreenPreviewItem(width, height)
        self.scene.addItem(self.screenPreviewItem)

    def zoomIn(self):

        self.view.scale(self.ZOOM_FACTOR, self.ZOOM_FACTOR)

    def zoomOut(self):

        self.view.scale(1 / self.ZOOM_FACTOR, 1 / self.ZOOM_FACTOR)

    def fitScreen(self):

        self.view.fitInView(self.screenPreviewItem.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

class OverlayItemsWidget(QWidget):

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
        newText = newMenu.addAction('Text')

        contextMenu.addSeparator()

        deleteItem = contextMenu.addAction('Delete')
        duplicateItem = contextMenu.addAction('Duplicate')
        renameItem = contextMenu.addAction('Rename')

        if self.list.currentItem() is None: 

            deleteItem.setVisible(False)
            duplicateItem.setVisible(False)
            renameItem.setVisible(False)

        action = contextMenu.exec(self.mapToGlobal(e.pos()))

        if   action is deleteItem: self.removeItem(self.list.currentItem())
        elif action is renameItem: self.list.editItem(self.list.currentItem())
        elif action is newImage: self.addItem(QListWidgetItem('Test'))

    def removeItem(self, item: QListWidgetItem) -> bool:

        return self.list.takeItem(self.list.indexFromItem(item).row()) is not None

    def addItem(self, item: QListWidgetItem):

        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.list.addItem(item)

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