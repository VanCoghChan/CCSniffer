import time

import psutil
import scapy.interfaces
from scapy.all import *
from PyQt6.QtCore import QObject, pyqtSignal


class GetInterfaceServer(QObject):
    """捕获网卡信息"""
    isActive = True
    bytes_flow = pyqtSignal(dict)
    interfaces_scapy = scapy.interfaces.get_working_ifaces()
    interfaces_psutil = psutil.net_io_counters(pernic=True)

    def run(self):
        while True:
            if not self.isActive:
                break
            res = {}
            for interface in self.interfaces_scapy:
                if interface.name in self.interfaces_psutil:
                    bytes_sent = psutil.net_io_counters(pernic=True)[interface.name].bytes_sent
                    bytes_recv = psutil.net_io_counters(pernic=True)[interface.name].bytes_recv
                else:
                    bytes_sent = 0
                    bytes_recv = 0
                res[interface.name] = (bytes_sent, bytes_recv)
            time.sleep(1)
            self.bytes_flow.emit(res)
        print("线程结束,等待销毁")
