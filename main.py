import sys
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.FramelessWindowHint  |
            QtCore.Qt.WindowType.WindowSystemMenuHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint
        )
        
        self.button = QPushButton("Click me!")
        self.text = QLabel("Hello World", alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout = QVBoxLayout(self)

        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.button.clicked.connect(self.close)

if __name__ == "__main__":
    app = QApplication([])
    widget = MyWidget()

    widget.show()
    sys.exit(app.exec())