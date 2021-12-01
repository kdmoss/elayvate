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

        QSplitter::handle:horizontal {

            background: #252526;
        }

        QSplitter::handle:pressed,
        QSplitter:hover {

            background: #007fd4;
        }
    '''

    OverlayItemsWidget = '''

        QLabel {

            background-color: #252526; 
            color: white; 
            font-weight: bold; 
            border-bottom: 1px solid #333333;
        }

        QListView {

            outline: none;
            border: 0px; 
            background-color: #252526; 
            color: white;
        }

        QListView::item {

            color: #fff;
        }

        QListView::item:hover {

            background: #2a2d2e;
        }

        QListView::item:selected,
        QListView::item:alternate {

            border: 1px solid #007fd4;
        }

        QListView::item:selected:!active {

            background: #094771;
        }

        QListView::item:selected:active {

            background: #094771;
        }        
    '''

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