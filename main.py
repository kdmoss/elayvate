import sys

from PyQt6 import QtGui
import style 

from PyQt6.QtCore import QMimeData, QPoint, Qt
from PyQt6.QtWidgets import QApplication, QBoxLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QListView, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction, QDrag, QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent, QResizeEvent, QStandardItem, QStandardItemModel, QWindow

class PyCrossWindow(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        self._widget = QWidget(self)
        self._layout = QHBoxLayout(self._widget)
        self._width = self.screen().size().width() // 2
        self._height = self.screen().size().height() // 2

        self.setCentralWidget(self._widget)
        self.setWindowTitle('PyCross')
        self.createMenuBar()
        self.createItemsBox()
        self.createOverlayBox()
        self.setFixedSize(self._width, self._height)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        
        
    def createMenuBar(self):
        
        self.createFileMenu()
        self.createSettingsMenu()
        self.createHelpMenu()

    def createFileMenu(self):

        newAction = QAction('&New', self)
        openAction = QAction('&Open...', self)
        saveAction = QAction('&Save', self)
        saveAsAction = QAction('&Save As...', self)
        exitAction = QAction('&Exit', self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')

        saveAction.setShortcut('Ctrl+S')
        exitAction.setShortcut('Alt+F4')
        exitAction.triggered.connect(self.close)

        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

    def createSettingsMenu(self):
        
        preferencesAction = QAction('&Preferences...', self)
        hotkeyMapperAction = QAction('&Hotkey Mapper...', self)

        menuBar = self.menuBar()
        settingsMenu = menuBar.addMenu('&Settings')
        
        settingsMenu.addAction(preferencesAction)
        settingsMenu.addAction(hotkeyMapperAction)

    def createHelpMenu(self):

        aboutAction = QAction('&About...', self)
        donateAction = QAction('&Donate...', self)
        
        menuBar = self.menuBar()
        helpMenu = menuBar.addMenu('&Help')

        aboutAction.setShortcut('F1')
        helpMenu.addAction(aboutAction)
        helpMenu.addAction(donateAction)

    def createItemsBox(self):
        
        self.itemsFrame = ItemsFrame(self._widget)
        self._layout.addWidget(self.itemsFrame)

    def createOverlayBox(self):

        self.overlayFrame = OverlayFrame(self._widget)
        self._layout.addWidget(self.overlayFrame)

class DragFrame(QFrame):

    def __init__(self, parent: QWidget):

        super().__init__(parent)

    def mousePressEvent(self, e: QMouseEvent):

        super().mousePressEvent(e)
        if e.button() != Qt.MouseButton.LeftButton: return

        self._mousePressPosition = e.globalPosition().toPoint()
        self._mouseMovePosition = e.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, e: QMouseEvent):

        super().mouseReleaseEvent(e)
        if self._mousePressPosition is None: return 

        distance: QPoint = e.globalPosition().toPoint() - self._mousePressPosition
        if distance.manhattanLength() > 3:  e.ignore()

    def mouseMoveEvent(self, e: QMouseEvent):
        
        super().mouseMoveEvent(e)
        if e.buttons() != Qt.MouseButton.LeftButton: return

        currentPosition = self.mapToGlobal(self.pos())
        deltaPosition: QPoint = e.globalPosition().toPoint() - self._mouseMovePosition
        
        self.move(self.mapFromGlobal(currentPosition + deltaPosition))
        self._mouseMovePosition = e.globalPosition().toPoint()

class ItemsFrame(QWidget):

    def __init__(self, parent: QWidget):
    
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._parent = parent

        self.label = QLabel('Items')
        self.buttonFrame = PushButtonGroup()
        self.listView = QListView(self)
        self.listModel = QStandardItemModel(self.listView)

        self.listView.setModel(self.listModel)
        self.listModel.appendRow(QStandardItem('Test'))
        self._layout.addWidget(self.label)
        self._layout.addWidget(self.listView)
        self._layout.addWidget(self.buttonFrame)
        self.stylize()
    
    def stylize(self):

        self.setFixedSize(250, 500)
        # Label
        self.label.setStyleSheet('background-color: #3c3c3c; color: white; font-weight: bold')
        self.label.setFixedHeight(30)
        self.label.setContentsMargins(5, 5, 5, 5)

        # List
        self.listView.setStyleSheet('border: 0px; background-color: #252526; color: white')
        self.listView.setContentsMargins(5, 5, 5, 5)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

class PushButtonGroup(QFrame):

    def __init__(self):

        super().__init__()
        self._layout = QHBoxLayout(self)
        self.addButton = QPushButton('+')
        self.delButton = QPushButton('-')

        self.addButton.setFixedSize(30, 30)
        self.delButton.setFixedSize(30, 30)

        self._layout.addStretch()
        self._layout.addWidget(self.addButton)
        self._layout.addWidget(self.delButton)
        self._layout.setContentsMargins(5, 5, 5, 5)
        self.stylize()

    def stylize(self):
        self.setStyleSheet('background-color: #252526; color: white')
        self.addButton.setStyleSheet(style.QPushButton)
        self.delButton.setStyleSheet(style.QPushButton)

class OverlayFrame(QFrame):

    def __init__(self, parent: QWidget):

        super().__init__(parent)
        self._layout = QGridLayout(self)
        self._parent = parent
        self.setFixedSize
        (
            self.screen().size().width() // 2, 
            self.screen().size().height() // 2
        )

        self.test = DragFrame(self)
        self.test.setFixedSize(100, 100)
        self.setStyleSheet('background-color: #1e1e1e')
        self._layout.addWidget(self.test)

        
if __name__ == '__main__':

    app = QApplication([])
    window = PyCrossWindow()
    app.setStyleSheet(style.QApplication)
    window.show()
    sys.exit(app.exec())