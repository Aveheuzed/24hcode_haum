import socket

UDP_IP = "192.168.24.1"
UDP_PORT = 4210
MESSAGE = "Hi, can you listen to this?"

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("message:", MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE.encode('ascii'), (UDP_IP, UDP_PORT))

print("sended")
