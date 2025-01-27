import time
from datetime import datetime
import pandas as pd

import customtkinter
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog
from CTkTable import *
import time
import threading
import queue
import os

from Configure_Arduino import Configure_Arduino
from Global_var import status
from Output import OutputProcess
from Arduino import Arduino
from Result import result
from Register import ChemicalRegister
from Register import ChemicalSelection
from Register import SolutionSelected
from InventoryWindow import *

class Chameleon_TCS34725_window(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.new_window = None

        self.button_Arduino_config = customtkinter.CTkButton(self, text="Arduino Configuration", command=self.ArduinoConfiguration)
        self.button_Arduino_config.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")

        self.button_file = customtkinter.CTkButton(self, text="Select Folder", command=self.selectfolder)
        self.button_file.grid(row=1, column=0, padx=10, pady=(10,0), sticky="ew")

        self.entry_folder = customtkinter.CTkEntry(self, placeholder_text="Save data file at ...")
        self.entry_folder.grid(row=1, column=1, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="nsew")

        self.label_TestBench = customtkinter.CTkLabel(self, text="Select a test bench", anchor="w")
        self.label_TestBench.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_TestBench = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["A: test bench", "B: car", "C"])
        self.optionmenu_TestBench.grid(row=3, column=0, padx=10, pady=(0, 10))

        self.button_run = customtkinter.CTkButton(self, text="RUN", command=self.RunReaction, hover = True, state='disabled', fg_color="Red")
        self.button_run.grid(row=10, column=0, columnspan=3, rowspan=2, padx=10, pady=5, sticky="ew")
        self.grid_rowconfigure(11, weight=1)

        self.button_showresult = customtkinter.CTkButton(self, text="REGISTER CHEMICAL", command=ChemicalRegister, hover = True, state='normal')
        self.button_showresult.grid(row=12, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_showresult = customtkinter.CTkButton(self, text="SELECT CHEMICAL", command=self.ChemicalSelection, hover = True, state='normal')
        self.button_showresult.grid(row=13, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_pause = customtkinter.CTkButton(self, text="PAUSE", command=self.StopReaction, hover = True, fg_color="orange")
        self.button_pause.grid(row=14, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_reset = customtkinter.CTkButton(self, text="RESET", command=self.Reset, hover = True)
        self.button_reset.grid(row=15, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.button_save = customtkinter.CTkButton(self, text="SAVE", command=self.save_data, hover = True, fg_color="green")
        self.button_save.grid(row=16, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.SolutionSelected_1 = SolutionSelected(self)
        self.SolutionSelected_1.grid(row=18, column=0, columnspan=2, padx=10, pady=(10, 10), sticky="nsw")

    def ArduinoConfiguration(self):
        self.Configure_window = Configure_Arduino()
        thread2 = threading.Thread(target=self.check_connection)
        thread2.start() 

    def check_connection(self):
        while self.Configure_window.winfo_exists():
            time.sleep(0.1)
            
            if status.Arduino_connection == True:
                self.button_run.configure(state = 'normal')
                self.button_run.configure(fg_color="green")

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

    def RunReaction(self):
        Arduino.execute('s')
        status.LegendTrigger = True # Reset the legend trigger
        self.button_run.configure(state = 'disabled', fg_color="red")
        result.Output_list = []
        self.outputWindow()

    def StopReaction(self):
        Arduino.execute('t')
        self.button_run.configure(state = 'normal')
        try:
            self.new_window.auto_log_off()
            result.Output_save = pd.concat(result.Output_list)
        except self.new_window == None:
            pass

    def outputWindow(self):
        SensorReadingQueue = queue.Queue()
        self.new_window = OutputProcess(SensorReadingQueue, 'chameleon')
        self.new_window.auto_log_on()

    def Reset(self):
        self.button_run.configure(state = 'normal', fg_color="green")

    def selectfolder(self):
        self.folderpath = filedialog.askdirectory()
        status.folderpath = self.folderpath
        self.entry_folder.delete(0, 'end')
        self.entry_folder.insert('end', self.folderpath)
        print(self.folderpath)

    def save_data(self):
        if not result.Output_save.empty:
            self.folderpath = self.entry_folder.get()

            # if no folder was selcted
            if self.folderpath == '': 
                self.folderpath = os.path.dirname(__file__) + "/Saved_data"
                os.makedirs(self.folderpath, exist_ok=True)
            
            # Check if the folder path is legit
            if os.path.isdir(self.folderpath):
                now = datetime.now()
                date_time = now.strftime("%Y_%m_%d_%H_%M_%S")

                filename_prefix = 'Cache' # Default prefix
                if 'Bottle ID: ' in status.ChemicalSelected[0]:
                    if status.ChemicalSelected[0] != 'Bottle ID: NA':
                        filename_prefix = status.ChemicalSelected[0].split(': ')[1]

                file_name =  os.path.dirname(__file__) + "/Saved_data/" + filename_prefix + "_" + date_time + ".csv"
                result.Output_save.to_csv(file_name, index = False)

                if os.path.exists(file_name):
                    self.save_msg()
            else:
                msg_displayed = "Folder path:" + self.folderpath + "does not exist"
                msg = CTkMessagebox(title="System Error", message = msg_displayed, icon="warning", option_1="OK")

        else:
            self.save_warning()

    def save_warning(self):
    # Show some retry/cancel warnings
        msg = CTkMessagebox(title="System Error", message="No data to be saved!",
                    icon="warning", option_1="Cancel", option_2="Retry")
    
        if msg.get()=="Retry":
            self.save_warning()

    def save_msg(self):
        msg = CTkMessagebox(title="Data Saved", message="Data successfully saved!",
                    icon="check", option_1="OK")