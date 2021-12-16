from PySide6.QtCore import QEvent, Signal
from PySide6.QtGui import QAction, QContextMenuEvent, QKeyEvent
from Widgets import ClickableLineEdit
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QWidget 


class HotkeyLineEdit(ClickableLineEdit):
    
    editing = Signal(QEvent)

    def __init__(self, value = ''):

        super().__init__(value)
        self.addAction(QAction('Change...'), self.clicked.emit)
        self.setToolTip('Left-click to record new hot-key. \nRight-click for more actions.')

class HotkeyMapperDialog(QDialog):

    def __init__(self, parent: QWidget):

        super().__init__(parent)
        self.initUI()
        
    def initUI(self):

        QGridLayout(self)

        self.reading = False
        self.renderHotkey = HotkeyLineEdit('None')
        self.renderHotkey.clicked.connect(self.updateRender)
        self.setWindowTitle('Hotkey Mapper')
        self.layout().addWidget(QLabel('Render:'),  0, 0)
        self.layout().addWidget(self.renderHotkey,  0, 1)

    def updateRender(self):

        self.reading = True 

    def keyPressEvent(self, event: QKeyEvent) -> None:
        
        if not self.reading: return 

        self.renderHotkey.setText(event.text())

        
