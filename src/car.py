import socket
import struct
import threading

LOCAL_PORT = 65432
REMOTE_HOST = "192.168.24.123"
REMOTE_PORT = 4210


ENGINE_CTRL = b"\x10"
PILOTE_CTRL = b"\x11"
HEADLIGHT_CTRL = b"\x12"

LIMIT_SPEED = 0X30
INVERT_STEERING = 0X31
INVERT_THROTTLE = 0X32
SET_COLOR = 0x33

ENGINE_ON = b"\x01"
ENGINE_OFF = b"\x00"

class AbstractComm(socket.socket):

    def send_command(self, lvl=1, passwd=b"\x00"*6, command=b"\x00", arg=b"\x00"):
        msg = b"CIS" + bytes([lvl]) + passwd + command + arg
        print(msg)
        if self.send(msg) != len(msg) :
            raise RuntimeError("UDP command failed")

class UDPComm(AbstractComm):

    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.connect((REMOTE_HOST, REMOTE_PORT))

class TCPComm(AbstractComm) :

    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", LOCAL_PORT))
        self.listen(16)

    def upgrade_from_udp(self, updcomm, passwd2):
        updcomm.send_command(lvl=2, passwd=passwd2,
                             command=b"\x01" + LOCAL_PORT.to_bytes(2, "little", signed=False)
        )
        self._client, self._client_addr = self.accept()


def listen_multicast():
    MCAST_GRP = '239.255.0.1'
    MCAST_PORT = 4211
    IS_ALL_GROUPS = True

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if IS_ALL_GROUPS:
        # on this port, receives ALL multicast groups
        sock.bind(('', MCAST_PORT))
    else:
        # on this port, listen ONLY to MCAST_GRP
        sock.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("listening for multicast info")

    while True:
        data, address = sock.recvfrom(1024)
        if  address[0] == REMOTE_HOST:
            print_status_packet(data)

def print_status_packet(packet):
    if not packet.startswith(b"CIS"):
        return
    packet = packet[3:]

    while len(packet):
        srv = packet[0]
        packet = packet[1:]
        if srv == 0:
            # STATUS_NO_REPORT
            print("(no report)")
        elif srv == 1:
            # STATUS_RSSI
            rssi = int.from_bytes(packet[:4], "little", signed=True)
            packet = packet[4:]
            print(f"RSSI: {rssi}")
        elif srv == 2:
            # STATUS_IR
            ir = int.from_bytes(packet[:1], "little", signed=False)
            packet = packet[1:]
            print(f"IR: {ir}")
        elif srv == 3:
            # STATUS_SIMULATION
            x = int.from_bytes(packet[:2], "little", signed=False)
            packet = packet[2:]
            y = int.from_bytes(packet[:2], "little", signed=False)
            packet = packet[2:]
            theta = int.from_bytes(packet[:2], "little", signed=False)
            packet = packet[2:]
            print(f"simu: {x=} {y=} {theta=}")
        elif srv == 4:
            # STATUS_HEADLIGHTS
            hl = int.from_bytes(packet[:2], "little", signed=False)
            packet = packet[2:]
            print(f"Headlights: {hl}")
        elif srv == 5:
            # STATUS_COLOR
            r = int.from_bytes(packet[0:1], "little", signed=False)
            g = int.from_bytes(packet[1:2], "little", signed=False)
            b = int.from_bytes(packet[2:3], "little", signed=False)
            packet = packet[3:]
            disp_r = int.from_bytes(packet[0:1], "little", signed=False)
            disp_g = int.from_bytes(packet[1:2], "little", signed=False)
            disp_b = int.from_bytes(packet[2:3], "little", signed=False)
            packet = packet[3:]
            print(f"Color: #{r:02X}{g:02X}{b:02X}")
            print(f"Displayed color: #{disp_r:02X}{disp_g:02X}{disp_b:02X}")
        elif srv == 6:
            # STATUS_BATTERY
            adc = int.from_bytes(packet[:2], "little", signed=False)
            packet = packet[2:]
            soc = int.from_bytes(packet[:2], "little", signed=False)
            packet = packet[2:]
            print(f"Battery: {adc=}  {soc=}")
        elif srv == 7:
            # STATUS_IMU
            imu_x_x = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            imu_x_y = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            imu_x_z = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]

            imu_g_x = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            imu_g_y = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            imu_g_z = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]

            print(f"IMU: acceleration {imu_x_x} {imu_x_y} {imu_x_z}")
            print(f"IMU: rotation {imu_g_x} {imu_g_y} {imu_g_z}")
        elif srv == 8:
            # STATUS_PILOT
            throtlle = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            steering = int.from_bytes(packet[:2], "little", signed=True)
            packet = packet[2:]
            started = int.from_bytes(packet[:1], "little", signed=False)
            packet = packet[1:]
            print(f"Pilot: {throtlle=} {steering=} {started=}")
        else:
            raise ValueError("Invalid packet")


def start_engine(udp):
    udp.send_command(lvl=1, passwd=b"\x00\x01\x02\x03\x04\x05", command=ENGINE_CTRL, arg=ENGINE_ON)
def stop_engine(udp):
    udp.send_command(lvl=1, passwd=b"\x00\x01\x02\x03\x04\x05", command=ENGINE_CTRL, arg=ENGINE_OFF)

def change_headlights(udp, level):
    udp.send_command(lvl=1, passwd=b"\x00\x01\x02\x03\x04\x05", command=HEADLIGHT_CTRL,
                     arg=int.to_bytes(level, 2, "little", signed=False))

def control_pilote(udp, throttle, steering):
    udp.send_command(lvl=1, passwd=b"\x00\x01\x02\x03\x04\x05", command=PILOTE_CTRL,
                     arg=(throttle << 16 | steering).to_bytes(length=4, byteorder="little", signed=False))


if __name__ == '__main__':

    udp = UDPComm()
    #udp.send_command(lvl=2, passwd=b"\x00"*6, command=b"\x12\x00\x07")
    #udp.send_command(lvl=1, passwd=b"\x00"*6, command=b"\x10\x01")
    #udp.send_command(lvl=1, passwd=b"\x00\x01\x02\x03\x04\x05", command=b"\x12\x00\x07")
    udp.send_command(lvl=1, passwd=b"\x00"*6, command=b"\x21\x00\x01\x02\x03\x04\x05")
    start_engine(udp)
    change_headlights(udp, 700)
    control_pilote(udp, 200, 200)



##    print("UDP up!")
    #tcp = TCPComm()
##    print("TCP up!")
    #tcp.upgrade_from_udp(udp, b"\x00\x00\x00\x00\x00\x00")
##    print("TCP upgrade!")
#
    listen_multicast()
