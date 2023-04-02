from car import *
from mdns import *
import pprint
import threading
import time

cars_ip = dnsquery()

pprint.pprint(cars_ip)

cname = input("Car name: ")
cip = cars_ip[cname]

udpc2 = CarControl(create_udp_conn(cip), None, 2, b"\x00"*6)

throttle = 0
steer = 0
headlights = 0
def spam_pilot():
    while True:
        udpc2.pilot(throttle, steer)
        udpc2.set_headlights(headlights)
        time.sleep(0.05)

while not fetch_status(cip).started :
    udpc2.engine_on()
threading.Thread(target=spam_pilot).start()

while True:
    pprint.pprint(fetch_status(cip))
    command = input("> ")
    if command == "z":
        throttle += 10
    elif command == "s":
        throttle -= 10
    elif command == "q":
        steer -= 10
    elif command == "d":
        steer += 10
    elif command == " " :
        throttle = 0
        steer = 0
    elif command == "p":
        headlights += 10
    elif command == "m":
        headlights -= 10
    else:
        print("NACK")
