import PySimpleGUI as sg
import serial
import serial.tools.list_ports
import time
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

import tkinter
import tkinter.messagebox
import customtkinter
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog
from PIL import Image

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class MB_frame_right(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.switch_r = customtkinter.CTkSwitch(self, text="R value")
        self.switch_r.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.switch_g = customtkinter.CTkSwitch(self, text="G value")
        self.switch_g.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        self.switch_b = customtkinter.CTkSwitch(self, text="B value")
        self.switch_b.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")

        self.button_save = customtkinter.CTkButton(self, text="SAVE", command=self.show_warning, hover = True)
        self.button_save.grid(row=8, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def get(self):
        ls_sensor_readings = []
        if self.switch_r.get() == 1:
            ls_sensor_readings.append(self.switch_r.cget("text"))
        if self.switch_g.get() == 1:
            ls_sensor_readings.append(self.switch_g.cget("text"))
        if self.switch_b.get() == 1:
            ls_sensor_readings.append(self.switch_b.cget("text"))
        return ls_sensor_readings
    
    def show_warning(self):
    # Show some retry/cancel warnings
        msg = CTkMessagebox(title="System Error", message="No data to be saved!",
                    icon="warning", option_1="Cancel", option_2="Retry")
    
        if msg.get()=="Retry":
            self.show_warning()
    
class MB_window(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.button_file = customtkinter.CTkButton(self, text="select file", command=self.selectfile)
        self.button_file.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.entry_file = customtkinter.CTkEntry(self, placeholder_text="Save data file at ...")
        self.entry_file.grid(row=0, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.label_TestBench = customtkinter.CTkLabel(self, text="Select a test bench", anchor="w")
        self.label_TestBench.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_TestBench = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["A: test bench", "B: car", "C"])
        self.optionmenu_TestBench.grid(row=2, column=0, padx=10, pady=(0, 10))

        self.label_KohConc = customtkinter.CTkLabel(self, text="Input the KOH concentration", anchor="w")
        self.label_KohConc.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_KohConc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_KohConc.grid(row=4, column=0, padx=10, pady=(0, 10))

        self.entry_KohConc = customtkinter.CTkEntry(self, placeholder_text="KOH concentration")
        self.entry_KohConc.grid(row=4, column=1, columnspan=2, padx=(20, 0), pady=(0, 10), sticky="nsew")

        self.button_run = customtkinter.CTkButton(self, text="RUN", command=self.show_warning, hover = True)
        self.button_run.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_clear = customtkinter.CTkButton(self, text="CLEAR", command=self.show_warning, hover = True)
        self.button_clear.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_pause = customtkinter.CTkButton(self, text="PAUSE", command=self.show_warning, hover = True)
        self.button_pause.grid(row=7, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_reset = customtkinter.CTkButton(self, text="RESET", command=self.show_warning, hover = True)
        self.button_reset.grid(row=8, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def show_warning(self):
    # Show some retry/cancel warnings
        msg = CTkMessagebox(title="Sensor Error", message="Colour sensor cannot be detected!",
                    icon="warning", option_1="Cancel", option_2="Retry")
    
        if msg.get()=="Retry":
            self.show_warning()

    def selectfile(self):
        filename = filedialog.askopenfilename()
        print(filename)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Logo")

        self.title("(REACTOR) Real-time Experiment Analysis Control and Tracking for Optimization and Records")
        
        self.geometry("800x400")
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.iconbitmap(os.path.join(image_path, "logo__Reactions_logo.ico"))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo__UTCV_banner(black)[20210912].png")), size=(152, 36))
        self.MB_logo = customtkinter.CTkImage(Image.open(os.path.join(image_path, "MB icon.png")), size=(26, 26))
        self.Chameleon_logo = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Chameleon logo.png")), size=(26, 26))
        self.testing_logo = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Testing logo.png")), size=(26, 26))
        self.setting_logo = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Setting logo.png")), size=(26, 26))

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
        self.switch_frame = MB_frame_right(self.MB_frame)
        self.switch_frame.grid(row=0, column=3, padx=10, pady=(10, 0), sticky="nsw")

        self.window = MB_window(self.MB_frame)
        self.window.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")

        # self.button = customtkinter.CTkButton(self.MB_frame, text="RUN", command=self.show_warning)
        # self.button.grid(row=3, column=3, padx=10, pady=10, sticky="ew")

        # self.button2 = customtkinter.CTkButton(self.MB_frame, text="select file", command=self.selectfile)
        # self.button2.grid(row=4, column=3, padx=10, pady=10, sticky="ew")

        # create Chameleon frame
        self.Chameleon_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create testing frame
        self.testing_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create setting frame
        self.setting_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.frame_1_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")
        self.frame_setting_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

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

    def button_callback(self):
        sg.popup("Will enter test mode")

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