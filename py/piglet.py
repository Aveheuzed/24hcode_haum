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
        
        self.LabelBoost = createLabel("Boost: ", 150, 10)
        self.LabelStatusBoost = createLabel("True", 200, 10)

        self.LabelThrottle = createLabel("Throttle: ", 10, 40)
        self.LabelStatusThrottle = createLabel("0", 100, 40)

        self.LabelSteer = createLabel("Steer: ", 10, 70)
        self.LabelStatusSteer = createLabel("0", 100, 70)

        self.LabelRssi = createLabel("Rssi: ", 10, 100)
        self.LabelStatusRssi = createLabel("0", 100, 100)

        self.LabelIrvalue = createLabel("IR: ", 10, 130)
        self.LabelStatusIrvalue = createLabel("0", 100, 130)
        
        self.LabelHeadlight = createLabel("Headlight: ", 10, 160)
        self.LabelStatusHeadlight = createLabel("40000", 100, 160)

        self.LabelWarn = createLabel("Warn: ", 150, 160)
        self.LabelStatusWarn = createLabel("False", 200, 160)
        
        # get a list of all low-level input devices:
        devices = pyglet.input.get_devices()

        # get a list of all controllers:
        controllers = pyglet.input.get_controllers()
        if controllers:
            controller = controllers[0]
            controller.open()
            controller.event(self.on_button_press)
            controller.event(self.on_button_release)
            print('Controller Ok')

        
        joysticks = pyglet.input.get_joysticks()

        if joysticks:
            joystick = joysticks[0]
            joystick.open()
            joystick.event(self.on_joyaxis_motion)
        print('Controller Ok')



    def updateSteerUI(self, steer):
        self.LabelStatusSteer.text = str(int(steer))

    def updateThrottleUI(self, throttle):
        self.LabelStatusThrottle.text = str(int(throttle))

    def updateEngineUI(self, engine):
        self.LabelStatusEngine.text = str(int(engine))

    def updateBoostUI(self, boost):
        self.LabelStatusBoost.text = str(boost)
        
    def updateRssiUI(self, rssi):
        self.LabelStatusRssi.text = str(int(rssi))

    def updateIrvaluUI(self, irValue):
        self.LabelStatusIrvalue.text = chr(irValue)
    
    def updateHeadlightUI(self, headlight):
        self.LabelStatusHeadlight.text = str(headlight)

    def updateWarnUI(self, warn):
        self.LabelStatusWarn.text = str(warn)

    def on_button_press(self, controller, button_name):     
        if button_name == 'a':
            self.controller.startEngine()
        elif button_name == 'b':
            self.controller.toggleWarn()
        elif button_name == 'leftstick':
            self.controller.boostMode(True)
        elif button_name == 'leftshoulder':
            self.controller.headlightChange(False)
        elif button_name == 'rightshoulder':
            self.controller.headlightChange(True)

    def on_button_release(self, controller, button_name):
        if button_name == 'leftstick':
            self.controller.boostMode(False)

    def on_joyaxis_motion(self, joystick, axis, value):
        if axis == 'y':
            self.controller.throttle = -int((self.controller.THROTTLE_MAX / 2 ) * round(value,2))
        elif axis == 'rx':
            self.controller.steer = int((self.controller.STEER_MAX / 2 - 1) * round(value,2))


    def on_draw(self):
        if(self.controller.ip != None):
            status = fetch_status(self.controller.ip)

            self.updateSteerUI(status.steering)
            self.updateThrottleUI(status.throttle)
            self.updateEngineUI(status.started)
            self.updateRssiUI(status.rssi)
            self.updateIrvaluUI(status.ir)
            self.updateBoostUI(self.controller.boost)
            self.updateHeadlightUI(status.headlights)
            self.updateWarnUI(self.controller.warnMode)

        self.clear()
        self.LabelEngine.draw()
        self.LabelStatusEngine.draw()
        self.LabelBoost.draw()
        self.LabelStatusBoost.draw()
        self.LabelThrottle.draw()
        self.LabelStatusThrottle.draw()
        self.LabelSteer.draw()
        self.LabelStatusSteer.draw()
        self.LabelIrvalue.draw()
        self.LabelStatusIrvalue.draw()
        self.LabelHeadlight.draw()
        self.LabelStatusHeadlight.draw()
        self.LabelWarn.draw()
        self.LabelStatusWarn.draw()
        self.LabelRssi.draw()
        self.LabelStatusRssi.draw()

    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.T:
            self.controller.startEngine()
        elif symbol == key.Y:
            self.controller.stopEngine()

class Controller:
    def __init__(self) -> None:
        #100
        self.ip = "192.168.24.123"
        self.udp = create_udp_conn(self.ip)
        #self.tcp = create_tcp_conn(self.udp, b"\x00"*6)
        self.carControl = CarControl(self.udp, None, 2, b"\x00"*6)
        self.setRearColor(0,255,0)

        self.warnMode = False
        self.boost = False
        self.throttle = 0
        self.steer = 0
        self.engine = False

        self.headlight = 40000
        self.ZisPressed = False
        self.SisPressed = False
        self.QisPressed = False
        self.DisPressed = False

        self.LIGHT_MIN = 0
        self.LIGHT_MAX = 65535

        self.THROTTLE_MAX = 8192
        self.THROTTLE_MIN = -8192
        self.STEER_MAX = 32768
        self.STEER_MIN = -32768

        self.threadCommand()
        self.threagWarn()

    def toggleWarn(self):
        self.warnMode = not self.warnMode

    def threagWarn(self):
        t1=Thread(target=self.updateWarn)
        t1.start()

    def updateWarn(self):
        while True:
            if self.warnMode:
                self.carControl.set_headlights(0)
                time.sleep(1)
                self.carControl.set_headlights(60000)


    def threadCommand(self):
        t1=Thread(target=self.updateValues)
        t1.start()

    def updateValues(self):
        while(True):


            ## Retrieve new values
            if(self.ip != None):
                if(self.engine):

                    calVal = self.throttle
                    if self.boost:
                        calVal = 16000
                        
                    self.carControl.pilot(calVal , self.steer)

            time.sleep(0.05)

    def headlightChange(self, bool):
        if bool:
            self.headlight = min(self.LIGHT_MAX,self.headlight + 10000) 
        else:
            self.headlight = max(self.LIGHT_MIN,self.headlight - 10000)
        self.carControl.set_headlights(self.headlight)

    def boostMode(self, bool):
        self.boost = bool

        if(self.boost):
            self.carControl.set_color(255,0,0)
        else:
            self.carControl.set_color(0,255,0)

    def throttleIncrease(self):
        self.throttle = min(self.THROTTLE_MAX, (self.throttle + 10))

    def throttleDecrease(self):
        self.throttle = max(self.THROTTLE_MIN, self.throttle - 10)

    def steerLeft(self):
        self.steer = max(self.STEER_MIN, self.steer - 500)

    def steerRight(self):
        self.steer = min(self.STEER_MAX, (self.steer + 500))

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

    def setRearColor(self, r, g, b):
        self.carControl.set_color(r,g,b)

if __name__ == "__main__":

    Piglet(Controller())
    pyglet.app.run()
