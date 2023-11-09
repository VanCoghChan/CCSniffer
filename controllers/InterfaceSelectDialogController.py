import sys

import scapy.interfaces
from PyQt6.QtGui import QPixmap
from scapy.all import *
from PyQt6.QtCore import QObject, QThread, pyqtSlot, QSize, Qt
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel
from qt_material import apply_stylesheet
from scapy.all import *

from controllers.MainWindowController import MainWindowController
from models.GetInterfaceModel import GetInterfaceServer
from views.InterfaceSelectDialogView import InterfaceSelectDialog


class InterfaceSelectDialogController(QObject):
    def __init__(self):
        super(InterfaceSelectDialogController, self).__init__()
        self.mainWindow = MainWindowController()
        self.interfaces = scapy.interfaces.get_working_ifaces()
        self.interface_select_dialog = InterfaceSelectDialog()
        qlabels = self.interface_select_dialog.listWidget.findChildren(QLabel)
        self.status_labels, self.bytes_labels = qlabels[1::3], qlabels[2::3]
        self.interface_select_dialog.show()
        self.interface_select_dialog.listWidget.itemDoubleClicked.connect(self.selectInterfaceAndjump2MainWindow)
        # 获取网络流量线程
        self.bytes_flow_thread = QThread()
        self.bytes_flow_server = GetInterfaceServer()
        self.bytes_flow_server.moveToThread(self.bytes_flow_thread)
        self.bytes_flow_thread.started.connect(self.bytes_flow_server.run)
        self.bytes_flow_server.bytes_flow.connect(self.checkInterfaceStatus)
        self.bytes_flow_thread.start()

    @pyqtSlot(dict)
    def checkInterfaceStatus(self, interface_bytes_flow):
        # print(interface_bytes_flow)
        for idx, interface in zip(range(len(self.interfaces)), self.interfaces):
            current_bytes_flow = interface_bytes_flow.get(interface.name)
            if current_bytes_flow != (0, 0):
                statuspix = QPixmap("./resources/status_green.png")
                statuspix = statuspix.scaled(QSize(20, 20),
                                             Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation
                                             )
                self.status_labels[idx].setPixmap(statuspix)
            else:
                statuspix = QPixmap("./resources/status_red.png")
                statuspix = statuspix.scaled(QSize(20, 20),
                                             Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation
                                             )
                self.status_labels[idx].setPixmap(statuspix)
            sentKB = round(current_bytes_flow[0]/1000, 2) if current_bytes_flow[0] else 0
            recvKB = round(current_bytes_flow[1]/1000, 2) if current_bytes_flow[1] else 0
            self.bytes_labels[idx].setText(f"↑{sentKB} KB, ↓{recvKB} KB")

    def selectInterfaceAndjump2MainWindow(self):
        selectedItemIndex = self.interface_select_dialog.listWidget.currentRow()
        selectedInterface = self.interfaces[selectedItemIndex]
        # self.mainWindow = MainWindowController()
        self.mainWindow.main_window_view.interfaceLabel.setText(f"网卡：{selectedInterface.name}")
        self.interface_select_dialog.close()
        # 安全退出线程
        self.bytes_flow_server.isActive = False
        self.bytes_flow_thread.quit()
        self.mainWindow.main_window_view.show()


if __name__ == '__main__':
    os.chdir("../")
    app = QApplication(sys.argv)
    # dark_teal dark_amber
    apply_stylesheet(app, theme='dark_lightgreen.xml')
    w = InterfaceSelectDialogController()
    sys.exit(app.exec())
