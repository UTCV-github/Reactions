import PySimpleGUI as sg
import os.path
import serial
import time
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configure the serial port that connects the Arduino
ser = serial.Serial('COM6', 9600, timeout=1)
time.sleep(1)
sg.popup(ser.readline())

# Define the function that send command to the Arduino
def Arduino_Run(command):
    ser.write(str.encode(command))

# Define the function that saves the data as csv file(s)
def save_csv(Date, Test_bench, KOH, Trial, Data_list, save_path):
    Date = datetime.strptime(Date, '%Y-%m-%d %H:%M:%S')
    Date = datetime.strftime(Date, '%Y-%m-%d-%H%M%S')
    file_name = save_path + "/" + Date + "_" + Test_bench + "_" + KOH + "_" + Trial + ".csv"
    # f = open(file_name, "x")
    # csv_writer = csv.writer(f)
    # csv_writer.writerows(Data_list)
    Data_list.to_csv(file_name, index = False)

def read_output(output):
    # Example output: b"R:365 G:117 B:76 C:590 cur_avg590 prev_avg590 read_idx8 Time:3.0889999866 Measured Time: 0.0000000000 \r\n"
    output = output.decode("utf-8")
    output = output[0:-5] # remove " \n\r" at the end of the string
    result = output.split()
    if len(result) > 3:
        R = int(result[0][2:])
        G = int(result[1][2:])
        B = int(result[2][2:])
        C = int(result[3][2:])
        cur_avg = int(result[4][7:])
        prev_avg = int(result[5][8:])
        read_idx = int(result[6][8:])
        time = float(result[7][5:])
        Measured_time = float(result[10])
        # Compile the results into a dataframe
        d = {'R': [R], 'G': [G], 'B': [B], 'C': C, 'cur_avg': [cur_avg], 'prev_avg': [prev_avg], 'read_idx': [read_idx], 'time': [time], 'measured_time': Measured_time}
        df = pd.DataFrame(data=d)
        return df
    # return the reaction time if the output is "measured time"
    elif len(result) == 3:
        measured_time = float(result[2])
        return measured_time

# Construct the layout of the GUI window
layout_1 = [
    [sg.Text("This is a UTCV Reactions GUI demo")], 
    [sg.Text("File save path"), sg.InputText(size=(25, 1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse()],
    [sg.Text('Test Bench (A/B/C)', size =(15, 1)), sg.InputText(key = "-TestBench-", do_not_clear=True)],
    # [sg.Text("Date"), sg.Input(key = "-Date-", size=(20,1)), sg.CalendarButton("Date", close_when_date_chosen=True, target="-Date-", format='%Y-%m-%d')],
    [sg.Text("Date"), sg.Input(key = "-Date-", size=(20,1)), sg.CalendarButton("Date", close_when_date_chosen=True, target="-Date-")],
    [sg.Text('KOH Concentration', size =(15, 1)), sg.InputText(key = "-KOHConc-", do_not_clear=True)],
    [sg.Text('Trial', size =(15, 1)), sg.InputText(key = "-trial-", do_not_clear=True)],
    [sg.Text('Arduino Command'), sg.Combo(values=["s", "t"], size = (15,1), key = "-Arduino_Comand-")],
    [sg.Button("Run"), sg.Button("Save as csv")]
    ]

# Create the window
font = ("Arial", 20)
window = sg.Window(title="Reactions Test Bench GUI Demo", layout = layout_1, size=(800, 500), font = font)

plt.ion()
fig = plt.figure()
i = 0

# Create an event loop
while True:

    event, values = window.read()
    # End program if user closes window or
    if event == sg.WIN_CLOSED:
        break
    # Save the data as a csv file using the designated path
    elif event == "Save as csv":
        # Data_list = [[1,2,3,4,5,6]]
        save_csv(values["-Date-"], values["-TestBench-"], values["-KOHConc-"], values["-trial-"], df_cb, values["-FOLDER-"])
        sg.popup("csv file saved for test bench" + values["-TestBench-"][0], "The csv file is save at: " + values["-FOLDER-"])
    elif event == "Run":
        Arduino_Run(values["-Arduino_Comand-"][0])
        measured_time = 0 # initialized the reaction time
        df_cb = [] # create a list to temporarily hold all dataframes 

        # Reads output
        while True: 
            output = ser.readline()
            result = read_output(output)
            if type(result) == float:
                measured_time = result
            elif type(result) == pd.DataFrame:
                df_cb.append(result)
                plt.scatter(float(result.time), int(result.C))
                plt.xlabel("Time (s)")
                plt.ylabel("C value")
                plt.show()
                plt.pause(0.001)
                if measured_time != 0 and int(result.measured_time) == 0:
                    break
            else:
                sg.popup("Unknown error happen during reading Arduino data", title = "Error Message")
                break
        df_cb = pd.concat(df_cb, axis=0, ignore_index=True) # df_cb is the dataframe that stores all data points

        # time.sleep(1)
        sg.popup(str(df_cb), title = "Output")

window.close()