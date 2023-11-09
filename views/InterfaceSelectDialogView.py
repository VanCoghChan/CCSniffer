import os
import sys

import psutil
import scapy.interfaces
from PyQt6.QtCharts import QChart, QSplineSeries, QValueAxis, QChartView
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSlot, QSize
from scapy.all import *
from PyQt6.QtGui import QIcon, QMouseEvent, QPen, QFont, QColor, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QListWidgetItem, QWidget, QRadioButton
from qt_material import apply_stylesheet

from custom.style import min_style, close_style
from models.GetInterfaceModel import GetInterfaceServer
from views.primitive_views.InterfaceSelectDialogView_pre import *


class InterfaceSelectDialog(Ui_InterfaceSelectDialog, QtWidgets.QDialog):
    def __init__(self):
        super(InterfaceSelectDialog, self).__init__()
        self._interfaces = scapy.interfaces.get_working_ifaces()
        # 初始化UI
        self.setupUi(self)
        # 设置鼠标位置记录量,用于窗口拖动实现
        self.mouse_pos = None
        # 设置窗口无边框
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # 设置窗口透明度
        self.setWindowOpacity(0.97)
        # 设置窗口大小固定
        self.setFixedSize(self.width(), self.height())
        # 初始化按钮控件
        self.initButtons()
        # 初始化列表控件
        self.initList()
        # 初始化label控件
        self.initLabel()

    def initButtons(self):
        self.minButton.setStyleSheet(min_style)
        self.closeButton.setStyleSheet(close_style)
        self.minButton.setIcon(QIcon("./resources/min.png"))
        self.closeButton.setIcon(QIcon("./resources/close.png"))
        self.minButton.clicked.connect(self.showMinimized)
        self.closeButton.clicked.connect(self.close)

    def initList(self):
        for interface in self._interfaces:
            listItem = customQListWidgetItem(interface.name)
            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, listItem.widget)

    def initLabel(self):
        # 设置UCASLogo
        statuspix = QPixmap("./resources/ucas.png")
        statuspix = statuspix.scaled(QSize(self.ucasLabel.width(), self.ucasLabel.height()),
                                     Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation
                                     )
        self.ucasLabel.setPixmap(statuspix)

        # 设置燦Logo
        canPixmap = QPixmap("./resources/can.png")
        canPixmap = canPixmap.scaled(self.canLogo.width(), self.canLogo.height(),
                                     Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
        self.canLogo.setPixmap(canPixmap)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        鼠标按下时记录坐标
        :type event: QMouseEvent
        """
        self.mouse_pos = event.globalPosition()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        鼠标移动时计算移动距离
        :type event: QMouseEvent
        """
        if self.mouse_pos:
            diff = event.globalPosition() - self.mouse_pos
            self.move(self.pos() + diff.toPoint())
            self.mouse_pos = event.globalPosition()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        鼠标释放时清空坐标
        :type event: QMouseEvent
        """
        self.mouse_pos = None


class customQListWidgetItem(QListWidgetItem):
    def __init__(self, iface_name):
        super().__init__()
        # 自定义item中的widget 用来显示自定义的内容
        self.widget = QWidget()
        # 设置布局
        self.hboxLayout = QHBoxLayout()
        # 设置label
        self.nameLabel = QLabel()
        self.nameLabel.setText(iface_name)
        self.statusLabel = QLabel()
        statuspix = QPixmap("./resources/status_red.png")
        statuspix = statuspix.scaled(QSize(20, 20),
                                     Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation
                                     )
        self.statusLabel.setPixmap(statuspix)
        self.bytesLabel = QLabel()
        self.hboxLayout.addWidget(self.nameLabel)
        self.hboxLayout.addWidget(self.statusLabel)
        self.hboxLayout.addWidget(self.bytesLabel)

        # 设置widget的布局
        self.widget.setLayout(self.hboxLayout)
        # 设置自定义的QListWidgetItem的sizeHint，不然无法显示
        self.setSizeHint(self.widget.sizeHint())


