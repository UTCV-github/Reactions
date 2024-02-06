import threading
import customtkinter
from Global_var import status
from CTkMessagebox import CTkMessagebox
from Arduino import Arduino
import matplotlib.pyplot as plt

class OutputProcess():
    def __init__(self) -> None:
        pass

    # Start a new thread to process the Arduino output so the main window won't be stuck
    def auto_log_thread(self):
        thread1 = threading.Thread(target=self.auto_log)
        thread1.start()

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

    def GraphicOutput_Setup(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        plt.xlabel("Time (s)")
        plt.ylabel("C value")
        plt.ylim(0,2500)
        self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)