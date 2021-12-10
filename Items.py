
from Globals import Colors, Math

from PySide6.QtGui import QColor, QFocusEvent, QKeyEvent
from PySide6.QtWidgets import QApplication, QGraphicsItem, QGraphicsItemGroup, QGraphicsLineItem, QGraphicsRectItem, QGraphicsSceneContextMenuEvent, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QListWidgetItem, QMenu, QWidget
from PySide6.QtCore import QPoint, QRectF, Qt

class OverlayListWidgetItem(QListWidgetItem):

    def __init__(self, parent: QWidget, text):

        super().__init__(text)
        self.parent = parent

class OverlayGraphicsItem(QGraphicsRectItem):

    def __init__(self, parent: QWidget, x: int, y: int, width: int, height: int):

        super().__init__(x, y, width, height)
        self.setAcceptHoverEvents(True)
        self.setBrush(Qt.GlobalColor.white)
        self.setPen(Qt.PenStyle.NoPen)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsRectItem.ItemSendsScenePositionChanges, True)
        self.parent = parent
        self.isDragging = False

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):

        if change == QGraphicsItem.ItemSelectedChange:

            self.parent.selectItem(value, graphics=self)

        return super().itemChange(change, value)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        
        QApplication.instance().setOverrideCursor(Qt.CursorShape.OpenHandCursor)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        
        QApplication.instance().restoreOverrideCursor()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):

        if event.button() is Qt.MouseButton.LeftButton:

            self.isDragging = True
            QApplication.instance().setOverrideCursor(Qt.CursorShape.ClosedHandCursor)
        else:

            self.isDragging = False
            QApplication.instance().restoreOverrideCursor()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):

        if event.button() is Qt.MouseButton.LeftButton:

            self.isDragging = False
            self.setPos(Math.gridSnap(self.x(), self.y(), self.parent.cellSize))
            self.parent.updateItem(graphics=self)

        QApplication.instance().setOverrideCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def updateRect(self, x, y, width, height):

        pos = Math.gridSnap(x, y, self.parent.cellSize)
        size = Math.gridSnap(width, height, self.parent.cellSize)

        self.setRect(0, 0, size.x(), size.y())
        self.setPos(pos.x(), pos.y())
        self.parent.updateItem(graphics=self)
        
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):

        if not self.isDragging: return 

        goalX = event.scenePos().x() - event.lastScenePos().x() + self.scenePos().x()
        goalY = event.scenePos().y() - event.lastScenePos().y() + self.scenePos().y()

        self.setX(Math.clamp(goalX, 0, self.parent.screenPreviewItem.width - self.rect().width()))
        self.setY(Math.clamp(goalY, 0, self.parent.screenPreviewItem.height - self.rect().height()))
        super().mouseMoveEvent(event)

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent):

        contextMenu = QMenu(self.parent)
        deleteItem = contextMenu.addAction('Delete')
        renameItem = contextMenu.addAction('Rename')

        deleteItem.setShortcut('Delete')
        action = contextMenu.exec(event.screenPos())
        
        if action is deleteItem: self.parent.deleteItem(graphics=self)

    def screenClamp(self, x, y, w, h) -> QPoint:

        return QPoint(
            
            Math.clamp(x, 0, self.parent.screenPreviewItem.width - w), 
            Math.clamp(y, 0, self.parent.screenPreviewItem.height - h)
        )

class ScreenPreviewItem(QGraphicsItemGroup):

    def __init__(self, width: int, height: int, cellSize: int):

        super().__init__()
        
        self.width = width
        self.height = height 
        self.cellSize = cellSize
        screen = QGraphicsRectItem(0, 0, width, height)
        screen.setBrush(QColor(Colors.GraySelected))
        screen.setPen(QColor(Colors.GraySelected))
        
        self.addToGroup(screen)
        self.drawGrid()

    def drawGrid(self):

        # Vertical
        for i in range(1, self.width // self.cellSize):

            x = i * self.cellSize
            mid = self.width // self.cellSize // 2

            line = QGraphicsLineItem(x, 0, x, self.height)    
            if i == mid: line = QGraphicsLineItem(x, -self.cellSize, x, self.height + self.cellSize) 
            else: line.setOpacity(0.2)

            line.setPen(QColor(Colors.White))
            self.addToGroup(line)

        # Horizontal
        for i in range(1, self.height // self.cellSize):

            y = i * self.cellSize
            mid = self.height // self.cellSize // 2

            line = QGraphicsLineItem(0, y, self.width, y)
            if i == mid: line = QGraphicsLineItem(-self.cellSize, y, self.width + self.cellSize, y)
            else: line.setOpacity(0.2)

            line.setPen(QColor(Colors.White))
            self.addToGroup(line)