import tkinter as tk
import tkinter.font as tkFont
from tkinter.colorchooser import askcolor
from tkinter import ttk
from PIL import ImageTk, Image
import cv2

class App:
    def __init__(self, root):
        
        self.initValues()
        
        #setting title
        root.title("undefined")

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

        self.initZQSDUI(root)

        self.initAccelerometerUI(root)        
        self.initGyroscopeUI(root)        

        self.initBatteryUI(root)        
        self.initBlinkerUI(root)        
        self.initRSSIUI(root)        

        self.bindings(root)

    def initValues(self):
        self.speed = 0
        self.steer = 0
        self.headlight = 0
        self.rearlight = "#1c7bd9"
        self.blinker = False
        self.tmpBlinker = tk.IntVar()
        
        self.SPEED_MAX = 8192
        self.SPEED_MIN = -8192
        self.STEER_MAX = 32768
        self.STEER_MIN = -32768
        self.HEADLIGHT_MIN = 0
        self.HEADLIGHT_MAX = 65535

    def bindings(self,root):
        root.bind('a', lambda event: self.setForward())
        root.bind('e', lambda event: self.setStop())
        root.bind('z', lambda event: self.speedIncrease())
        root.bind('q', lambda event: self.steerLeft())
        root.bind('s', lambda event: self.speedDecrease())
        root.bind('d', lambda event: self.steerRight())
        root.bind('p', lambda event: self.headlightUp())
        root.bind('m', lambda event: self.headlightDown())

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


    ##################################################
    ##################################################
    ### SPEED DISPLAY
    ##################################################
    ##################################################

    def initSpeedUI(self, root):
        self.ScaleSpeed=tk.Scale(root)
        ft = tkFont.Font(family='Times',size=10)
        self.ScaleSpeed["from"] = -100
        self.ScaleSpeed["to"] = 100
        self.ScaleSpeed["label"] = "Speed"
        self.ScaleSpeed["tickinterval"] = 10
        self.ScaleSpeed["orient"] = tk.HORIZONTAL
        self.ScaleSpeed.place(x=400,y=110,width=300,height=100)
        self.ScaleSpeed["command"] = self.ScaleSpeed_command

        self.LabelSpeed=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelSpeed["font"] = ft
        self.LabelSpeed["fg"] = "#333333"
        self.LabelSpeed["justify"] = "center"
        self.LabelSpeed["text"] = "Speed: " + str(self.speed)
        self.LabelSpeed.place(x=50,y=30,width=100,height=25)


    def updateSpeedInfo(self):
        self.LabelSpeed["text"] = "Speed: " + str(int(self.speed))
        self.ScaleSpeed.set(self.speed * 100 / self.SPEED_MAX)
    
    def speedIncrease(self):
        self.speed = min(self.SPEED_MAX, self.speed + 819.2)
        self.updateSpeedInfo()

    def speedDecrease(self):
        self.speed = max(self.SPEED_MIN, self.speed - 819.2)
        self.updateSpeedInfo()

    def setForward(self):
        self.speed = 2048
        self.updateSpeedInfo()

    def setStop(self):
        self.speed = 0
        self.updateSpeedInfo()

    # UI Scale
    def ScaleSpeed_command(self, value):
        self.speed=int(value) * self.SPEED_MAX / 100
        self.updateSpeedInfo()

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
        self.ScaleSteering["command"] = self.ScaleSteering_command

        self.LabelSteer=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.LabelSteer["font"] = ft
        self.LabelSteer["fg"] = "#333333"
        self.LabelSteer["justify"] = "center"
        self.LabelSteer["text"] = "Steer: " + str(self.steer)
        self.LabelSteer.place(x=50,y=60,width=100,height=25)

    def updateSteerInfo(self):
        self.LabelSteer["text"] = "Steer: " + str(int(self.steer))
        self.ScaleSteering.set(self.steer * 180 / self.STEER_MAX)

    def steerRight(self):
        self.steer = min(self.STEER_MAX, self.steer + 3276.8)
        self.updateSteerInfo()

    def steerLeft(self):
        self.steer = max(self.STEER_MIN, self.steer - 3276.8)
        self.updateSteerInfo()

    # UI Scale
    def ScaleSteering_command(self, value: int):
        self.steer=int(value) * self.STEER_MAX / 180
        self.updateSteerInfo()



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
        self.LabelHeadlight["text"] = "Headlight: " + str(self.steer)
        self.LabelHeadlight.place(x=50,y=90,width=100,height=25)

    def updateHeadlightInfo(self):
        self.LabelHeadlight["text"] = "Headlight: " + str(int(self.headlight))
        self.ScaleHeadlight.set(self.headlight * 100 / self.HEADLIGHT_MAX)

    def headlightUp(self):
        self.headlight = min(self.HEADLIGHT_MAX, self.headlight + 6553.5)
        self.updateHeadlightInfo()

    def headlightDown(self):
        self.headlight = max(self.HEADLIGHT_MIN, self.headlight - 6553.5)
        self.updateHeadlightInfo()

    # UI Scale
    def ScaleHeadlight_command(self, value):
        self.headlight=int(value) * self.HEADLIGHT_MAX / 100
        self.updateHeadlightInfo()

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

    def updateRearlightInfo(self):
        self.LabelColorRear.configure(bg=self.rearlight)
        self.LabelColorRear["text"] = self.rearlight


    def ButtonColorChooser_command(self):
        self.rearlight = askcolor(title="Tkinter Color Chooser")[1]
        self.updateRearlightInfo()

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
    
    def updateAccelerometerInfo(self, x, y, z):
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

    def updateGyroscopeInfo(self, x, y, z):
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

    def updateRSSIInfo(self, value):
        self.LabelRSSIValue["text"] = value


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

        ProgressBatteryADC=ttk.Progressbar(root)
        ProgressBatteryADC["orient"] = tk.HORIZONTAL
        ProgressBatteryADC.place(x=150, y=150, width=100)

        LabelBatterySOC=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        LabelBatterySOC["font"] = ft
        LabelBatterySOC["justify"] = "center"
        LabelBatterySOC["text"] = "Battery SOC"
        LabelBatterySOC.place(x=50,y=175,width=100,height=25)

        ProgressBatterySOC=ttk.Progressbar(root)
        ProgressBatterySOC["orient"] = tk.HORIZONTAL
        ProgressBatterySOC.place(x=150, y=175, width=100)


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
        self.LabelBlinkerValue["text"] = "Blinker: " + str(self.blinker)
        self.LabelBlinkerValue.place(x=500,y=310,width=100,height=25)
        
    def updateBlinkerInfo(self):
        self.LabelBlinkerValue["text"] = "Blinker: " + str(self.blinker)
    
    def CheckBoxBlinker_command(self):
        print(self.tmpBlinker.get())
        if (self.tmpBlinker.get() == 1):
            #self.CheckBoxBlinker.select()
            print("setToTrue")
            self.blinker = True
        else:
            print("setToFalse")
            self.blinker = False
            #self.CheckBoxBlinker.deselect()

        self.updateBlinkerInfo()

    ##################################################
    ##################################################
    ### Other 
    ##################################################
    ##################################################

    def ButtonLeft_command(self):
        print("command")

    def ButtonForward_command(self):
        print("command")

    def ButtonRight_command(self):
        print("command")


    def ButtonBackward_command(self):
        print("command")

    def CheckBoxHeadLight_command(self):
        print("command")

    

# function for video streaming
def video_stream():

    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(1, video_stream) 

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    # Capture from camera
    cap = cv2.VideoCapture(0)

    lmain = tk.Label(root)
    lmain.place(x=10,y=500,width=1000,height=500)

    video_stream()
    
    root.mainloop()
