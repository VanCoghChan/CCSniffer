import scapy.interfaces
import scapy.arch.windows
from PyQt6.QtCore import QEvent, QSize, Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QMouseEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QPushButton, QAbstractItemView, QHBoxLayout

from views.primitive_views.MainWindowView_pre import *
from qt_material import apply_stylesheet
from custom.style import min_style, close_style, normalButton_style
import sys


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 初始化UI
        self.hboxLayout = None
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
        # 初始化表格控件
        self.initTable()
        # 初始化Label控件
        self.initLabel()

    def initButtons(self) -> None:
        """
        初始化按钮控件
        :rtype: None
        """
        # 单独设置最小化、关闭窗口按钮以及filter按钮的样式
        self.minButton.setStyleSheet(min_style)
        self.closeButton.setStyleSheet(close_style)
        self.minButton.setIcon(QIcon("./resources/min.png"))
        self.closeButton.setIcon(QIcon("./resources/close.png"))
        self.doFilterButton.setProperty('class', 'success')

        # 设置按钮图标的QPixmap
        catchpix = QPixmap("./resources/start.png")
        catchpix = catchpix.scaled(QSize(80, 80))
        pausepix = QPixmap("./resources/pause.png")
        pausepix = pausepix.scaled(QSize(80, 80))
        restartpix = QPixmap("./resources/restart.png")
        restartpix = restartpix.scaled(QSize(80, 80))
        openFilepix = QPixmap("./resources/openFiles.png")
        openFilepix = openFilepix.scaled(QSize(80, 80))
        prepix = QPixmap("./resources/pre.png")
        prepix = prepix.scaled(QSize(80, 80))
        postpix = QPixmap("./resources/post.png")
        postpix = postpix.scaled(QSize(80, 80))
        toppix = QPixmap("./resources/top.png")
        toppix = toppix.scaled(QSize(80, 80))
        bottompix = QPixmap("./resources/bottom.png")
        bottompix = bottompix.scaled(QSize(80, 80))
        # 将QPixmap应用到按钮
        self.catchButton.setIcon(QIcon(catchpix))
        self.pauseButton.setIcon(QIcon(pausepix))
        self.restartButton.setIcon(QIcon(restartpix))
        self.openFileButton.setIcon(QIcon(openFilepix))
        self.jump2preButton.setIcon(QIcon(prepix))
        self.jump2nextButton.setIcon(QIcon(postpix))
        self.jump2topButton.setIcon(QIcon(toppix))
        self.jump2tailButton.setIcon(QIcon(bottompix))
        # 功能按钮应用自定义style（增加hover样式）
        for button in self.findChildren(QPushButton):
            if button.objectName() not in ["closeButton", "minButton", "ucasLogoButton"]:
                button.setStyleSheet(normalButton_style)
        self.catchButton.setStyleSheet(normalButton_style)

    def initTable(self) -> None:
        """
        对QTableWidget的初始化
        :rtype: None
        """
        # 设置表格单元不可编辑
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 取消表格默认行号
        self.tableWidget.verticalHeader().setHidden(True)
        # 根据现有窗口设置表头单元格宽度
        self.tableWidget.horizontalHeader().resizeSection(0, 70)
        self.tableWidget.horizontalHeader().resizeSection(1, 80)
        self.tableWidget.horizontalHeader().resizeSection(2, 140)
        self.tableWidget.horizontalHeader().resizeSection(3, 140)
        self.tableWidget.horizontalHeader().resizeSection(4, 120)
        self.tableWidget.horizontalHeader().resizeSection(5, 100)
        self.tableWidget.horizontalHeader().resizeSection(6, 310)
        headerItemTooltips = ["序号", "捕获时间", "源IP地址", "目的IP地址", "协议", "长度(字节)", "详细"]
        for idx, tip in zip(range(7), headerItemTooltips):
            item = self.tableWidget.horizontalHeaderItem(idx)
            item.setToolTip(tip)

    def initLabel(self) -> None:
        """
        对QLabel控件初始化
        :rtype: None
        """
        # 设置国科大Logo
        ucasPixmap = QPixmap("./resources/ucas.png")
        ucasPixmap = ucasPixmap.scaled(self.ucasLogo.width() - 3, self.ucasLogo.height() - 3,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        self.ucasLogo.setPixmap(ucasPixmap)

        # 设置燦Logo
        canPixmap = QPixmap("./resources/can.png")
        canPixmap = canPixmap.scaled(self.canLogo.width(), self.canLogo.height(),
                                     Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
        self.canLogo.setPixmap(canPixmap)
        self.textEdit.verticalScrollBar().setVisible(False)
        self.textEdit.verticalScrollBar().setDisabled(True)
        self.textEdit.setReadOnly(True)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_amber.xml')
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
