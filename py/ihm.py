from tkinter import *

from car import *
from mdns import *
import pprint
import threading
import time

if __name__ == "__main__":

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

    def event_handler(event):
        global throttle, steer, headlights
        if event.keysym == "z":
            throttle += 10
        elif event.keysym == "s":
            throttle -= 10
        elif event.keysym == "q":
            steer -= 10
        elif event.keysym == "d":
            steer += 10
        elif event.keysym == "space" :
            throttle = 0
            steer = 0
        elif event.keysym == "p":
            headlights += 10
        elif event.keysym == "m":
            headlights -= 10

    while not fetch_status(cip).started :
        udpc2.engine_on()
    threading.Thread(target=spam_pilot).start()

    # UI setup
    # ------------------------------------------------------------------

    root = Tk()
    display = Text(root, state=DISABLED)

    def display_update():
        display["state"] = NORMAL
        display.delete("1.0", END)
        display.insert(END, pprint.pformat(fetch_status(cip)))
        display["state"] = DISABLED
        display.after(500, display_update)

    root.bind("<KeyPress>", event_handler)
    display_update()

    display.pack()
    root.mainloop()
