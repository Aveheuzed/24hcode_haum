import socket
import struct

import threading
import time
from dataclasses import dataclass
from select import select
import random


LOCAL_PORT = 65432
REMOTE_HOST = "192.168.24.123"
REMOTE_PORT = 4210

MCAST_GRP = '239.255.0.1'
MCAST_PORT = 4211


def create_udp_conn(remote_host):
    print("create UDP")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((remote_host, REMOTE_PORT))
    return s

def create_tcp_conn(udp, lvl_2_pass):
    print("create TCP")
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("", LOCAL_PORT))
    tcp.listen(16)

    udpcontrol = CarControl(udp, tcp, 2, lvl_2_pass)

    while True:
        udpcontrol.open_tcp_link(LOCAL_PORT)
        ack = select([tcp], [], [], 1.0)[0]
        if not ack:
            continue
        client, client_addr = tcp.accept()
        print("TCP upgrade from", client_addr)
        return client

class CarControl :

    def __init__(self, udpsocket, tcpsocket, lvl, password):
        self.udpsocket = udpsocket
        self.tcpsocket = tcpsocket
        self.lvl = lvl
        self.password = password

        self.upgrade_passwords()

    def udp_generic_send(self, command):
        self.udpsocket.send(b"CIS"
                       + self.lvl.to_bytes(1, "big")
                       + self.password
                       + command
        )

    def tcp_generic_send(self, command):
        self.tcpsocket.send(b"CIS"
                       + self.lvl.to_bytes(1, "big")
                       + self.password
                       + command
        )

    def upgrade_passwords(self):
        newpass = random.randbytes(6)
        self.udp_generic_send(b"\x21"+newpass)
        print(f"Level 1 password: old {self.password} | new {newpass}")
        if self.lvl == 1:
            self.password = newpass

        newpass = random.randbytes(6)
        self.udp_generic_send(b"\x22"+newpass)
        print(f"Level 2 password: old {self.password} | new {newpass}")
        if self.lvl == 2:
            self.password = newpass

    def open_tcp_link(self, port):
        self.udp_generic_send(b"\x01"+port.to_bytes(2, "big"))

    def engine_on(self):
        self.udp_generic_send(b"\x10\x01")

    def engine_off(self):
        self.udp_generic_send(b"\x10\x00")

    def pilot(self, throttle, steering):
        self.udp_generic_send(b"\x11"+throttle.to_bytes(2, "big", signed=True)+steering.to_bytes(2, "big",signed=True))

    def set_headlights(self, level):
        self.udp_generic_send(b"\x12"+level.to_bytes(2, "big"))

    def invert_steering(self, activate=True):
        self.udp_generic_send(b"\x31"+activate.to_bytes(1, "big"))

    def invert_throttle(self, activate=True):
        self.udp_generic_send(b"\x32"+activate.to_bytes(1, "big"))

    def set_color(self, r, g, b):
        self.udp_generic_send(b"\x33"+r.to_bytes(1)+g.to_bytes(1)+b.to_bytes(1, "big"))

@dataclass
class CarStatus:
    rssi: int = None
    ir: int = None
    sim_x: int = None
    sim_y: int = None
    sim_theta: int = None
    headlights: int = None
    r:int = None
    g:int = None
    b:int = None
    disp_r:int = None
    disp_g:int = None
    disp_b:int = None
    batt_adc:int = None
    batt_soc:int = None
    imu_xl_x:int = None
    imu_xl_y:int = None
    imu_xl_z:int = None
    imu_g_x:int = None
    imu_g_y:int = None
    imu_g_z:int = None
    throttle:int = None
    steering:int = None
    started:int = None

    def is_complete(self):
        return not any(x is None for x in self.__dict__.values())

def fetch_status(target_host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    status = CarStatus()
    while not status.is_complete():
        data, address = sock.recvfrom(1024)
        if address[0] == target_host:
            fill_status(data, status)
    return status

def fill_status(packet, status):
    if not packet.startswith(b"CIS"):
        return
    packet = packet[3:]

    while len(packet):
        srv = packet[0]
        packet = packet[1:]
        if srv == 0:
            # STATUS_NO_REPORT
            pass
        elif srv == 1:
            # STATUS_RSSI
            status.rssi = int.from_bytes(packet[:4], "little", signed=True)
            packet = packet[4:]
        elif srv == 2:
            # STATUS_IR
            status.ir = int.from_bytes(packet[:1], "little")
            packet = packet[1:]
        elif srv == 3:
            # STATUS_SIMULATION
            status.sim_x = int.from_bytes(packet[:2], "little")
            packet = packet[2:]
            status.sim_y = int.from_bytes(packet[:2], "little")
            packet = packet[2:]
            status.sim_theta = int.from_bytes(packet[:2], "little")
            packet = packet[2:]
        elif srv == 4:
            # STATUS_HEADLIGHTS
            status.headlights = int.from_bytes(packet[:2], "little")
            packet = packet[2:]
        elif srv == 5:
            # STATUS_COLOR
            status.r = int.from_bytes(packet[0:1], "little")
            status.g = int.from_bytes(packet[1:2], "little")
            status.b = int.from_bytes(packet[2:3], "little")
            packet = packet[3:]
            status.disp_r = int.from_bytes(packet[0:1], "little")
            status.disp_g = int.from_bytes(packet[1:2], "little")
            status.disp_b = int.from_bytes(packet[2:3], "little")
            packet = packet[3:]
        elif srv == 6:
            # STATUS_BATTERY
            status.batt_adc = int.from_bytes(packet[:2], "little")
            packet = packet[2:]
            status.batt_soc = int.from_bytes(packet[:2], "little")
            packet = packet[2:]
        elif srv == 7:
            # STATUS_IMU
            status.imu_xl_x = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            status.imu_xl_y = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            status.imu_xl_z = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]

            status.imu_g_x = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            status.imu_g_y = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            status.imu_g_z = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
        elif srv == 8:
            # STATUS_PILOT
            status.throttle = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            status.steering = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            status.started = int.from_bytes(packet[:1], "little")
            packet = packet[1:]
        else:
            raise ValueError("Invalid packet")
