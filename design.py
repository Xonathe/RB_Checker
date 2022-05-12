from other import *
from functions import *
from PySide2.QtCore import QRect, QSize, Qt, QByteArray
from PySide2.QtGui import QFont, QIcon, QIntValidator, QPixmap
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from threading import Thread

stay = bool


def icon_from_base_64(base64):
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray.fromBase64(base64))
    icon = QIcon(pixmap)
    return icon


class Root(QWidget):
    def __init__(self):
        super().__init__()
        self.button_stop = QPushButton('STOP', self)
        self.button_refresh = QPushButton('REFRESH', self)
        self.button_start = QPushButton('START', self)
        self.button_test = QPushButton('TEST MESSAGE', self)
        self.label_status = QLabel('OFF', self)
        self.list_hwnd = QListWidget(self)
        self.init_ui()

    def init_ui(self):
        # Set Window
        self.setWindowTitle("RB Checker")
        self.setMinimumSize(QSize(250, 225))
        self.setMaximumSize(QSize(250, 225))
        icon = icon_from_base_64(image_base64)
        self.setWindowIcon(icon)

        # List
        self.list_hwnd.setGeometry(QRect(10, 40, 230, 55))

        # Labels
        self.label_status.setGeometry(QRect(10, 10, 230, 20))
        self.label_status.setStyleSheet('color: red')
        font = QFont()
        font.setPointSize(14)
        self.label_status.setFont(font)
        self.label_status.setAlignment(Qt.AlignCenter)

        # Buttons
        self.button_start.setGeometry(QRect(10, 100, 230, 25))
        self.button_start.clicked.connect(self.start)
        self.button_refresh.setGeometry(QRect(10, 130, 230, 25))
        self.button_refresh.clicked.connect(self.refresh)
        self.button_stop.setGeometry(QRect(10, 160, 230, 25))
        self.button_stop.clicked.connect(self.stop)
        self.button_stop.setEnabled(False)

        self.button_test.setGeometry(QRect(10, 190, 230, 25))
        self.button_test.clicked.connect(send_message)

    def start(self):
        global stay
        stay = True
        item = self.list_hwnd.currentItem()
        self.button_start.setEnabled(False)
        self.button_refresh.setEnabled(False)
        self.list_hwnd.setEnabled(False)
        self.button_stop.setEnabled(True)
        self.label_status.setText("ON")
        self.label_status.setStyleSheet('color: #32CD32')
        hwnd = int(item.text())
        Thread(target=mainloop, args=(hwnd,), daemon=True).start()

    def stop(self):
        global stay
        stay = False
        self.list_hwnd.setEnabled(True)
        self.button_start.setEnabled(True)
        self.button_refresh.setEnabled(True)
        self.button_stop.setEnabled(False)
        self.label_status.setText("OFF")
        self.label_status.setStyleSheet('color: red')

    def refresh(self):
        y = 10
        windows.clear()
        self.list_hwnd.clear()
        get_hwnd()
        for hwnd in windows:
            filename = get_name(hwnd)
            if filename == -1:
                return -1
            self.list_hwnd.insertItem(400, str(hwnd))
            pixmap = QPixmap(filename)
            self.label_picture = QLabel(self)
            self.label_picture.setPixmap(pixmap)
            self.label_picture.setGeometry(QRect(125, y, 65, 80))
            y += 18
            os.remove(filename)
        if self.list_hwnd.count() != 0:
            self.list_hwnd.setCurrentRow(0)
            self.button_start.setEnabled(True)
            self.list_hwnd.setEnabled(True)
        else:
            self.button_start.setEnabled(False)
            self.list_hwnd.setEnabled(False)

    def closeEvent(self, event):
        global stay
        stay = False
        event.accept()
