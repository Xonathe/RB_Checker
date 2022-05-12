# -*- coding: utf-8 -*-
import sys
from design import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    root = Root()
    root.refresh()
    root.show()
    sys.exit(app.exec_())

# pyinstaller main.py -D -i icon.ico --noconsole --name "Golkonda" --version-file version.txt
# --add-data C:\Users\Xonathe\PycharmProjects\Asterios_AutoHeal_Bot\toEXE;.


