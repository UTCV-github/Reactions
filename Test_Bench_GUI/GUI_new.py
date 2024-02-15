import serial
import serial.tools.list_ports
import time
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tkinter
import tkinter.messagebox
import customtkinter
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog
from PIL import Image
from CTkTable import *
import time
import platform
from Configure_Arduino import Configure_Arduino
from Global_var import status
import re
import threading
from Output import OutputProcess
from Arduino import Arduino
import queue
import os
from Result import result

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

#Initialize status variables
status.Arduino_connection_real = False
status.Arduino_connection = False
status.ser = None
status.TestMode = False
Output = pd.DataFrame()
Output_previous = pd.DataFrame()

class RGBC_switch(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.switch_r = customtkinter.CTkSwitch(self, text="R value")
        self.switch_r.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.switch_g = customtkinter.CTkSwitch(self, text="G value")
        self.switch_g.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        self.switch_b = customtkinter.CTkSwitch(self, text="B value")
        self.switch_b.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        self.switch_c = customtkinter.CTkSwitch(self, text="C value")
        self.switch_c.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")

        self.button_save = customtkinter.CTkButton(self, text="SAVE", command=self.save_data, hover = True)
        self.button_save.grid(row=8, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def get(self):
        ls_sensor_readings = []
        if self.switch_r.get() == 1:
            ls_sensor_readings.append(self.switch_r.cget("text"))
        if self.switch_g.get() == 1:
            ls_sensor_readings.append(self.switch_g.cget("text"))
        if self.switch_b.get() == 1:
            ls_sensor_readings.append(self.switch_b.cget("text"))
        if self.switch_c.get() == 1:
            ls_sensor_readings.append(self.switch_c.cget("text"))
        return ls_sensor_readings
    
    def show_warning(self):
    # Show some retry/cancel warnings
        msg = CTkMessagebox(title="System Error", message="No data to be saved!",
                    icon="warning", option_1="Cancel", option_2="Retry")
    
        if msg.get()=="Retry":
            self.show_warning()

    def save_msg(self):
        msg = CTkMessagebox(title="Data Saved", message="Data successfully saved!",
                    icon="check", option_1="OK")

    def save_data(self):
        if not result.Output_save.empty:
            os.makedirs('Saved_data', exist_ok=True)
            now = datetime.now()
            date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
            file_name =  os.path.dirname(__file__) + "/Saved_data/Cache_" + date_time + ".csv"
            result.Output_save.to_csv(file_name, index = False)
            if os.path.exists(file_name):
                self.save_msg()
        else:
            self.show_warning()

    
class MB_window(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.button_Arduino_config = customtkinter.CTkButton(self, text="Arduino Configuration", command=Configure_Arduino)
        self.button_Arduino_config.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")

        self.button_file = customtkinter.CTkButton(self, text="select file", command=self.selectfile)
        self.button_file.grid(row=1, column=0, padx=10, pady=(10,0), sticky="ew")

        self.entry_file = customtkinter.CTkEntry(self, placeholder_text="Save data file at ...")
        self.entry_file.grid(row=1, column=1, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="nsew")

        self.label_TestBench = customtkinter.CTkLabel(self, text="Select a test bench", anchor="w")
        self.label_TestBench.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_TestBench = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["A: test bench", "B: car", "C"])
        self.optionmenu_TestBench.grid(row=3, column=0, padx=10, pady=(0, 10))

        self.label_KohConc = customtkinter.CTkLabel(self, text="Input the KOH concentration", anchor="w")
        self.label_KohConc.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_KohConc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_KohConc.grid(row=5, column=0, padx=10, pady=(0, 10))

        self.entry_KohConc = customtkinter.CTkEntry(self, placeholder_text="KOH concentration")
        self.entry_KohConc.grid(row=5, column=1, columnspan=2, padx=(20, 0), pady=(0, 10), sticky="nsew")

        self.button_run = customtkinter.CTkButton(self, text="RUN", command=self.show_warning, hover = True)
        self.button_run.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_showresult = customtkinter.CTkButton(self, text="SHOW RESULT", command=None, hover = True)
        self.button_showresult.grid(row=7, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_pause = customtkinter.CTkButton(self, text="PAUSE", command=self.show_warning, hover = True)
        self.button_pause.grid(row=8, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_reset = customtkinter.CTkButton(self, text="RESET", command=self.show_warning, hover = True)
        self.button_reset.grid(row=9, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def show_warning(self):
    # Show some retry/cancel warnings
        msg = CTkMessagebox(title="Sensor Error", message="Colour sensor cannot be detected!",
                    icon="warning", option_1="Cancel", option_2="Retry")
    
        if msg.get()=="Retry":
            self.show_warning()

    def selectfile(self):
        filename = filedialog.askopenfilename()
        print(filename)


class Chameleon_window(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.new_window = None

        self.button_Arduino_config = customtkinter.CTkButton(self, text="Arduino Configuration", command=Configure_Arduino)
        self.button_Arduino_config.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")

        self.button_file = customtkinter.CTkButton(self, text="select file", command=self.selectfile)
        self.button_file.grid(row=1, column=0, padx=10, pady=(10,0), sticky="ew")

        self.entry_file = customtkinter.CTkEntry(self, placeholder_text="Save data file at ...")
        self.entry_file.grid(row=1, column=1, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="nsew")

        self.label_TestBench = customtkinter.CTkLabel(self, text="Select a test bench", anchor="w")
        self.label_TestBench.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_TestBench = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["A: test bench", "B: car", "C"])
        self.optionmenu_TestBench.grid(row=3, column=0, padx=10, pady=(0, 10))

        self.label_KohConc = customtkinter.CTkLabel(self, text="Input the KOH concentration", anchor="w")
        self.label_KohConc.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_KohConc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_KohConc.grid(row=5, column=0, padx=10, pady=(0, 10))

        self.entry_KohConc = customtkinter.CTkEntry(self, placeholder_text="KOH concentration")
        self.entry_KohConc.grid(row=5, column=1, columnspan=2, padx=(20, 0), pady=(0, 10), sticky="nsew")

        self.label_DexConc = customtkinter.CTkLabel(self, text="Input the Dextrose concentration", anchor="w")
        self.label_DexConc.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_DexConc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_DexConc.grid(row=7, column=0, padx=10, pady=(0, 10))

        self.entry_DexConc = customtkinter.CTkEntry(self, placeholder_text="Dex concentration")
        self.entry_DexConc.grid(row=7, column=1, columnspan=2, padx=(20, 0), pady=(0, 10), sticky="nsew")

        self.label_Kmno4Conc = customtkinter.CTkLabel(self, text="Input the KMnO\u2084 concentration", anchor="w")
        self.label_Kmno4Conc.grid(row=8, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_Kmno4Conc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/500mL", "g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_Kmno4Conc.grid(row=9, column=0, padx=10, pady=(0, 20))

        self.entry_Kmno4Conc = customtkinter.CTkEntry(self, placeholder_text="KMnO\u2084 concentration")
        self.entry_Kmno4Conc.grid(row=9, column=1, columnspan=2, padx=(20, 0), pady=(0, 20), sticky="nsew")

        self.button_run = customtkinter.CTkButton(self, text="RUN", command=self.RunReaction, hover = True)
        self.button_run.grid(row=10, column=0, columnspan=3, rowspan=2, padx=10, pady=5, sticky="ew")
        self.grid_rowconfigure(11, weight=1)

        self.button_showresult = customtkinter.CTkButton(self, text="DISPLAY GRAPH", command=self.DisplayGraph, hover = True, state='disabled')
        self.button_showresult.grid(row=12, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_showresult = customtkinter.CTkButton(self, text="Draw", command=self.GraphicAuto, hover = True, state='disabled')
        self.button_showresult.grid(row=13, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_pause = customtkinter.CTkButton(self, text="PAUSE", command=self.StopReaction, hover = True)
        self.button_pause.grid(row=14, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_reset = customtkinter.CTkButton(self, text="RESET", command=None, hover = True)
        self.button_reset.grid(row=15, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def RunReaction(self):
        Arduino.execute('s')
        result.Output_list = []
        self.outputWindow()

    def StopReaction(self):
        Arduino.execute('t')
        try:
            self.new_window.auto_log_off()
            result.Output_save = pd.concat(result.Output_list)
        except self.new_window == None:
            pass

    def outputWindow(self):
        self.new_window = OutputProcess()
        self.new_window.auto_log_open()
        self.new_window.auto_log_on()

    def ResultWindowOpen(self):
        self.new_window = OutputProcess()
        self.new_window.auto_log_open()

    def selectfile(self):
        filename = filedialog.askopenfilename()
        print(filename)

    def DisplayGraph(self):
        self.new_window = OutputProcess()
        test = self.new_window.auto_log_open()

    def DrawGraph(self):
        self.draw = OutputProcess()
        test = self.draw.GraphicDraw()

    def GraphicAuto(self):
        self.draw = OutputProcess()
        drawing = self.draw.GraphicAuto()

class Testing_window(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.auto = False

        self.sensor_reading_display = customtkinter.CTkTextbox(self, width=500, height=300, corner_radius=5)
        self.sensor_reading_display.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nsew")

        self.command_input = customtkinter.CTkEntry(self)
        self.command_input.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.command_send = customtkinter.CTkButton(self, text="SEND", command=self.send_command)
        self.command_send.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="nsew")

        self.read_line = customtkinter.CTkButton(self, text="READ", command=self.write_output)
        self.read_line.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="nsew")

        self.LogData_win = customtkinter.CTkButton(self, text="LOG WINDOW", command=self.auto_log_open)
        self.LogData_win.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="nsew")

        self.LogData = customtkinter.CTkButton(self, text="AUTO LOG ON", command=self.auto_log_on)
        self.LogData.grid(row=4, column=1, padx=10, pady=(10, 0), sticky="nsew")

        self.LogData_Off = customtkinter.CTkButton(self, text="AUTO LOG OFF", command=self.auto_log_off)
        self.LogData_Off.grid(row=5, column=1, padx=10, pady=(10, 0), sticky="nsew")

    def send_command(self):
        command = self.command_input.get()
        if command == '':
            msg = CTkMessagebox(title="Command ERROR", message="Please input command", icon="warning", option_1="OK")
        else:
            Arduino.execute(command)

    def write_output(self):
        # print(status.Arduino_connection)
        if status.Arduino_connection:
            output = Arduino.read_output()
            self.sensor_reading_display.insert('end', output)
            self.sensor_reading_display.insert('end', '\n')
            # print(output)

    # Start a new thread to process the Arduino output so the main window won't be stuck
    def auto_log_thread(self):
        thread1 = threading.Thread(target=self.auto_log)
        thread1.start()

    def auto_log_open(self):
        self.log_window = customtkinter.CTkToplevel()
        self.log_window.title("Arduino readings")
        self.log_window.geometry("550x350")
        self.result_box = customtkinter.CTkTextbox(self.log_window, width=500, height=300, corner_radius=5)
        self.result_box.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

    def auto_log(self):
        if status.Arduino_connection:
            self.auto_log_open()
            print("test")

            while self.auto:
                output = Arduino.read_output()
                self.result_box.insert('end', output)
                self.result_box.insert('end', '\n')
                self.result_box.see('end')
                if self.auto == False:
                    break

    def auto_log_on(self):
        self.auto = True
        self.auto_log_thread()

    def auto_log_off(self):
        # self.auto_log_on()
        self.auto = False

class Setting_window(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.label_appearance = customtkinter.CTkLabel(self, text="Choose a colour theme", anchor="w")
        self.label_appearance.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="s")

        self.label_TestMode = customtkinter.CTkLabel(self, text="Test mode", anchor="w")
        self.label_TestMode.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.switch_TestMode_var = customtkinter.StringVar(value="Off")
        self.switch_TestMode = customtkinter.CTkSwitch(self, text="On", command=self.test_mode, 
                                                       variable=self.switch_TestMode_var, onvalue="On", offvalue="Off")
        self.switch_TestMode.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="s")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def test_mode(self):
        if self.switch_TestMode_var.get() == "On":
            status.Arduino_connection = True
            print("1")
        elif self.switch_TestMode_var.get() == "Off":
            if status.Arduino_connection_real == False:
                status.Arduino_connection = False
            print("2")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Logo")

        self.title("(REACTOR) Real-time Experiment Analysis Control and Tracking for Optimization and Records")
        
        self.geometry("800x600")
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.iconbitmap(os.path.join(image_path, "logo__Reactions_logo.ico"))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.logo_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "logo__UTCV_banner(black)[20210912].png")),
                                                 dark_image=Image.open(os.path.join(image_path, "logo__UTCV_banner(white)[20210912].png")), size=(152, 36))
        self.MB_logo = customtkinter.CTkImage(Image.open(os.path.join(image_path, "MB icon.png")), size=(26, 26))
        self.Chameleon_logo = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Chameleon logo.png")), size=(26, 26))
        self.testing_logo = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "Testing logo.png")),
                                                   dark_image=Image.open(os.path.join(image_path, "Testing logo (white).png")), size=(26, 26))
        self.setting_logo = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Setting logo.png")), size=(26, 26))
        self.ResultTable_logo = customtkinter.CTkImage(Image.open(os.path.join(image_path, "result_table.ico")), size=(26, 26))

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=None, image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=5, pady=5)

        self.frame_1_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=5, height=40, border_spacing=10, text="Blue Bottle",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.MB_logo, anchor="w", command=self.frame_1_button_event)
        self.frame_1_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=5, height=40, border_spacing=10, text="Chameleon",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.Chameleon_logo, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=5, height=40, border_spacing=10, text="Testing",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.testing_logo, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.frame_setting_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=5, height=40, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.setting_logo, anchor="w", command=self.frame_setting_button_event)
        self.frame_setting_button.grid(row=4, column=0, sticky="ew")

        # create MB frame (Frame_1)
        self.MB_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.MB_frame.grid_columnconfigure(0, weight=1)

        # Create check box
        self.switch_frame = RGBC_switch(self.MB_frame)
        self.switch_frame.grid(row=0, column=3, padx=10, pady=(10, 0), sticky="nsw")

        self.window = MB_window(self.MB_frame)
        self.window.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")

        # create Chameleon frame
        self.Chameleon_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.Chameleon = Chameleon_window(self.Chameleon_frame)
        self.Chameleon.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")

        self.switch_frame_2 = RGBC_switch(self.Chameleon_frame)
        self.switch_frame_2.grid(row=0, column=3, padx=10, pady=(10, 0), sticky="nsw")

        # create testing frame
        self.testing_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.testing_frame.grid_columnconfigure(0, weight=1)

        self.testing = Testing_window(self.testing_frame)
        self.testing.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")

        # create setting frame
        self.setting_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.setting = Setting_window(self.setting_frame)
        self.setting.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")

        # select default frame
        self.select_frame_by_name("Chameleon")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.frame_1_button.configure(fg_color=("gray75", "gray25") if name == "MB" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "Chameleon" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "testing" else "transparent")
        self.frame_setting_button.configure(fg_color=("gray75", "gray25") if name == "setting" else "transparent")

        # show selected frame
        if name == "MB":
            self.MB_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.MB_frame.grid_forget()
        if name == "Chameleon":
            self.Chameleon_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.Chameleon_frame.grid_forget()
        if name == "testing":
            self.testing_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.testing_frame.grid_forget()
        if name == "setting":
            self.setting_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.setting_frame.grid_forget()

    def frame_1_button_event(self):
        self.select_frame_by_name("MB")

    def frame_2_button_event(self):
        self.select_frame_by_name("Chameleon")

    def frame_3_button_event(self):
        self.select_frame_by_name("testing")

    def frame_setting_button_event(self):
        self.select_frame_by_name("setting")    


    # def show_warning(self):
    # # Show some retry/cancel warnings
    #     msg = CTkMessagebox(title="Sensor Error", message="Colour sensor cannot be detected!",
    #                 icon="warning", option_1="Cancel", option_2="Retry")
    
    #     if msg.get()=="Retry":
    #         App.show_warning(self)

    # def selectfile(self):
    #     filename = filedialog.askopenfilename()
    #     print(filename)

app = App()
app.mainloop()