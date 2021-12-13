from PySide6.QtWidgets import QGraphicsRectItem, QListWidgetItem

from Items import OverlayGraphicsItem, OverlayListWidgetItem

class OverlayItem():

    name: str = 'Image'
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    def __init__(self):

        super().__init__()

class OverlayItemProxy():

    widget: OverlayListWidgetItem
    graphics: OverlayGraphicsItem

    def __init__(self):

        self.selected = False
        self.widget = None
        self.graphics = None
        self.source = ''