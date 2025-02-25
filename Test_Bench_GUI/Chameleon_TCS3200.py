import time
from datetime import datetime
import pandas as pd

import customtkinter
import tkinter as tk
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog
from CTkTable import *
import time
import threading
import queue
import os
import re

from Configure_Arduino import Configure_Arduino
from Global_var import status
from Output import OutputProcess
from Arduino import Arduino
from Result import result
from Register import ChemicalRegister
from Register import ChemicalSelection
from Register import SolutionSelected
from InventoryWindow import *

class Chameleon_TCS3200_window(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.log_window = None
        self.TestBenchSelected = None
        self.filename_input = tk.StringVar()
        self.default_filename = self.auto_filename() # Store the default name
        self.filename_input.set(self.default_filename)

        self.result_box = None

        self.button_Arduino_config = customtkinter.CTkButton(self, text="Arduino Configuration", command=self.ArduinoConfiguration)
        self.button_Arduino_config.grid(row=0, column=0, columnspan=3, padx=10, pady=(10,0), sticky="ew")

        self.button_file = customtkinter.CTkButton(self, text="Select Folder", command=self.selectfolder)
        self.button_file.grid(row=1, column=2, padx=10, pady=(10,0), sticky="ew")

        self.entry_folder = customtkinter.CTkEntry(self, placeholder_text="Save data file at ...", width=300)
        self.entry_folder.grid(row=1, column=0, columnspan=2, padx=(10, 10), pady=(10, 0), sticky="nsew")

        self.label_TestBench = customtkinter.CTkLabel(self, text="Select a test bench", anchor="w")
        self.label_TestBench.grid(row=2, column=0, padx=10, pady=(20, 10), sticky="nsew")

        self.optionmenu_TestBench = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["-Select Test Bench-", "Test Bench A", "Test Bench B", "Test Bench C", "Test Bench D"],
                                                        command = self.TestBenchSelection)
        self.optionmenu_TestBench.grid(row=2, column=1, columnspan=2, padx=10, pady=(20, 10), sticky="nsew")

        self.button_showresult = customtkinter.CTkButton(self, text="REGISTER CHEMICAL", command=ChemicalRegister, hover = True, state='normal')
        self.button_showresult.grid(row=12, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_showresult = customtkinter.CTkButton(self, text="SELECT CHEMICAL", command=self.ChemicalSelection, hover = True, state='normal')
        self.button_showresult.grid(row=13, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.SolutionSelected_1 = SolutionSelected(self)
        self.SolutionSelected_1.grid(row=14, column=0, columnspan=2, padx=10, pady=(10, 10), sticky="nsw")

        self.SerialMonitor = customtkinter.CTkButton(self, text="Serial Monitor", command=self.auto_log_on, hover = True, state='disabled', fg_color="Red")
        self.SerialMonitor.grid(row=20, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_run = customtkinter.CTkButton(self, text="RUN", command=self.Start, hover = True, state='disabled', fg_color="Red")
        self.button_run.grid(row=21, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_pause = customtkinter.CTkButton(self, text="STOP", command=self.Stop, hover = True, state='disabled', fg_color="Red")
        self.button_pause.grid(row=22, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        # self.entry_filename = customtkinter.CTkEntry(self, placeholder_text=self.auto_filename(), width=300)
        self.entry_filename = customtkinter.CTkEntry(self, textvariable=self.filename_input, width=300)
        self.entry_filename.grid(row=23, column=0, columnspan=2, padx=(10, 10), pady=(5, 5), sticky="nsew")
        
        self.button_DefaultName = customtkinter.CTkButton(self, text="Default Name", command=self.default_name, hover = True)
        self.button_DefaultName.grid(row=23, column=2, columnspan=1, padx=10, pady=(5, 5), sticky="ew")

        self.button_save = customtkinter.CTkButton(self, text="SAVE", command=self.save_data, hover = True)
        self.button_save.grid(row=24, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="ew")

    def ArduinoConfiguration(self):
        self.Configure_window = Configure_Arduino()
        thread2 = threading.Thread(target=self.check_connection)
        thread2.start() 

    def check_connection(self):
        while self.Configure_window.winfo_exists():
            time.sleep(0.1)
            
            if status.Arduino_connection == True:
                self.button_pause.configure(state = 'normal')
                self.button_pause.configure(fg_color="#3B8ED0")
                self.button_run.configure(state = 'normal')
                self.button_run.configure(fg_color="#3B8ED0")
                self.SerialMonitor.configure(state = 'normal')
                self.SerialMonitor.configure(fg_color="#3B8ED0")

    def TestBenchSelection(self, selection):
        self.TestBenchSelected = selection

        if self.entry_filename.get() == self.default_filename: # if the user did not manually change the default file name, then keep the user name, otherwise, uupdate the defualt name but keep the file name
            self.default_filename = self.auto_filename()
            self.filename_input.set(self.default_filename)
        else:
            self.default_filename = self.auto_filename()

    def ChemicalSelection(self):
        self.SelectionWindow = ChemicalSelection()
        thread3 = threading.Thread(target=self.CheckChemical)
        thread3.start() 

    def CheckChemical(self):
        while self.SelectionWindow.winfo_exists():
            time.sleep(0.1)
            if status.ChemicalSelected != status.ChemicalSelectedNew:
                self.SolutionSelected_1.label_SolID.configure(text=status.ChemicalSelectedNew[0])
                self.SolutionSelected_1.label_KOH_conc.configure(text=status.ChemicalSelectedNew[1])
                self.SolutionSelected_1.label_Dex_conc.configure(text=status.ChemicalSelectedNew[2])
                self.SolutionSelected_1.label_KMnO4_conc.configure(text=status.ChemicalSelectedNew[3])

                status.ChemicalSelected = status.ChemicalSelectedNew
                if self.entry_filename.get() == self.default_filename: # if the user did not manually change the default file name, then keep the user name, otherwise, uupdate the defualt name but keep the file name
                    self.default_filename = self.auto_filename()
                    self.filename_input.set(self.default_filename)
                else:
                    self.default_filename = self.auto_filename()
                # self.entry_filename.configure(placeholder_text = self.auto_filename()) # Update the default text in the file name box once a chemical is selected

    # Start a new thread to process the Arduino output so the main window won't be stuck
    def auto_log_thread(self):
        thread1 = threading.Thread(target=self.auto_log)
        thread1.start()

    def SerialMonitorWindow(self):
        self.Endpoint = False # Changed to be true once endpoint reached

        self.log_window = customtkinter.CTkToplevel()
        self.log_window.title("Serial Monitor")
        self.log_window.geometry("600x355")
        self.result_box = customtkinter.CTkTextbox(self.log_window, width=500, height=300, corner_radius=5)
        self.result_box.grid(row=0, column=0, rowspan=10, padx=10, pady=(10, 0), sticky="nsew")
        self.button_clear_text = customtkinter.CTkButton(self.log_window, text="CLEAR", command=self.clear_text)
        self.button_clear_text.grid(row=11, column=0, padx=10, pady=(10, 20), sticky="nsew")

        self.text_Endpoint_header = customtkinter.CTkLabel(self.log_window, text="Endpoint:")
        self.text_Endpoint_header.grid(row=0, column=1, padx=10, pady=(10, 20), sticky="nsew")
        self.text_Endpoint = customtkinter.CTkLabel(self.log_window, text="NA")
        self.text_Endpoint.grid(row=1, column=1, padx=10, pady=(10, 20), sticky="nsew")

        self.text_Timer_header = customtkinter.CTkLabel(self.log_window, text="Timer:")
        self.text_Timer_header.grid(row=2, column=1, padx=10, pady=(10, 20), sticky="nsew")
        self.text_Timer = customtkinter.CTkLabel(self.log_window, text="0 s")
        self.text_Timer.grid(row=3, column=1, padx=10, pady=(10, 20), sticky="nsew")
        self.log_window.protocol("WM_DELETE_WINDOW", self.log_window_close)
        self.log_window.focus()

    def clear_text(self):
        self.result_box.delete(0.0, 'end')
        self.Endpoint = False
        self.text_Endpoint.configure(text = "NA")

    def log_window_close(self):
        print("Subwindow is closing")
        self.auto_log_off()
        self.log_window.destroy()

    def auto_log(self):
        if status.Arduino_connection:
            self.SerialMonitorWindow()

            while self.auto:
                output = Arduino.read_output_raw()
                if output != '':
                    self.result_box.insert('end', output)
                    self.result_box.insert('end', '\n')
                    self.result_box.see('end')
                if 'Time' in output:
                    text_time = float(output.split(":")[-1])
                    self.text_Timer.configure(text = f"{text_time:.2f}" + ' s')
                if 'Endpoint' in output and not self.Endpoint:
                    text_Endpoint = float(output.split(":")[-1])
                    self.text_Endpoint.configure(text = f"{text_Endpoint:.2f}" + ' s')
                    self.Endpoint = True

                if self.auto == False:
                    break

    def auto_log_on(self):
        self.auto = True
        self.auto_log_thread()
        self.SerialMonitor.configure(state = 'disabled', fg_color="red")
        self.button_run.configure(state = 'normal', fg_color="#3B8ED0")
        self.button_pause.configure(state = 'normal', fg_color="#3B8ED0")

    def auto_log_off(self):
        # self.auto_log_on()
        self.auto = False
        self.SerialMonitor.configure(state = 'normal', fg_color="#3B8ED0")
        self.button_run.configure(state = 'disabled', fg_color="red")
        self.button_pause.configure(state = 'disabled', fg_color="red")

    def Send_command(self, command):
        if self.log_window == None or not self.log_window.winfo_exists():
            msg = CTkMessagebox(title="System Error", message = 'Serial Monitor is not open', icon="warning", option_1="OK")
        else:
            Arduino.execute(command)
    
    def Start(self):
        self.Send_command('s')
        self.button_run.configure(state = 'disabled', fg_color="red")

    def Stop(self):
        self.Send_command('t')
        self.button_run.configure(state = 'normal', fg_color="#3B8ED0")

    def default_name(self):
        self.default_filename = self.auto_filename()
        self.filename_input.set(self.default_filename)

    def auto_filename(self):
        now = datetime.now()
        date_time = now.strftime("%Y_%m_%d_%H_%M_%S")

        filename_prefix = 'Cache' # Default prefix
        if 'Bottle ID: ' in status.ChemicalSelected[0]:
            if status.ChemicalSelected[0] != 'Bottle ID: NA':
                filename_prefix = status.ChemicalSelected[0].split(': ')[1]

        dict_TestBench = {"Test Bench A": "A",
                          "Test Bench B": "B",
                          "Test Bench C": "C",
                          "Test Bench D": "D",
                          "-Select Test Bench-": "N"}
        
        if self.TestBenchSelected in dict_TestBench:
            filename_prefix = dict_TestBench[self.TestBenchSelected] + filename_prefix
        else:
            filename_prefix = "N" + filename_prefix

        file_name =  filename_prefix + "_" + date_time + ".txt"

        return file_name

    def save_data(self):
        if (self.result_box != '') and (self.result_box != None):
            # if no folder was selcted
            if status.folderpath == '': 
                status.folderpath = os.path.join(os.path.dirname(__file__), "Saved_data")
                os.makedirs(status.folderpath, exist_ok=True)

            # Check if the folder path is legit
            if os.path.isdir(status.folderpath):
                file_name_enter = self.entry_filename.get()

                # Check the format of the filename in the text box
                if file_name_enter != '':
                    if not file_name_enter.endswith(".txt"):
                        file_name_enter += ".txt"
                    file_name = file_name_enter

                # Check if the name has been manually changed, if not, auto generate a new name using current time
                if file_name_enter == self.default_filename:
                    file_name = self.auto_filename()

                file_path = os.path.join(status.folderpath, file_name)

                # Writing to a file
                with open(file_path, 'w') as file:
                    text_to_save = self.result_box.get(0.0, 'end')
                    file.write(text_to_save)

                msg = CTkMessagebox(title="Data Saved", message = 'Data has beeen saved at ' + file_path, icon="check", option_1="OK")

            else:
                msg_displayed = "Folder path:" + status.folderpath + " does not exist"
                msg = CTkMessagebox(title="System Error", message = msg_displayed, icon="warning", option_1="OK")
        else:
            msg = CTkMessagebox(title="System Error", message = 'No Data for saving, please check if the serial monitor window is open', icon="warning", option_1="OK")

    def selectfolder(self):
        self.folderpath = filedialog.askdirectory()
        status.folderpath = self.folderpath
        self.entry_folder.delete(0, 'end')
        self.entry_folder.insert('end', self.folderpath)
        print(self.folderpath)
