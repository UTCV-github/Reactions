import threading
import customtkinter
from Global_var import status
from CTkMessagebox import CTkMessagebox
from Arduino import Arduino
import matplotlib.pyplot as plt
from Result import result
import pandas as pd

class OutputProcess():
    def __init__(self) -> None:
        self.output = pd.DataFrame
        self.auto = None

    # Start a new thread to process the Arduino output so the main window won't be stuck
    def auto_log_thread(self):
        thread1 = threading.Thread(target=self.auto_log)
        thread1.start()
        # thread2 = threading.Thread(target=self.GraphicAuto)
        # thread2.start()

    def auto_log_open(self):
        self.log_window = customtkinter.CTkToplevel()
        self.log_window.title("Arduino readings")
        self.log_window.geometry("550x350")
        self.log_window.after(10, self.log_window.lift)
        self.result_box = customtkinter.CTkTextbox(self.log_window, width=500, height=300, corner_radius=5)
        self.result_box.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

    def auto_log(self):
        if status.Arduino_connection:
            self.auto_log_open()

            while self.auto:
                self.output = Arduino.read_output()
                global Output
                Output = self.output
                # result.output.append(self.output)
                self.result_box.insert('end', self.output)
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

    def GraphicOutput_Setup(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        plt.xlabel("Time (s)")
        plt.ylabel("C value")
        plt.ylim(0,2500)
        self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)

    def GraphicDraw(self, data):
        # if data.empty:
        #     global Output
        #     data = Output
        # print(data)
        x = data.Time.iloc[-1]
        y = data.C.iloc[-1]
        dot, = self.ax.plot(x, y,'.', color = 'lightblue', markersize = 10)
        # dot, = ax.plot(float(result.time), int(result.cur_avg),'.', color = 'lightgreen', markersize = 5)
        self.ax.draw_artist(dot)
        self.fig.canvas.blit(self.fig.bbox) 

    def GraphicAuto(self):
        self.GraphicOutput_Setup()
        global Output
        data = Output
        previous_output = pd.DataFrame()
        while True:
            try:
                self.GraphicDraw(data)
            except data.equals(previous_output):
                pass

            if self.auto == False:
                break
    
    def DrawGraphThread(self):
        thread2 = threading.Thread(target=self.GraphicAuto)
        thread2.start()