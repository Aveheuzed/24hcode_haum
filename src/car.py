import socket
import struct
import threading

class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

def send_command(level, pwd, cmd, arg):
    UDP_IP = "192.168.24.1"
    UDP_PORT = 4210
    MESSAGE = bytes("CIS" + level + pwd + cmd + arg, encoding='utf-8')

    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    print("message:", MESSAGE)

    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    print("sended")
    recv = sock.recv(2048)
    print("recv ".join(recv))

def tcp_server(name):

    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        send_command("1", "000000", chr(0x10), str(1)) #engine on
        #send_command("1", "000000", chr(0x10), str(0)) #engine off
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                print(f"{data}", data)


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

    listen_multicast()
    #tcp_server("toto")



