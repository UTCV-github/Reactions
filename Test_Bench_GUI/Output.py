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
    def __init__(self, SensorReadingQueue):
        self.output = pd.DataFrame()
        self.auto = None
        self.OutputQueue = SensorReadingQueue

    # Start a new thread to process the Arduino output so the main window won't be stuck
    def auto_log_thread(self):
        if status.Arduino_connection:
            self.auto_log_open()
            thread1 = threading.Thread(target=self.auto_log)
            thread1.start() 

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

                Diff = Stopping.default()

            self.graph.update()

            if self.auto == False:
                print("Auto log paused")
                break

    def auto_log_on(self):
        self.auto = True
        self.auto_log_thread()
        # print('Auto log on')
        # self.GraphicAuto()

    def auto_log_off(self):
        # self.auto_log_on()
        self.auto = False    

    def GraphicOutput_Setup(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        plt.xlabel("Time (s)")
        plt.ylabel("C value")
        plt.ylim(0,2500)
        self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)

    # def GraphicDraw(self, data):
    #     # if data.empty:
    #     #     global Output
    #     #     data = Output
    #     # print(data)
    #     if not data.empty():
    #         x = data.Time.iloc[-1]
    #         y = data.C.iloc[-1]
    #         dot, = self.ax.plot(x, y,'.', color = 'lightblue', markersize = 10)
    #         # dot, = ax.plot(float(result.time), int(result.cur_avg),'.', color = 'lightgreen', markersize = 5)
    #         self.ax.draw_artist(dot)
    #         self.fig.canvas.blit(self.fig.bbox)
    #     else:
    #         print('No data to be plotted')

    def GraphicAuto(self):
        # self.GraphicOutput_Setup()
        print('self.auto is', self.auto)
        while self.auto: 
            try:
                print('getting data...')
                self.lock.acquire()
                data = self.OutputQueue.get()
                print(data)
                self.lock.release()
                # self.GraphicDraw(data)
            except self.OutputQueue.empty():
                print('pass')
                pass

            if self.auto == False and self.OutputQueue.empty(): # Make sure the data in the queue is all plotted
                print('break')
                break

    def SendOutput(self):
        return self.output
    
    def StopReaction(self):
        Arduino.execute('t')
        self.auto_log_off()
        result.Output_save = pd.concat(result.Output_list)
    