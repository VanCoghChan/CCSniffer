import time

from PyQt6.QtCore import QObject, pyqtSignal
from scapy.all import *
from scapy.layers.l2 import Ether

from custom.packetAnalyser import getHighestProtocol, getARPLayerAddr, getIPLayerAddr


class OpenFileServer(QObject):
    """处理大文件的加载"""
    def __init__(self):
        super(OpenFileServer, self).__init__()

    _file_name = None
    _is_active = False
    _counter = 0
    current_paket = pyqtSignal(scapy.layers.l2.Ether)
    current_packet_info = pyqtSignal(tuple)

    @property
    def isActive(self) -> bool:
        return self._is_active

    @isActive.setter
    def isActive(self, value: bool) -> None:
        self._is_active = value

    @property
    def counter(self) -> int:
        return self._counter

    @counter.setter
    def counter(self, value: int) -> None:
        self._counter = value

    @property
    def fileName(self) -> str:
        return self._file_name

    @fileName.setter
    def fileName(self, file_name: str) -> None:
        self._file_name = file_name

    def run(self):
        while True:
            while self.isActive:
                pkts = rdpcap(filename=self._file_name)
                base_time = pkts[0].time
                for pkt in pkts:
                    protocol = getHighestProtocol(pkt)
                    if protocol == 'ARP':
                        src, dst = getARPLayerAddr(pkt)
                    else:
                        src, dst = getIPLayerAddr(pkt)
                    self._counter += 1
                    current_packet = (self._counter, round(pkt.time - base_time, 6),
                                      src, dst, protocol, len(pkt), str(pkt))
                    self.current_packet_info.emit(current_packet)
                    self.current_paket.emit(pkt)
                    time.sleep(0.2)
                self.isActive = False
