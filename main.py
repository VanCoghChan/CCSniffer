import sys

from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from controllers.InterfaceSelectDialogController import InterfaceSelectDialogController
from controllers.MainWindowController import MainWindowController

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # dark_teal dark_amber dark_lightgreen
    apply_stylesheet(app, theme='dark_lightgreen.xml')
    wid = InterfaceSelectDialogController()
    sys.exit(app.exec())
