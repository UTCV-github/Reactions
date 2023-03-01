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
time.sleep(1) # Pause for 1 sencond to wait for response from the Arduino
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

# Define the function that reads a line of Arduino output and return the readings of each parameter
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
        d = {'R': [R], 'G': [G], 'B': [B], 'C': [C], 'cur_avg': [cur_avg], 'prev_avg': [prev_avg], 'read_idx': [read_idx], 'time': [time], 'measured_time': [Measured_time]}
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
    [sg.Button("Run"), sg.Button("Save as csv"), sg.Button("See Results"), sg.Button("Pause")] 
    ]


# Construct the layout of the result table window
result_table = []
headings_table = ['R', 'G', 'B', 'C', 'time', 'measured_time']
layout_table = [
    [sg.Table( values = result_table,
    headings = headings_table,
    max_col_width=40,
                auto_size_columns=True,
                display_row_numbers=True,
                justification='middle',
                num_rows=20,
                key = '-ResultTable-',
                row_height=30
    )]
]

# Create the window
font = ("Arial", 20)
window1 = sg.Window(title = "Reactions Test Bench GUI Demo", layout = layout_1, size=(800, 500), font = font, finalize=True)
window_result = None

# Open Pyplot interactive tool
plt.ion()
fig = plt.figure()
plt.xlabel("Time (s)")
plt.ylabel("C value")

# Create an event loop
while True:

    # Pop up the window
    # event, values = window1.read()
    window, event, values = sg.read_all_windows()

    # End program if user closes window
    
    # if event == sg.WIN_CLOSED:
    #     break

    if event == sg.WIN_CLOSED:
        window.close()
        if window == window_result:       # if closing win 2, mark as closed
            window_result = None
        elif window == window1:     # if closing win 1, exit program
            break

    # Pop up result table
    elif event == "See Results" and not window_result:
        window_result = sg.Window(title = "Sensor Reading", layout=layout_table, size=(800, 600), font = font, finalize=True)

    # Save the data as a csv file using the designated path
    elif event == "Save as csv":
        if 'df_cb' in globals():
            # Data_list = [[1,2,3,4,5,6]]
            save_csv(values["-Date-"], values["-TestBench-"], values["-KOHConc-"], values["-trial-"], df_cb, values["-FOLDER-"])
            sg.popup("csv file saved for test bench" + values["-TestBench-"][0], "The csv file is save at: " + values["-FOLDER-"])
        else:
            sg.popup("No data has been received", title = "Error Message")

    # Send command to Arduino and show realtime sensor readings in a plot    
    elif event == "Run":
        Arduino_Run(values["-Arduino_Comand-"][0])
        measured_time = 0 # initialized the reaction time
        df_cb = [] # create a list to temporarily hold all dataframes 
        result_table = [] # Initialize the result table again

        # Reads output
        while True: 
            output = ser.readline()
            result = read_output(output)
            if type(result) == float:
                measured_time = result
            elif type(result) == pd.DataFrame:
                df_cb.append(result)
                plt.scatter(float(result.time), int(result.C))
                plt.show()
                plt.pause(0.001)
                if result_table != None: 
                    result_table_row = [int(result['R']), int(result['G']), int(result['B']), int(result['C']), float(result['time']), float(result['measured_time'])]
                    result_table.append(result_table_row)
                    window_result['-ResultTable-'].update(result_table)

                if measured_time != 0 and int(result.measured_time) == 0:
                    break
            else:
                sg.popup("Unknown error happen during reading Arduino data", title = "Error Message")
                break
            
            # Add Pause buttom to stop the program
            if event == "Pause":
                break

        df_cb = pd.concat(df_cb, axis=0, ignore_index=True) # df_cb is the dataframe that stores all data points

        # time.sleep(1)
        sg.popup(str(df_cb), title = "Output")
 
window1.close()