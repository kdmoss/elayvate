from typing import Callable
from PySide6.QtGui import QAction

from Items import OverlayFinalGraphicsItem, OverlayPreviewGraphicsItem, OverlayListWidgetItem

class OverlayItem():

    name: str = ''
    source: str = ''
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    def __init__(self):

        super().__init__()

class CallableActionProxy:

    def __init__(self, action: QAction, callable: Callable):

        self.__action = action 
        self.__callable = callable

    def callable(self): 

        return self.__callable

    def action(self):

        return self.__action

class OverlayItemProxy():

    __listWidgetItem: OverlayListWidgetItem
    __previewGraphicsItem: OverlayPreviewGraphicsItem
    __finalGraphicsItem: OverlayFinalGraphicsItem

    def __init__(self):

        self.__listWidgetItem = None
        self.__previewGraphicsItem = None
        self.__finalGraphicsItem = None

    def listWidgetItem(self) -> OverlayListWidgetItem: 
        
        return self.__listWidgetItem

    def previewGraphicsItem(self) -> OverlayPreviewGraphicsItem:

        return self.__previewGraphicsItem

    def finalGraphicsItem(self) -> OverlayPreviewGraphicsItem:

        return self.__finalGraphicsItem

    def x(self) -> float:

        return self.__previewGraphicsItem.x()

    def y(self) -> float:

        return self.__previewGraphicsItem.y()

    def width(self) -> float:

        return self.__previewGraphicsItem.boundingRect().width()

    def height(self) -> float:

        return self.__previewGraphicsItem.boundingRect().height()

    def source(self) -> str:

        return self.__previewGraphicsItem.source()

    def setListWidgetItem(self, widget: OverlayListWidgetItem):

        self.__listWidgetItem = widget

    def setpreviewGraphicsItem(self, graphics: OverlayPreviewGraphicsItem):

        self.__previewGraphicsItem = graphics
        self.__finalGraphicsItem = OverlayFinalGraphicsItem(graphics)

    def setX(self, x: float):

        self.__previewGraphicsItem.setX(x)
        self.__finalGraphicsItem.setX(x)

    def setY(self, y: float):

        self.__previewGraphicsItem.setY(y)
        self.__finalGraphicsItem.setY(y)

    def setSource(self, source: str):

        self.__previewGraphicsItem.setSource(source)

    def setRect(self, x: float, y: float, width: float, height: float):

        self.__previewGraphicsItem.setRect(x, y, width, height)
