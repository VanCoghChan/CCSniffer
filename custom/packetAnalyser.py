from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether, ARP
from scapy.all import *


def getHighestProtocol(pkt: Ether) -> str:
    """
    :type pkt: scapy.layers.l2.Ether
    :param pkt: a packet that you want to know its highest protocol
    :return: a string --> the highest protocol of this packet
    """
    highest_layer = ""
    for layer in pkt.layers():
        layer = str(layer)
        if "scapy.layers" in layer:
            highest_layer = layer
    highest_layer_protocol = highest_layer.split('.')[-1][:-2]
    # 由于ICMPv6相关协议众多，为了便于显示，统一修改为ICMPv6
    if "ICMPv6" in highest_layer_protocol:
        highest_layer_protocol = "ICMPv6"
    # 同理统一IPv6
    elif "IPv6" in highest_layer_protocol:
        highest_layer_protocol = "IPv6"
    return highest_layer_protocol


def getTCPorUDPPort(pkt: Ether) -> dict:
    """
    :type pkt: scapy.layers.l2.Ether
    :rtype: a dict --> contains src_port, dst_port like this:{
            src_port:XXX, dst_port:XXX
        }
    :param pkt: a packet that you want to know its source port, destination port
    """
    res = {}
    tcp_udp_layer = None
    if pkt.haslayer(TCP):
        tcp_udp_layer = pkt.getlayer(TCP)
    elif pkt.haslayer(UDP):
        tcp_udp_layer = pkt.getlayer(UDP)
    res['src_port'], res['dst_port'] = tcp_udp_layer.sport, tcp_udp_layer.dport
    return res


def getIPLayerAddr(pkt: Ether) -> tuple:
    """
    :type pkt: scapy.layers.l2.Ether
    :rtype: a tuple --> contains src_ip, dst_ip like this:
            src_ip:XXX, dst_ip:XXX

    :param pkt: a packet that you want to know its source ip address, destination ip address
    """
    res = {}
    ip_layer = None
    if pkt.haslayer(IP):
        ip_layer = pkt.getlayer(IP)
    elif pkt.haslayer(IPv6):
        ip_layer = pkt.getlayer(IPv6)
    try:
        res['src_ip'], res['dst_ip'] = ip_layer.src, ip_layer.dst
    except AttributeError as e:
        print(pkt)
        pkt.show()
    return ip_layer.src, ip_layer.dst


def getARPLayerAddr(pkt: Ether) -> tuple:
    """
    :type pkt: scapy.layers.l2.Ether
    :rtype: a tuple --> contains hwsrc, hwdst like this:
            hwsrc:XXX, hwsrc:XXX
    :param pkt: a packet that you want to know its source MAC address, destination MAC address
    """
    layer = pkt.getlayer(ARP)
    return layer.hwsrc, layer.hwdst


def getAllLayersDetail(pkt: Ether) -> dict:
    """
    :type pkt: scapy.layers.l2.Ether
    :rtype: a dict --> contains all layers' detail info like this:{
            "Ether": {xxx}
            "IP": {xxx}
            "TCP": {xxx}
            ...}
    :param pkt: a packet that you want to know its all layer info
    """
    packet_detail = {}
    layers = pkt.layers()
    for layer in layers:
        layer = str(layer)
        protocol = layer.split('.')[-1][:-2]
        packet_detail[protocol] = pkt.getlayer(protocol).fields.items()
    return packet_detail
