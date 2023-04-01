import socket
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

if __name__ == '__main__':

    udp = UDPComm()
    print("UDP up!")
    tcp = TCPComm()
    print("TCP up!")
    tcp.upgrade_from_udp(udp, b"passwd")
    print("TCP upgrade!")
