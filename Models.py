from PyQt6.QtCore import QModelIndex
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QListView
from PyQt6.sip import delete

from Graphics import ImageItem

class OverlayItem(QStandardItem):

    def __init__(self):
        super().__init__()

class OverlayItemsListModel(QStandardItemModel):

    def __init__(self, list: QListView):
        super().__init__(list)

    def removeRow(self, item: QModelIndex) -> bool:
        return super().removeRow(item.row())