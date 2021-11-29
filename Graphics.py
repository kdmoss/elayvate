
from Globals import Colors
from PyQt6.QtGui import QColor, QMouseEvent, QPen
from PyQt6.QtWidgets import QApplication, QGraphicsItem, QGraphicsItemGroup, QGraphicsLineItem, QGraphicsRectItem, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QLineEdit, QMainWindow
from PyQt6.QtCore import Qt

class ImageItem(QGraphicsRectItem):

    def __init__(self):

        super().__init__(0, 0, 100, 100)
        self.setAcceptHoverEvents(True)
        self.setBrush(Qt.GlobalColor.blue)

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

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):

        super().mouseMoveEvent(event)
        print('here')

class ScreenPreviewItem(QGraphicsItemGroup):

    def __init__(self, width, height):

        super().__init__()
        
        self.width = width
        self.height = height 
        self.cellSize = (self.width + self.height) // 100

        print(self.cellSize)
        screen = QGraphicsRectItem(0, 0, width, height)
        screen.setBrush(QColor(Colors.GraySelected))
        self.addToGroup(screen)
        self.drawGrid()

    def drawGrid(self):

        for i in range(1, self.width // self.cellSize):

            x = i * self.cellSize
            mid = self.width // self.cellSize // 2

            line = QGraphicsLineItem(x, 0, x, self.height)    
            if i == mid: line = QGraphicsLineItem(x, -self.cellSize, x, self.height + self.cellSize) 
            else: line.setOpacity(0.2)

            line.setPen(QColor(Colors.White))
            self.addToGroup(line)

        for i in range(1, self.height // self.cellSize):

            y = i * self.cellSize
            mid = self.height // self.cellSize // 2

            line = QGraphicsLineItem(0, y, self.width, y)
            if i == mid: line = QGraphicsLineItem(-self.cellSize, y, self.width + self.cellSize, y)
            else: line.setOpacity(0.2)

            line.setPen(QColor(Colors.White))
            self.addToGroup(line)