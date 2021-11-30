from Graphics import ScreenPreviewItem
from Globals import Colors

from PyQt6.QtCore import QMargins, Qt
from PyQt6.QtWidgets import QFrame, QGraphicsScene, QGraphicsView, QLabel, QListWidget, QListWidgetItem, QMenu, QVBoxLayout, QWidget
from PyQt6.QtGui import QContextMenuEvent, QResizeEvent

class OverlayPreviewWidget(QFrame):

    def __init__(self, parent: QWidget):

        super().__init__(parent)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)

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
        self.list = QListWidget()
        
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

        self.setFixedWidth(self.WIDTH)
        
        # Label
        self.label.setStyleSheet('background-color: #333333; color: white; font-weight: bold')
        self.label.setFixedHeight(self.LABEL_HEIGHT)
        self.label.setContentsMargins(self.CHILD_MARGINS)

        # List
        self.list.setStyleSheet('border: 0px; background-color: #252526; color: white')
        self.list.setContentsMargins(self.CHILD_MARGINS)
        self.layout().setContentsMargins(self.MARGINS)
        self.layout().setSpacing(self.SPACING)