
from Globals import Colors, Math
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QGraphicsItemGroup, QGraphicsLineItem, QGraphicsRectItem, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent
from PySide6.QtCore import Qt

class ImageItem(QGraphicsRectItem):

    def __init__(self, x: int, y: int, width: int, height: int, cellSize: int):

        super().__init__(x, y, width, height)
        self.setAcceptHoverEvents(True)
        self.setBrush(Qt.GlobalColor.blue)
        self.cellSize = cellSize

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        
        super().hoverEnterEvent(event)
        application: QApplication = QApplication.instance()
        application.setOverrideCursor(Qt.CursorShape.OpenHandCursor)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        
        super().hoverEnterEvent(event)
        application: QApplication = QApplication.instance()
        application.restoreOverrideCursor()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):

        pass

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):

        self.setPos(
            Math.gridSnap(self.x(), self.y(), self.cellSize)
        )

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):

        super().mouseMoveEvent(event)
        self.setX(event.scenePos().x() - event.lastScenePos().x() + self.scenePos().x())
        self.setY(event.scenePos().y() - event.lastScenePos().y() + self.scenePos().y())

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