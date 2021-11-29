from Graphics import ScreenPreviewItem
from Globals import Colors

from PyQt6.QtCore import QMargins, Qt
from PyQt6.QtWidgets import QFrame, QGraphicsLineItem, QGraphicsScene, QGraphicsView, QLabel, QListView, QVBoxLayout, QWidget
from PyQt6.QtGui import QBrush, QPen, QResizeEvent, QStandardItem, QStandardItemModel

class OverlayPreviewWidget(QFrame):

    def __init__(self, parent: QWidget):

        super().__init__(parent)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.magnification = 0

        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setFrameShape(QFrame.Shape.NoFrame)

        self.view.setFixedSize(self.width(), self.height())
        self.setStyleSheet('background: {}'.format(Colors.MenuDark))
        self.drawTest()

    def drawTest(self):

        width = self.screen().size().width() // 2
        height = self.screen().size().height() // 2
        self.scene.addItem(ScreenPreviewItem(width, height))

    def resizeEvent(self, e: QResizeEvent):

        super().resizeEvent(e)
        self.view.setFixedSize(self.width(), self.height())

class OverlayItemsWidget(QWidget):

    # Constants
    WIDTH = 200
    MARGINS = QMargins(0, 0, 0, 0)
    SPACING = 0

    # Children Constants
    LABEL_HEIGHT = 30
    CHILD_MARGINS = QMargins(5, 5, 5, 5)

    def __init__(self, parent: QWidget):
    
        super().__init__(parent)
        QVBoxLayout(self)

        self.label = QLabel('Items')
        self.listView = QListView(self)
        self.listModel = QStandardItemModel(self.listView)

        self.listView.setModel(self.listModel)
        self.listModel.appendRow(QStandardItem('Test'))
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.listView)
        self.stylize()
    
    def stylize(self):

        self.setFixedWidth(self.WIDTH)
        
        # Label
        self.label.setStyleSheet('background-color: #333333; color: white; font-weight: bold')
        self.label.setFixedHeight(self.LABEL_HEIGHT)
        self.label.setContentsMargins(self.CHILD_MARGINS)

        # List
        self.listView.setStyleSheet('border: 0px; background-color: #252526; color: white')
        self.listView.setContentsMargins(self.CHILD_MARGINS)
        self.layout().setContentsMargins(self.MARGINS)
        self.layout().setSpacing(self.SPACING)

    def resizeEvent(self, e: QResizeEvent):
        
        super().resizeEvent(e)
        self.move(0, 0)