import tkinter as tk
import tkinter.font as tkFont
from tkinter.colorchooser import askcolor
from tkinter import ttk
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import time
from threading import *
#from PIL import ImageTk, Image
#import cv2

from car import create_udp_conn, create_tcp_conn, CarControl, fetch_status

class App:
    def __init__(self, root):
        self.initControllerKeyboard()
        
        self.initValues()

        self.ip = None
        self.udp = None
        self.tcp =None
        #setting title
        root.title("undefined")

        self.root = root

        #setting window size
        width=1000
        height=1000
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.initSteerUI(root)
        self.initSpeedUI(root)
        self.initHeadlightUI(root)
        self.initRearlightUI(root)

        #self.initZQSDUI(root)

        self.initAccelerometerUI(root)        
        self.initGyroscopeUI(root)        

        self.initBatteryUI(root)        
        self.initBlinkerUI(root)        
        self.initRSSIUI(root)        

        self.initCarSelectUI(root)
        self.bindings(root)

        self.threadCommand()
        print("startUI")
        self.threadUI()

    def initControllerKeyboard(self):
        self.throttle = 0
        self.steer = 0
        self.engine = False

    def initValues(self):
        self.headlight = 0
        self.rearlight = "#1c7bd9"
        self.tmpBlinker = tk.IntVar()

        self.rssi = 0
        self.batterySOC = 0
        self.batteryADC = 0

        self.accelerometerX = 0
        self.accelerometerY = 0
        self.accelerometerZ = 0
        
        self.gyroscopeX = 0
        self.gyroscopeY = 0
        self.gyroscopeZ = 0

        self.carList = tabName

        self.selectedCar = tk.StringVar()
        self.selectedCar.set(None) # default value

        self.SPEED_MAX = 8192
        self.SPEED_MIN = -8192
        self.STEER_MAX = 32768
        self.STEER_MIN = -32768
        self.HEADLIGHT_MIN = 0
        self.HEADLIGHT_MAX = 65535

        print('Finished initValues')

    def bindings(self,root):
        #root.bind('<KeyRelease-a>', lambda event: print("release"))
        root.bind('z', lambda event: self.throttleIncrease())
        root.bind('s', lambda event: self.throttleDecrease())

        root.bind('t', lambda event: self.startEngine())
        root.bind('y', lambda event: self.stopEngine())

        root.bind('e', lambda event: self.setStop())
        root.bind('q', lambda event: self.steerLeft())
        root.bind('d', lambda event: self.steerRight())
        root.bind('p', lambda event: self.headlightUp())
        root.bind('m', lambda event: self.headlightDown())


    ##################################################
    ##################################################
    ### ZQSD DISPLAY
    ##################################################
    ##################################################

    def initZQSDUI(self, root):
        ButtonLeft=tk.Button(root)
        ButtonLeft["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ButtonLeft["font"] = ft
        ButtonLeft["fg"] = "#000000"
        ButtonLeft["justify"] = "center"
        ButtonLeft["text"] = "Left"
        ButtonLeft.place(x=50,y=320,width=70,height=25)
        ButtonLeft["command"] = self.ButtonLeft_command

        ButtonForward=tk.Button(root)
        ButtonForward["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ButtonForward["font"] = ft
        ButtonForward["fg"] = "#000000"
        ButtonForward["justify"] = "center"
        ButtonForward["text"] = "Forward"
        ButtonForward.place(x=120,y=290,width=70,height=25)
        ButtonForward["command"] = self.ButtonForward_command

        ButtonRight=tk.Button(root)
        ButtonRight["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ButtonRight["font"] = ft
        ButtonRight["fg"] = "#000000"
        ButtonRight["justify"] = "center"
        ButtonRight["text"] = "Right"
        ButtonRight.place(x=190,y=320,width=70,height=25)
        ButtonRight["command"] = self.ButtonRight_command

        ButtonBackward=tk.Button(root)
        ButtonBackward["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ButtonBackward["font"] = ft
        ButtonBackward["fg"] = "#000000"
        ButtonBackward["justify"] = "center"
        ButtonBackward["text"] = "Backward"
        ButtonBackward.place(x=120,y=350,width=70,height=25)
        ButtonBackward["command"] = self.ButtonBackward_command

    def ButtonLeft_command(self):
        print("command")

    def ButtonForward_command(self):
        print("command")

    def ButtonRight_command(self):
        print("command")

    def ButtonBackward_command(self):
        print("command")

    ##################################################
    ##################################################
    ### SPEED DISPLAY
    ##################################################
    ##################################################

    def initSpeedUI(self, root):
        LabelEngine=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        LabelEngine["font"] = ft
        LabelEngine["fg"] = "#333333"
        LabelEngine["justify"] = "center"
        LabelEngine["text"] = "Engine"
        LabelEngine.place(x=0,y=10,width=100,height=25)

        ButtonEngine=tk.Button(root)
        ButtonEngine["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ButtonEngine["font"] = ft
        ButtonEngine["fg"] = "#000000"
        ButtonEngine["justify"] = "center"
        ButtonEngine["text"] = "On"
        ButtonEngine.place(x=100,y=10,width=50,height=20)
        ButtonEngine["command"] = self.ButtonEngineOn_command

        ButtonEngine=tk.Button(root)
        ButtonEngine["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ButtonEngine["font"] = ft
        ButtonEngine["fg"] = "#000000"
        ButtonEngine["justify"] = "center"
        ButtonEngine["text"] = "Off"
        ButtonEngine.place(x=150,y=10,width=50,height=20)
        ButtonEngine["command"] = self.ButtonEngineOff_command

        self.LabelEngine=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelEngine["font"] = ft
        self.LabelEngine["fg"] = "#333333"
        self.LabelEngine["justify"] = "center"
        self.LabelEngine["text"] = "Engine status: "
        self.LabelEngine.place(x=200,y=10,width=100,height=25)

        self.ScaleSpeed=tk.Scale(root)
        ft = tkFont.Font(family='Times',size=10)
        self.ScaleSpeed["from"] = -100
        self.ScaleSpeed["to"] = 100
        self.ScaleSpeed["label"] = "Speed"
        self.ScaleSpeed["tickinterval"] = 10
        self.ScaleSpeed["orient"] = tk.HORIZONTAL
        self.ScaleSpeed.place(x=400,y=110,width=300,height=100)

        self.LabelSpeed=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelSpeed["font"] = ft
        self.LabelSpeed["fg"] = "#333333"
        self.LabelSpeed["justify"] = "center"
        self.LabelSpeed["text"] = "Speed: "
        self.LabelSpeed.place(x=50,y=30,width=100,height=25)


    def updateSpeedUI(self, throttle):
        self.LabelSpeed["text"] = "Speed: " + str(int(throttle))
        self.ScaleSpeed.set(throttle * 100 / self.SPEED_MAX)

    def updateEngineUI(self, engine):
        self.LabelEngine["text"] = "Engine status: " + str(engine)
    
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

    def ButtonEngineOn_command(self):
        self.carControl.engine_on()

    def ButtonEngineOff_command(self):
        self.carControl.engine_off()

    ##################################################
    ##################################################
    ### STEER DISPLAY
    ##################################################
    ##################################################

    def initSteerUI(self, root):
        self.ScaleSteering=tk.Scale(root)
        ft = tkFont.Font(family='Times',size=10)
        self.ScaleSteering["from"] = -180
        self.ScaleSteering["to"] = 180
        self.ScaleSteering["label"] = "Steering"
        self.ScaleSteering["tickinterval"] = 10
        self.ScaleSteering["orient"] = tk.HORIZONTAL
        self.ScaleSteering.place(x=400,y=10,width=300,height=100)

        self.LabelSteer=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelSteer["font"] = ft
        self.LabelSteer["fg"] = "#333333"
        self.LabelSteer["justify"] = "center"
        self.LabelSteer["text"] = "Steer: "
        self.LabelSteer.place(x=50,y=60,width=100,height=25)

    def updateSteerUI(self, steering):
        self.LabelSteer["text"] = "Steer: " + str(int(steering))
        self.ScaleSteering.set(steering * 180 / self.STEER_MAX)

    def steerRight(self):
        self.steer = min(self.STEER_MAX, self.steer + 3276.8)

    def steerLeft(self):
        self.steer = max(self.STEER_MIN, self.steer - 3276.8)

    ##################################################
    ##################################################
    ### HEADLIGHT DISPLAY
    ##################################################
    ##################################################

    def initHeadlightUI(self, root):
        self.ScaleHeadlight=tk.Scale(root)
        ft = tkFont.Font(family='Times',size=10)
        self.ScaleHeadlight["from"] = 0
        self.ScaleHeadlight["to"] = 100
        self.ScaleHeadlight["label"] = "Headlight Power"
        self.ScaleHeadlight["tickinterval"] = 10
        self.ScaleHeadlight["orient"] = tk.HORIZONTAL
        self.ScaleHeadlight.place(x=400,y=210,width=300,height=100)
        self.ScaleHeadlight["command"] = self.ScaleHeadlight_command

        self.LabelHeadlight=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelHeadlight["font"] = ft
        self.LabelHeadlight["fg"] = "#333333"
        self.LabelHeadlight["justify"] = "center"
        self.LabelHeadlight["text"] = "Headlight: "
        self.LabelHeadlight.place(x=50,y=90,width=100,height=25)

    def updateHeadlightUI(self, headlight):
        self.LabelHeadlight["text"] = "Headlight: " + str(int(headlight))
        self.ScaleHeadlight.set(headlight * 100 / self.HEADLIGHT_MAX)

    def headlightUp(self):
        #self.headlight = min(self.HEADLIGHT_MAX, self.headlight + 6553.5)
        #self.updateHeadlightUI()
        self.carControl.set_headlights(int(min(self.HEADLIGHT_MAX, self.headlight + 6553.5)))

    def headlightDown(self):
        #self.headlight = max(self.HEADLIGHT_MIN, self.headlight - 6553.5)
        #self.updateHeadlightUI()
        self.carControl.set_headlights(int(max(self.HEADLIGHT_MIN, self.headlight - 6553.5)))

    # UI Scale
    def ScaleHeadlight_command(self, value):
        #self.headlight=int(value) * self.HEADLIGHT_MAX / 100
        #self.updateHeadlightUI()
        self.carControl.set_headlights(int(int(value) * self.HEADLIGHT_MAX / 100))

    ##################################################
    ##################################################
    ### REARLIGHT DISPLAY
    ##################################################
    ##################################################

    def initRearlightUI(self, root):
        self.LabelColorRear=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelColorRear["font"] = ft
        self.LabelColorRear["bg"] = self.rearlight
        self.LabelColorRear["justify"] = "center"
        self.LabelColorRear["text"] = self.rearlight
        self.LabelColorRear.place(x=50,y=120,width=100,height=25)

        ButtonColorChooser=tk.Button(root)
        ButtonColorChooser["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ButtonColorChooser["font"] = ft
        ButtonColorChooser["fg"] = "#000000"
        ButtonColorChooser["justify"] = "center"
        ButtonColorChooser["text"] = "RearLight Color"
        ButtonColorChooser.place(x=175,y=120,width=100,height=25)
        ButtonColorChooser["command"] = self.ButtonColorChooser_command

    def updateRearlightUI(self, rearlight):
        self.LabelColorRear.configure(bg=rearlight)
        self.LabelColorRear["text"] = rearlight

    def ButtonColorChooser_command(self):
        #self.rearlight = askcolor(title="Tkinter Color Chooser")[1]
        #self.updateRearlightUI()
        r, g, b = askcolor(title="Tkinter Color Chooser")[0]

        self.carControl.set_color(int(r), int(g), int(b))

    ##################################################
    ##################################################
    ### Accelerometer 
    ##################################################
    ##################################################

    def initAccelerometerUI(self, root):
        LabelAccelerometer=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        LabelAccelerometer["font"] = ft
        LabelAccelerometer["justify"] = "center"
        LabelAccelerometer["text"] = "Accelerometer"
        LabelAccelerometer.place(x=700,y=10,width=100,height=25)

        self.LabelAccelerometerX=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelAccelerometerX["font"] = ft
        self.LabelAccelerometerX["justify"] = "center"
        self.LabelAccelerometerX["text"] = "X: "
        self.LabelAccelerometerX.place(x=720,y=35,width=100,height=25)

        self.LabelAccelerometerY=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelAccelerometerY["font"] = ft
        self.LabelAccelerometerY["justify"] = "center"
        self.LabelAccelerometerY["text"] = "Y: "
        self.LabelAccelerometerY.place(x=720,y=60,width=100,height=25)

        self.LabelAccelerometerZ=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelAccelerometerZ["font"] = ft
        self.LabelAccelerometerZ["justify"] = "center"
        self.LabelAccelerometerZ["text"] = "Z: "
        self.LabelAccelerometerZ.place(x=720,y=85,width=100,height=25)
    
    def updateAccelerometerUI(self, x, y, z):
        self.LabelAccelerometerX["text"] = x
        self.LabelAccelerometerY["text"] = y
        self.LabelAccelerometerZ["text"] = z

    ##################################################
    ##################################################
    ### Gyroscope 
    ##################################################
    ##################################################

    def initGyroscopeUI(self, root):
        LabelGyroscope=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        LabelGyroscope["font"] = ft
        LabelGyroscope["justify"] = "center"
        LabelGyroscope["text"] = "Gyroscope"
        LabelGyroscope.place(x=700,y=110,width=100,height=25)

        self.LabelGyroscopeX=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelGyroscopeX["font"] = ft
        self.LabelGyroscopeX["justify"] = "center"
        self.LabelGyroscopeX["text"] = "X: "
        self.LabelGyroscopeX.place(x=720,y=135,width=100,height=25)

        self.LabelGyroscopeY=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelGyroscopeY["font"] = ft
        self.LabelGyroscopeY["justify"] = "center"
        self.LabelGyroscopeY["text"] = "Y: "
        self.LabelGyroscopeY.place(x=720,y=160,width=100,height=25)

        self.LabelGyroscopeZ=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelGyroscopeZ["font"] = ft
        self.LabelGyroscopeZ["justify"] = "center"
        self.LabelGyroscopeZ["text"] = "Z: "
        self.LabelGyroscopeZ.place(x=720,y=185,width=100,height=25)

    def updateGyroscopeUI(self, x, y ,z):
        self.LabelGyroscopeX["text"] = x
        self.LabelGyroscopeY["text"] = y
        self.LabelGyroscopeZ["text"] = z

    ##################################################
    ##################################################
    ### RSSI 
    ##################################################
    ##################################################

    def initRSSIUI(self, root):
        LabelRSSI=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        LabelRSSI["font"] = ft
        LabelRSSI["justify"] = "center"
        LabelRSSI["text"] = "RSSI: "
        LabelRSSI.place(x=700,y=210,width=100,height=25)

        self.LabelRSSIValue=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelRSSIValue["font"] = ft
        self.LabelRSSIValue["justify"] = "center"
        self.LabelRSSIValue["text"] = "0"
        self.LabelRSSIValue.place(x=800,y=210,width=100,height=25)

    def updateRSSIUI(self):
        self.LabelRSSIValue["text"] = self.rssi

    ##################################################
    ##################################################
    ### Car select 
    ##################################################
    ##################################################

    def initCarSelectUI(self, root):
        LabelCarSelection=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        LabelCarSelection["font"] = ft
        LabelCarSelection["justify"] = "center"
        LabelCarSelection["text"] = "Select a car: "
        LabelCarSelection.place(x=50,y=200,width=100,height=25)

        OptionMenuCarSelect = tk.OptionMenu(root, self.selectedCar, *(self.carList), command = self.OptionMenuCarSelect_command)
        OptionMenuCarSelect.place(x=150,y=200,width=100,height=25)

        self.LabelCarSelection=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelCarSelection["font"] = ft
        self.LabelCarSelection["justify"] = "center"
        self.LabelCarSelection["text"] = "Connected to: " + self.selectedCar.get()
        self.LabelCarSelection.place(x=100,y=230,width=110,height=25)        

    def updateRSSIUI(self, rssi):
        self.LabelRSSIValue["text"] = rssi

    def OptionMenuCarSelect_command(self, value):
        self.LabelCarSelection["text"] = "Connected to: " + self.selectedCar.get()

        for e in tab:
            if e[0] == self.selectedCar.get():
                self.ip = e[1]
                self.udp = create_udp_conn(e[1])
                self.tcp = create_tcp_conn(self.udp, b"\x00"*6)
                self.carControl = CarControl(self.udp, self.tcp, 2, b"\x00"*6)
                
                print("set ip: " + str(self.ip))



    ##################################################
    ##################################################
    ### Battery 
    ##################################################
    ##################################################
    
    def initBatteryUI(self, root):
        LabelBatteryADC=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        LabelBatteryADC["font"] = ft
        LabelBatteryADC["justify"] = "center"
        LabelBatteryADC["text"] = "Battery ADC"
        LabelBatteryADC.place(x=50,y=150,width=100,height=25)

        self.ProgressBatteryADC=ttk.Progressbar(root)
        self.ProgressBatteryADC["orient"] = tk.HORIZONTAL
        self.ProgressBatteryADC.place(x=150, y=150, width=100)

        LabelBatterySOC=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        LabelBatterySOC["font"] = ft
        LabelBatterySOC["justify"] = "center"
        LabelBatterySOC["text"] = "Battery SOC"
        LabelBatterySOC.place(x=50,y=175,width=100,height=25)

        self.ProgressBatterySOC=ttk.Progressbar(root)
        self.ProgressBatterySOC["orient"] = tk.HORIZONTAL
        self.ProgressBatterySOC.place(x=150, y=175, width=100)

    def updateBatteryUI(self, adc, soc):
        self.ProgressBatteryADC["value"] = adc
        self.ProgressBatterySOC["value"] = soc

    ##################################################
    ##################################################
    ### Blinker 
    ##################################################
    ##################################################
    def initBlinkerUI(self, root):
        self.CheckBoxBlinker=tk.Checkbutton(root)
        ft = tkFont.Font(family='Times',size=10)
        self.CheckBoxBlinker["font"] = ft
        self.CheckBoxBlinker["fg"] = "#333333"
        self.CheckBoxBlinker["justify"] = "center"
        self.CheckBoxBlinker["text"] = "Blinkers"
        self.CheckBoxBlinker.place(x=400,y=310,width=100,height=25)
        self.CheckBoxBlinker["offvalue"] = "0"
        self.CheckBoxBlinker["onvalue"] = "1"
        self.CheckBoxBlinker["command"] = self.CheckBoxBlinker_command
        self.CheckBoxBlinker["variable"] = self.tmpBlinker

        self.LabelBlinkerValue=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelBlinkerValue["font"] = ft
        self.LabelBlinkerValue["justify"] = "center"
        self.LabelBlinkerValue["text"] = "Blinker: "
        self.LabelBlinkerValue.place(x=500,y=310,width=100,height=25)
        
    def updateBlinkerInfo(self):
        self.LabelBlinkerValue["text"] = "Blinker: "
    
    def CheckBoxBlinker_command(self):
        print(self.tmpBlinker.get())
        #if (self.tmpBlinker.get() == 1):
            #self.CheckBoxBlinker.select()
            #self.blinker = True
        #else:
            #self.blinker = False
            #self.CheckBoxBlinker.deselect()

        self.updateBlinkerInfo()

    ##################################################
    ##################################################
    ### Other 
    ##################################################
    ##################################################
    def upadteUI(self):
        while(True):
            if(self.ip != None):
                status = fetch_status(self.ip)

                self.updateEngineUI(status.started)
                self.updateSteerUI(status.steering)
                self.updateSpeedUI(status.throttle)
                self.updateHeadlightUI(status.headlights)
                self.updateRearlightUI('#%02x%02x%02x' % (status.r, status.g, status.b))


                self.updateAccelerometerUI(status.imu_xl_x, status.imu_xl_y, status.imu_xl_z)
                self.updateGyroscopeUI(status.imu_g_x, status.imu_g_y, status.imu_g_z)

                self.updateBlinkerInfo()
                self.updateBatteryUI(status.batt_adc, status.batt_soc)
                self.updateRSSIUI(status.rssi)

    def updateValues(self):
        while(True):
            ## Retrieve new values

            if(self.ip != None):
                if(self.engine):        
                    #print("pilot" + str(self.throttle) + "," +  str(self.steer))
                    self.carControl.pilot(self.throttle, self.steer)

                #self.rearlight = '#%02x%02x%02x' % (status.disp_r, status.disp_g, status.disp_b)
            time.sleep(0.05)
    
    def threadCommand(self):
        t1=Thread(target=self.updateValues)
        t1.start()

    def threadUI(self):
        t1=Thread(target=self.upadteUI)
        t1.start()

tabName = []
tab = []
class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        tabName.append(name.split('.')[0])
        tab.append((name.split('.')[0], ".".join(str(val) for val in [info.addresses[0][i] for i in range(0, len(info.addresses[0]))])))

if __name__ == "__main__":
    
    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_carnode._udp.local.", listener)
    print("getting cars list...")
    time.sleep(10)
    print(tab)


    root = tk.Tk()
    app = App(root)

    ##############################
    # car.py    
    ##############################

    
    ##############################
    # Start Video
    ##############################
    #cap = cv2.VideoCapture(0)
    #lmain = tk.Label(root)
    #lmain.place(x=10,y=500,width=1000,height=500)
    #video_stream()



    
    root.mainloop()