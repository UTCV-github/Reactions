import threading
import customtkinter
from Global_var import status
from CTkMessagebox import CTkMessagebox
from Arduino import Arduino
import matplotlib.pyplot as plt
from Result import result
import pandas as pd
import queue
import time
from Graphic import Plotting
import Stopping

class OutputProcess():
    def __init__(self, SensorReadingQueue, reactions):
        self.output = pd.DataFrame()
        self.auto = None
        self.OutputQueue = SensorReadingQueue
        self.reactions = reactions

    # Start a new thread to process the Arduino output so the main window won't be stuck
    def auto_log_thread(self):
        if status.Arduino_connection:
            self.auto_log_open()
            thread1 = threading.Thread(target=self.auto_log)
            thread1.start() 
            thread2 = threading.Thread(target=self.auto_plotting) #
            thread2.start() #

    def auto_log_open(self):
        self.log_window = customtkinter.CTkToplevel()
        self.log_window.title("Arduino readings")
        self.log_window.geometry("550x350")
        self.log_window.after(10, self.log_window.lift)
        self.result_box = customtkinter.CTkTextbox(self.log_window, width=500, height=300, corner_radius=5)
        self.result_box.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.result_box_pause = customtkinter.CTkButton(self.log_window, text="PAUSE", command=self.StopReaction, hover = True)
        self.result_box_pause.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.graph = Plotting(self.OutputQueue)

    def auto_log(self):

        while self.auto:
            self.output = Arduino.read_output()
            if not self.output.empty:
                self.OutputQueue.put(self.output)
                result.Output_list.append(self.output)
                self.result_box.insert('end', self.output)
                self.result_box.insert('end', '\n')
                self.result_box.see('end')

                Diff = Stopping.Algorithm(self.reactions)

            # self.graph.update()

            if self.auto == False:
                print("Auto log paused")
                break

#
    def auto_plotting(self):
        while self.auto:
            self.graph.update()

    def auto_log_on(self):
        self.auto = True
        self.auto_log_thread()
        # print('Auto log on')
        # self.GraphicAuto()

    def auto_log_off(self):
        # self.auto_log_on()
        self.auto = False    

    def SendOutput(self):
        return self.output
    
    def StopReaction(self):
        Arduino.execute('t')
        self.auto_log_off()
        result.Output_save = pd.concat(result.Output_list)
        Arduino.clear_buffer()
        self.OutputQueue.queue.clear()
    