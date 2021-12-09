from typing import Dict
from PySide6.QtCore import QMargins, QPoint


class Style:

    QPushButton = '''

        QPushButton {

            background-color: gray;
            border: 0px;
        }

        QPushButton::hover {

            background-color: lightgray;
        }
    '''

    QApplication = '''

        QMenuBar {
            
            background-color: #3c3c3c;
            color: #fff;
        }

        QMenuBar::item {

            background-color: #3c3c3c;
            color: #fff;
        }

        QMenuBar::item::selected {

            background-color: #505050;
            color: #fff;
        }

        QMenu {

            background-color: #252526;
            color: #fff;
        }
        
        QMenu::item::selected {

            background-color: #094771;
            color: #fff;
        }

        QMenu::item::disabled {

            color: gray;
        }

        QSplitter::handle:horizontal,
        QSplitter::handle:vertical {

            background: #252526;
            height: 0px;
        }

        QSplitter::handle:pressed {

            background: #007fd4;
        }
    '''

    OverlayItemListWidget = '''

        QListView {

            outline: none;
            border: 0px; 
            background-color: #252526; 
            color: white;
        }

        QListView::item {

            color: #fff;
            height: 20px
        }

        QListView::item:hover {

            background: #2a2d2e;
        }

        QListView::item:selected,
        QListView::item:alternate {

            border: 1px solid #094771;
        }

        QListView::item:selected:!active {

            background: #094771;
        }

        QListView::item:selected:active {

            background: #094771;
        }        
    '''

    OverlayItemPropertiesWidget = '''

        QObject {

            background-color: #252526;
            height: 20px;
        }

        QLabel {

            color: #fff; 
            padding-left: 5px;
        }    

        QLineEdit {

            margin-right: 5px;
            border: 1px solid #505050;
            color: #fff;
        }

        QLineEdit:focus {

            border: 1px solid #094771;
        }
    '''

    OverlayItemBoxTitle = '''

        height: 30px;
        background-color: #505050; 
        color: white; 
        font-weight: bold; 
    '''

    # Constants
    NoMargins = QMargins(0, 0, 0, 0)
    SmallMargins = QMargins(5, 5, 5, 5)

class Colors:

    White = '#fff'
    MenuDark = '#1e1e1e'
    MenuMedium = '#252526'
    MenuLight = '#3c3c3c'
    GraySelected = '#505050'
    BlueSelected = '#094771'

class Math:

    def toCellSize(n):

        return int(str(n)[0]) * 10

    def gridSnap(x: int, y: int, cell: int):
        
        return QPoint(round(x / cell) * cell, round(y / cell) * cell)

    def clamp(n: int, floor: int, ceil: int):

        return max(floor, min(n, ceil))
