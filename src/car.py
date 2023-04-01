import socket
import struct
import threading

LOCAL_PORT = 65432
REMOTE_HOST = "192.168.24.1"
REMOTE_PORT = 4210

class AbstractComm(socket.socket):

    def send_command(self, lvl=1, passwd=b"\x00"*6, command=b""):
        msg = b"CIS" + bytes([lvl]) + passwd + command

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
                command=b"\x01"+LOCAL_PORT.to_bytes(2, "big", signed=False)
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
    # For Python 3, change next line to "print(sock.recv(10240))"
        print(sock.recv(10240))

if __name__ == '__main__':

    udp = UDPComm()
    print("UDP up!")
    tcp = TCPComm()
    print("TCP up!")
    tcp.upgrade_from_udp(udp, b"passwd")
    print("TCP upgrade!")

    listen_multicast()
