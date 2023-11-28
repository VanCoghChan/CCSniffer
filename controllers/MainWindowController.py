import scapy.layers.l2
import scapy.interfaces
import scapy.arch.windows
from PyQt6.QtCore import QThread, pyqtSlot, QObject
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog, QLabel, QTreeWidget, QTreeWidgetItem, \
    QTextBrowser, QTextEdit, QWidget, QHBoxLayout
from scapy.all import *
from scapy.interfaces import NetworkInterface

from custom.packetAnalyser import getAllLayersDetail
from models.CatchModel import CatchServer
from models.OpenFileModel import OpenFileServer
from views.MainWindowView import MainWindow
from custom.style import save_types


# 必须继承Qt的一个基类QObject，否则无法使用@pyqtSlot进行通信
class MainWindowController(QObject):
    def __init__(self):
        super().__init__()
        self.main_window_view = MainWindow()
        # self.main_window_view.show()
        # 设置网络设备列表
        self.inter_faces = scapy.interfaces.get_working_ifaces()
        # 设置包数据暂存变量
        self.stored_packets = list()
        # 每次数据填入表格时的基准时间
        self.base_time = 0
        # 创建服务和对应的线程
        # 创建线程时，需要给线程变量添加self标识，否则线程将会异常，甚至无法正常启动线程
        # 初步猜测应该是因为没有self标识，创建的就只是局部变量，而不是类的实例属性，无法跨线程使用。
        self.catch_thread = QThread()
        self.open_file_thread = QThread()
        self.catch_server = CatchServer()
        # self.open_file_server = OpenFileServer()
        # 将服务绑定至线程
        self.catch_server.moveToThread(self.catch_thread)
        self.catch_thread.started.connect(self.catch_server.run)
        self.catch_thread.start()
        # self.open_file_server.moveToThread(self.open_file_thread)
        # self.open_file_thread.started.connect(self.open_file_server.run)
        # self.open_file_thread.start()
        # 设置的信号接受方
        self.catch_server.current_paket.connect(self.storeTempCapturedPackets)
        self.catch_server.current_packet_info.connect(self.captureAppendTable)
        self.catch_server.packet_number.connect(self.updateStatusBar)
        # self.open_file_server.current_packet_info.connect(self.openFileAppendTable)
        # self.open_file_server.current_paket.connect()
        # 绑定MainWindow中的功能绑定
        self.main_window_view.closeButton.clicked.connect(self.safeQuit)
        self.main_window_view.minButton.clicked.connect(self.main_window_view.showMinimized)
        self.main_window_view.catchButton.clicked.connect(self.doCapture)
        self.main_window_view.pauseButton.clicked.connect(self.doPause)
        self.main_window_view.restartButton.clicked.connect(self.doRestart)
        self.main_window_view.openFileButton.clicked.connect(self.openFile)
        self.main_window_view.jump2preButton.clicked.connect(self.previousRow)
        self.main_window_view.jump2nextButton.clicked.connect(self.nextRow)
        self.main_window_view.jump2topButton.clicked.connect(self.topRow)
        self.main_window_view.jump2tailButton.clicked.connect(self.tailRow)
        self.main_window_view.tableWidget.cellClicked.connect(self.showPacketDetail)
        self.main_window_view.tableWidget.cellClicked.connect(self.showPacketFrame)
        # 设置打开文件按钮不可用
        self.main_window_view.openFileButton.setDisabled(True)

    @pyqtSlot(int)
    def updateStatusBar(self, packetNum: int) -> None:
        """
        更新程序状态信息至statusbar
        :rtype: None
        """
        self.main_window_view.statusBar.showMessage(f"分组:{packetNum}   ·   已显示:{packetNum}")

    @pyqtSlot(tuple)
    def captureAppendTable(self, packetInfo: list) -> None:
        """
        用于接受self.catch_server返回的包数据并显示到table
        :rtype: None
        :param packetInfo: 从self.catch_server传过来的数据
        """
        row_count = self.main_window_view.tableWidget.rowCount()
        self.main_window_view.tableWidget.insertRow(row_count)
        if row_count == 0:
            self.base_time = packetInfo[1]
        for idx in range(7):
            if idx == 1:
                val = str(round(packetInfo[idx] - self.base_time, 6))
                item = QTableWidgetItem(val)

            else:
                val = str(packetInfo[idx])
                item = QTableWidgetItem(val)
            item.setToolTip(val)
            self.main_window_view.tableWidget.setItem(row_count, idx, item)
        # self.main_window_view.tableWidget.scrollToBottom()

    @pyqtSlot(tuple)
    def openFileAppendTable(self, packetInfo: tuple) -> None:
        """
        用于接受open_file_server返回的包数据并显示到table
        :rtype: None
        :param packetInfo: 从open_file_server传过来的数据
        """
        row_count = self.main_window_view.tableWidget.rowCount()
        self.main_window_view.tableWidget.insertRow(row_count)
        for idx in range(7):
            item = QTableWidgetItem(str(packetInfo[idx]))
            self.main_window_view.tableWidget.setItem(row_count, idx, item)
        self.main_window_view.tableWidget.scrollToBottom()

    @pyqtSlot(scapy.layers.l2.Ether)
    def storeTempCapturedPackets(self, pkt: scapy.layers.l2.Ether) -> None:
        """
        暂存已捕获的包数据
        :param pkt: 由catch_server捕获并返回的数据包
        :rtype: None
        """
        self.stored_packets.append(pkt)

    @pyqtSlot(scapy.layers.l2.Ether)
    def storeTempOpenedPackets(self, pkt: scapy.layers.l2.Ether) -> None:
        """
        暂存从文件中读取的包数据
        :param pkt: 由open_file_server捕获并返回的数据包
        :rtype: None
        """
        self.stored_packets.append(pkt)

    def getCurrentInterface(self) -> NetworkInterface | list[NetworkInterface]:
        """
        获取当前选中的网卡
        :rtype: scapy.arch.windows.NetworkInterface_Win
        """
        labeltext = self.main_window_view.interfaceLabel.text().split("：")[1]
        for interface in self.inter_faces:
            if interface.name == labeltext:
                return interface
        # return self.inter_faces[self.main_window_view.interfaceComboBox.currentIndex()]

    def doCapture(self) -> None:
        """
        开始捕获
        :rtype: None
        """
        # 设置开始捕获按钮不可用，并且设置暂停和重新捕获按钮可用
        self.main_window_view.catchButton.setDisabled(True)
        self.main_window_view.pauseButton.setEnabled(True)
        self.main_window_view.restartButton.setEnabled(True)
        self.main_window_view.openFileButton.setDisabled(True)
        # 获取当前网卡
        interface = self.getCurrentInterface()
        # 如果表格中有数据则触发保存选项
        if self.main_window_view.tableWidget.rowCount():
            save_status = self.doUnsaved()  # 获取保存状态
            if save_status >= 0:
                if save_status:  # 如果成功保存
                    self.doRestart()
                else:  # 保存失败（中断）
                    self.doPause()
        # 如果表格中没有数据则执行捕获
        else:
            if not self.catch_server.isActive:
                self.catch_server.interFace = interface
                self.catch_server.isActive = True

    def doPause(self) -> None:
        """
        终止捕获
        :rtype: None
        """
        # 设置暂停按钮和重新捕获按钮不可用，并且设置开始捕获按钮可用
        self.main_window_view.catchButton.setEnabled(True)
        self.main_window_view.pauseButton.setDisabled(True)
        self.main_window_view.restartButton.setDisabled(True)
        # self.main_window_view.openFileButton.setEnabled(True)
        if self.catch_server.isActive:
            self.catch_server.isActive = False

    def doRestart(self) -> None:
        """
        重新捕获
        :rtype: None
        """
        self.catch_server.isActive = False
        self.catch_server.counter = 0
        self.catch_server.interFace = self.getCurrentInterface()
        self.doClear()
        self.catch_server.isActive = True

    def doClear(self) -> None:
        """
        清空表格所有内容，设置行数为0
        :rtype: None
        """
        self.main_window_view.tableWidget.clearContents()
        self.main_window_view.tableWidget.setRowCount(0)
        # 清空缓存的数据包
        self.stored_packets = list()
        # 清空ScrollArea
        tree = self.main_window_view.DetailScrollArea.findChildren(QTreeWidget)
        if tree:
            tree[0].clear()
        text = self.main_window_view.FrameScrollArea.findChild(QTextEdit)
        if text:
            text.setPlainText('')

    def doUnsaved(self) -> int:
        """
        处理未保存的数据
        :rtype: int
        :return 返回文件保存状态
                1：点击了save，并且成功保存
                0：点击了save，并且未成功保存
                -1：点击了discard
                -2：点击了cancel
        """
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Unsaved packets...")
        msgBox.setText("您是否要保存已捕获的分组在开始捕获前？")
        msgBox.setInformativeText("若不保存，您已经捕获的分组将会丢失。")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard |
                                  QMessageBox.StandardButton.Cancel)
        msgBox.setDefaultButton(QMessageBox.StandardButton.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.StandardButton.Save:
            """doSave"""
            fileDialog = QFileDialog(self.main_window_view,
                                     "保存已捕获的文件",
                                     "../", save_types)
            fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_name = ""
            if fileDialog.exec():
                file_name = fileDialog.selectedFiles()[0]
            if file_name:
                wrpcap(filename=file_name, pkt=self.stored_packets)
                return 1
            return 0
        elif ret == QMessageBox.StandardButton.Discard:
            """doDiscard"""
            self.doRestart()
            return -1
        elif ret == QMessageBox.StandardButton.Cancel:
            """doCancel"""
            self.doPause()
            return -2

    def previousRow(self) -> None:
        """
        在表格中定位到前一个捕获
        :rtype: None
        """
        current_row = self.main_window_view.tableWidget.currentRow()
        if current_row > 0:
            set_index = current_row - 1
        else:
            set_index = 0
        if self.main_window_view.tableWidget.rowCount() > 0:
            self.main_window_view.tableWidget.selectRow(set_index)
            self.showPacketDetail(set_index)
            self.showPacketFrame(set_index)

    def nextRow(self) -> None:
        """
        在表格中定位到后一个捕获
        :rtype: None
        """
        current_row = self.main_window_view.tableWidget.currentRow()
        if current_row >= 0:
            set_index = current_row + 1
        else:
            set_index = 0
        if set_index < self.main_window_view.tableWidget.rowCount():
            self.main_window_view.tableWidget.selectRow(set_index)
            self.showPacketDetail(set_index)
            self.showPacketFrame(set_index)

    def topRow(self) -> None:
        """
        在表格中定位到首个捕获
        :rtype: None
        """
        self.main_window_view.tableWidget.selectRow(0)
        if self.main_window_view.tableWidget.rowCount() > 0:
            self.showPacketDetail(0)
            self.showPacketFrame(0)

    def tailRow(self) -> None:
        """
        在表格中定位到最后一个捕获
        :rtype: None
        """
        current_row = self.main_window_view.tableWidget.rowCount()
        self.main_window_view.tableWidget.selectRow(current_row - 1)
        if self.main_window_view.tableWidget.rowCount() > 0:
            self.showPacketDetail(current_row - 1)
            self.showPacketFrame(current_row - 1)

    def openFile(self) -> None:
        """
        读取文件
        :rtype: None
        """
        msgBox = QMessageBox()
        msgBox.setWindowTitle("table value will be replaced...")
        msgBox.setText("打开外部文件会覆盖现有数据")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Cancel)
        msgBox.setDefaultButton(QMessageBox.StandardButton.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.StandardButton.Open:
            fileDialog = QFileDialog(self.main_window_view,
                                     "保存已捕获的文件",
                                     "../", save_types)
            fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            file_name = ""
            if fileDialog.exec():
                file_name = fileDialog.selectedFiles()[0]
            if file_name:
                self.doClear()
                self.open_file_server.fileName = file_name
                self.open_file_server.isActive = True
        else:
            pass

    def showPacketDetail(self, row: int) -> None:
        """
        显示所选择的数据包的详情
        :rtype: None
        :param row: int, chosen row
        """
        treeWidget = QTreeWidget()
        treeWidget.header().setVisible(False)
        treeWidget.setAnimated(True)
        packet_detail = getAllLayersDetail(self.stored_packets[row])
        for layer in packet_detail:
            # 添加一级树节点
            root = QTreeWidgetItem(treeWidget)
            root.setExpanded(False)
            root.setText(0, layer)
            # 添加二级树节点
            for key, item in packet_detail[layer]:
                child = QTreeWidgetItem(root)
                child.setExpanded(False)
                child.setText(0, "{} : {}".format(key, item))

        self.main_window_view.DetailScrollArea.setWidget(treeWidget)

    def showPacketFrame(self, row: int) -> None:
        """
        显示所选择的数据包的帧详情
        :rtype: None
        :param row: int, chosen row
        """
        textEdit = QTextEdit()
        textEdit.setReadOnly(True)
        textEdit.setText(hexdump(self.stored_packets[row], dump=True))
        self.main_window_view.FrameScrollArea.setWidget(textEdit)

    def safeQuit(self) -> None:
        """
        在退出程序时关闭线程
        :rtype: None
        """
        self.catch_server.isQuit = True
        self.catch_thread.quit()
        self.main_window_view.close()
