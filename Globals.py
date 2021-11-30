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
    '''

class Colors:

    White = '#fff'
    MenuDark = '#1e1e1e'
    MenuMedium = '#252526'
    MenuLight = '#3c3c3c'
    GraySelected = '#505050'
    BlueSelected = '#252526'

class Math:

    def toCellSize(n):
        return int(str(n)[0]) * 10