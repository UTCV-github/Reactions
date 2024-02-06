import tkinter
import tkinter.messagebox
import customtkinter
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog
from PIL import Image
from CTkTable import *
import time
import platform
import serial
import serial.tools.list_ports
from Global_var import status

class Configure_Arduino(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("Arduino Configuration")
        self.geometry("400x400")
        self.after(10, self.lift) # Add this to keep the new window float atop

        # Configure the Arduino
        CurrentOS = platform.system()

        if CurrentOS == "Windows":
            # Configure the serial port that connects the Arduino
            ports = serial.tools.list_ports.comports() # Get a COM port list
            ports_list = []
            for port, desc, hwid in sorted(ports): # Get all COM port name
                ports_list.append("{}: {}".format(port, desc))
            Arduino_eqip_list = ['Arduino Uno', 'Arduino Nano']
            Arduino_port = [s for s in ports_list if any(ports_list in s for ports_list in Arduino_eqip_list)] # Pick up the ports that are connected to a Arduino device
            
                
        elif CurrentOS == "Darwin":
            ports = serial.tools.list_ports.comports() # Get a COM port list
            ports_list = []
            for port, desc, hwid in sorted(ports): # Get all COM port name
                ports_list.append("{}: {}".format(port, desc))
            Arduino_port = ['']


        self.Cfg_Arduino_COM_label = customtkinter.CTkLabel(self, text="Select a COM port or input a COM port", anchor="w")
        self.Cfg_Arduino_COM_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.Cfg_Arduino_COM_Menu = customtkinter.CTkOptionMenu(self, values=ports_list, command=None)
        self.Cfg_Arduino_COM_Menu.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="nsew")
        if len(Arduino_port) > 0:   # In case no Arduino board is connected (Arduino_port has 0 element)
            self.Cfg_Arduino_COM_Menu.set(Arduino_port[0])

        self.COM_input = customtkinter.CTkEntry(self)
        self.COM_input.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.Cfg_Arduino_Baud_label = customtkinter.CTkLabel(self, text="Select a baud rate", anchor="w")
        self.Cfg_Arduino_Baud_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nsew")

        ls_Baud_rate = ["300", "600", "1200", "2400", "4800", "9600", "14400", "19200", "28800", "31250", "38400", "57600", "115200"] # Has to be a list of strings
        self.Cfg_Arduino_Baud_Menu = customtkinter.CTkOptionMenu(self, values=ls_Baud_rate, command=None)
        self.Cfg_Arduino_Baud_Menu.grid(row=4, column=0, padx=10, pady=(5, 0), sticky="nsew")
        self.Cfg_Arduino_Baud_Menu.set("9600")

        # self.grid_rowconfigure(5, weight=1)

        self.Cfg_Arduino_Connect = customtkinter.CTkButton(self, text="Connect Arduino", anchor="w", command=self.Connect_Arduino)
        self.Cfg_Arduino_Connect.grid(row=6, column=0, padx=10, pady=(20, 0), sticky="nsew")

    def Connect_Arduino(self):
        COM_port = self.Cfg_Arduino_COM_Menu.get()
        Baud = int(self.Cfg_Arduino_Baud_Menu.get())
        CurrentOS = platform.system()
        if CurrentOS == "Windows":
            COM_port = COM_port.split(":")[0]
        elif CurrentOS == "Darwin":
            COM_port = COM_port.split(":")[0]

        if self.COM_input.get() != '':
            COM_port = self.COM_input.get()

        ser = serial.Serial(COM_port, Baud, timeout=1)
        status.ser = ser
        time.sleep(1) # Pause for 1 sencond to wait for response from the Arduino

        # Detect if the sensor is connected properly
        msg = ser.readline()
        print(msg)
        if msg.decode('utf-8').rstrip() == 'Found sensor':
            msg_popup = CTkMessagebox(title="Found sensor", message="Colour sensor detected!", 
                                      icon="check", option_1="OK")
            status.Arduino_connection = True    # Change global variable
            status.Arduino_connection_real = True

        else: 
            msg_popup = CTkMessagebox(title="Sensor Error", message="Colour sensor cannot be detected!", 
                                      icon="warning", option_1="OK", option_2="Retry")
            if msg_popup.get() == "Retry":
                self.Connect_Arduino()