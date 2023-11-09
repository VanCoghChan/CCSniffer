import sys
import time

import scapy.layers.l2
import scapy.arch.windows
from PyQt6.QtCore import QObject, pyqtSignal
from scapy.all import *

from custom.packetAnalyser import getIPLayerAddr, getHighestProtocol, getARPLayerAddr


class CatchServer(QObject):
    def __init__(self):
        super(CatchServer, self).__init__()

    """处理嗅探任务"""
    _interface = None
    _is_active = False
    isQuit = False
    _counter = 0
    # 包捕获信号
    current_paket = pyqtSignal(scapy.layers.l2.Ether)
    current_packet_info = pyqtSignal(tuple)
    # 包数量信号
    packet_number = pyqtSignal(int)

    @property
    def interFace(self) -> scapy.arch.windows.NetworkInterface_Win:
        return self._interface

    @interFace.setter
    def interFace(self, value: scapy.arch.windows.NetworkInterface_Win) -> None:
        self._interface = value

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

    def run(self):
        while True:
            if self.isQuit:
                break
            self._counter = 0
            while self._is_active:
                try:
                    sniff_filter = "ether proto 0x0800 or ether proto 0x86dd or ether proto 0x11 or ether proto 0x0806"
                    '''
                        ether proto 0x0806 - 匹配ARP包
                        ether proto 0x0800 - 匹配IPv4包
                        ether proto 0x86dd - 匹配IPv6包
                        ether proto 0x11 - 匹配UDP包(IPv4/IPv6上的UDP)
                    '''
                    print("线程中的网卡：", self._interface.name)
                    pkt = sniff(count=1, filter=sniff_filter, iface=self._interface)[0]
                    print("...")
                    self._counter += 1
                    protocol = getHighestProtocol(pkt)
                    if protocol == 'ARP':
                        src, dst = getARPLayerAddr(pkt)
                    else:
                        src, dst = getIPLayerAddr(pkt)
                    current_packet = (self._counter, pkt.time,
                                      src, dst, protocol, len(pkt), str(pkt))
                    self.current_paket.emit(pkt)
                    self.current_packet_info.emit(current_packet)
                    self.packet_number.emit(self._counter)
                except OSError as e:
                    print(e)
