import pyglet
import time
from pyglet.window import key
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from threading import *

from car import create_udp_conn, create_tcp_conn, CarControl, fetch_status


tabName = ["simu","car"]
tab = [("simu", "192.168.24.123"), ("car", "192.168.24.123")]

def createLabel(name, x, y):
    return pyglet.text.Label(name,
                          font_name='Times New Roman',
                          font_size=12,
                          x=x, y=y,
                          anchor_x='left', anchor_y='bottom')

class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print("name: " + name.split('.')[0])
        print("ip: "  + ".".join(str(val) for val in [info.addresses[0][i] for i in range(0, len(info.addresses[0]))]))
        tabName.append(name.split('.')[0])
        tab.append((name.split('.')[0], ".".join(str(val) for val in [info.addresses[0][i] for i in range(0, len(info.addresses[0]))])))


class Piglet(pyglet.window.Window):
    def __init__(self, controller):
        self.controller = controller

        super().__init__(width=512, height=512,visible=True)
        self.LabelEngine = createLabel("Engine: ", 10, 10)
        self.LabelStatusEngine = createLabel("0", 100, 10)

        self.LabelThrottle = createLabel("Throttle: ", 10, 40)
        self.LabelStatusThrottle = createLabel("0", 100, 40)

        self.LabelSteer = createLabel("Steer: ", 10, 70)
        self.LabelStatusSteer = createLabel("0", 100, 70)


    def updateSteerUI(self, steer):
        self.LabelStatusSteer.text = str(int(steer))

    def updateThrottleUI(self, throttle):
        self.LabelStatusThrottle.text = str(int(throttle))

    def updateEngineUI(self, engine):
        self.LabelStatusEngine.text = str(int(engine))

    def on_draw(self):
        if(self.controller.ip != None):
            status = fetch_status(self.controller.ip)

            self.updateSteerUI(status.steering)
            self.updateThrottleUI(status.throttle)
            self.updateEngineUI(status.started)

        self.clear()
        self.LabelEngine.draw()
        self.LabelStatusEngine.draw()
        self.LabelThrottle.draw()
        self.LabelStatusThrottle.draw()
        self.LabelSteer.draw()
        self.LabelStatusSteer.draw()

    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.Z:
            self.controller.ZisPressed = True
        elif symbol == key.S:
            self.controller.SisPressed = True
        elif symbol == key.Q:
            self.controller.QisPressed = True
        elif symbol == key.D:
            self.controller.DisPressed = True
        elif symbol == key.T:
            self.controller.startEngine()
        elif symbol == key.Y:
            self.controller.stopEngine()
    
    def on_key_release(self, symbol, modifiers):
        if symbol == key.Z:
            self.controller.ZisPressed = False
        elif symbol == key.S:
            self.controller.SisPressed = False
        elif symbol == key.Q:
            self.controller.QisPressed = False
        elif symbol == key.D:
            self.controller.DisPressed = False

class Controller:
    def __init__(self) -> None:
        self.ip = "192.168.24.123"
        self.udp = create_udp_conn(self.ip)
        #self.tcp = create_tcp_conn(self.udp, b"\x00"*6)
        self.carControl = CarControl(self.udp, None, 2, b"\x00"*6)

        self.throttle = 0
        self.steer = 0
        self.engine = False
        self.ZisPressed = False
        self.SisPressed = False
        self.QisPressed = False
        self.DisPressed = False

        self.threadCommand()

    def threadCommand(self):
        t1=Thread(target=self.updateValues)
        t1.start()

    def updateValues(self):
        while(True):

            if(self.ZisPressed and not self.SisPressed):
                self.throttle = 819
            elif(not self.ZisPressed and self.SisPressed):
                self.throttle = -819
            elif(not self.ZisPressed and not self.SisPressed):
                self.throttle = 0
            
            if(self.QisPressed and not self.DisPressed):
                self.steer = -3276 * 3
            elif(not self.QisPressed and self.DisPressed):
                self.steer = 3276 * 3
            elif(not self.QisPressed and not self.DisPressed):
                self.steer = 0

            ## Retrieve new values
            if(self.ip != None):
                if(self.engine):
                    self.carControl.pilot(self.throttle, self.steer)

            time.sleep(0.05)

    def throttleIncrease(self):
        print('increase throttle')
        self.throttle = int(min(self.SPEED_MAX, self.throttle + 819.2))

    def throttleDecrease(self):
        print('decrease throttle')
        self.throttle = int(max(self.SPEED_MIN, self.throttle - 819.2))

    def startEngine(self):
        if(self.ip != None):
            print("startEngine")
            self.engine = True
            self.carControl.engine_on()

    def stopEngine(self):
        if(self.ip != None):
            print("stopEngine")
            self.engine = False
            self.carControl.engine_off()

if __name__ == "__main__":

    Piglet(Controller())
    pyglet.app.run()
