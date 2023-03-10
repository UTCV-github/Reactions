'''
This is a GUI app built for UTCV Reactions to automate the data collection process in the lab
The coce is written by: Fred Feng
'''

import PySimpleGUI as sg
import os.path
import serial
import serial.tools.list_ports
import time
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

font = ("Arial", 16)
font_2 = ("Arial", 20)

# Configure the serial port that connects the Arduino
ports = serial.tools.list_ports.comports() # Get a COM port list
ports_list = []
for port, desc, hwid in sorted(ports): # Get all COM port name
    ports_list.append("{}: {}".format(port, desc))
Arduino_eqip_list = ['Arduino Uno', 'Arduino Nano']
Arduino_port = [s for s in ports_list if any(ports_list in s for ports_list in Arduino_eqip_list)] # Pick up the ports that are connected to a Arduino device
if len(Arduino_port) < 1:
    sg.popup("No Arduino device connected", title="Warning")
    layout_config = [
        [sg.Text('Port'), sg.Combo(values = ports_list, size = (40,1), key = "-COM_Port-")],
        [sg.Text('Baud'), sg.Combo(values = [9600], default_value = 9600,size = (20,1), key = "-Baud-")],
        [sg.Button("OK"), sg.Button("Exit")] 
        ]

else: 
    layout_config = [
        [sg.Text('Port'), sg.Combo(values = ports_list,  default_value = Arduino_port[0],size = (40,1), key = "-COM_Port-")],
        [sg.Text('Baud'), sg.Combo(values = [9600], default_value = 9600,size = (20,1), key = "-Baud-")],
        [sg.Button("OK"), sg.Button("Exit")] 
        ]

window_config = sg.Window(title = "Configure the serial monitor", layout = layout_config, size=(400, 200), font = font, finalize=True)
event, values = window_config.read(close=True)

if event == "Exit":
    quit()

COM_port = values["-COM_Port-"]
Baud = values["-Baud-"]
ser = serial.Serial(COM_port, Baud, timeout=1)
time.sleep(1) # Pause for 1 sencond to wait for response from the Arduino

# Detect if the sensor is connected properly
msg = ser.readline()
if msg.decode('utf-8').rstrip() == 'Found sensor':
    sg.popup("Sensor is working properly")
else:
    sg.popup("Sensor not detected, please check your connection")

# Define the function that send command to the Arduino
def Arduino_Run(command):
    ser.write(str.encode(command))

# Define the function that saves the data as csv file(s)
def save_csv(Date, Test_bench, KOH, Trial, Data_list, save_path):
    # Date = datetime.strptime(Date, '%Y-%m-%d %H:%M:%S')
    # Date = datetime.strftime(Date, '%Y-%m-%d-%H%M%S')
    current_time = datetime.now()
    current_time = datetime.strftime(current_time, '%H%M%S') # Convert time format into a string
    Date = datetime.strptime(Date, '%Y-%m-%d') # Convert string format into a time format
    Date = datetime.strftime(Date, '%Y%m%d')
    file_name = save_path + "/" + Date + "_" + current_time + "_" + Test_bench + "_" + KOH + "_" + Trial + ".csv"

    Data_list.to_csv(file_name, index = False)

# Define the function that reads a line of Arduino output and return the readings of each parameter
def read_output(output):
    # Example output: b"R:365;G:117;B:76;C:590;cur_avg590;prev_avg590;read_idx8;Time:3.0889999866;Measured_Time:0.0000000000 \r\n"
    output = output.decode("utf-8")
    output = output[0:-5] # remove " \n\r" at the end of the string
    result = output.split(',')
    if len(result) > 3:
        # R = int(result[0][2:])
        # G = int(result[1][2:])
        # B = int(result[2][2:])
        # C = int(result[3][2:])
        # cur_avg = int(result[4][7:])
        # prev_avg = int(result[5][8:])
        # read_idx = int(result[6][8:])
        # time = float(result[7][5:])
        # Measured_time = float(result[8][14:])

        R = result[0][2:]
        G = result[1][2:]
        B = result[2][2:]
        C = result[3][2:]
        cur_avg = result[4][7:]
        prev_avg = result[5][8:]
        read_idx = result[6][8:]
        time = result[7][5:]
        Measured_time = result[8][14:]

        # Compile the results into a dataframe
        d = {'R': [R], 'G': [G], 'B': [B], 'C': [C], 'cur_avg': [cur_avg], 'prev_avg': [prev_avg], 'read_idx': [read_idx], 'time': [time], 'measured_time': [Measured_time]}
        df = pd.DataFrame(data=d)
        return df
    # return the reaction time if the output is "measured time"
    elif len(result) < 3:
        result = output.split()
        measured_time = result[1]
        return float(measured_time)

# Construct the layout of the GUI window
previous_trial = 'NA'
layout_1 = [
    [sg.Text("This is a UTCV Reactions GUI demo")], 
    [sg.Text("File save path"), sg.InputText(size=(25, 1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse()],
    [sg.Text('Test Bench (A/B/C)', size =(15, 1)), sg.Combo(values=["A", "B", "C"], default_value = "A", size=(15,1))],
    # [sg.Text("Date"), sg.Input(key = "-Date-", size=(20,1)), sg.CalendarButton("Date", close_when_date_chosen=True, target="-Date-")], # Not working if sg.read_all_windows() is used
    [sg.Text("Date"), sg.Input(key = "-Date-", size=(20,1)), sg.Button('Date')],
    [sg.Text('KOH Concentration', size =(15, 1)), sg.InputText(key = "-KOHConc-", do_not_clear=True, size=(20,1))],
    [sg.Text('Trial', size =(15, 1)), sg.InputText(key = "-trial-", do_not_clear=True, size=(15,1)), sg.Text('Previous trial: '), sg.Text(previous_trial, key = '-PreviousTrial-')],
    [sg.Text('Arduino Command'), sg.Combo(values=["s", "t"], default_value = "s", size = (15,1), key = "-Arduino_Comand-")],
    [sg.Button("Run"), sg.Button("Save as csv"), sg.Button("See Results"), sg.Button("Pause"), sg.Button("Clear"), sg.Button("Reset")],
    [sg.Button("Competition Mode", size = (25,1))]
    ]

# Construct the layout of the competition window
def make_competition_window():
    layout_competition = [
        [sg.Text("This window is used for KOH concentration calculation and time estimation")],
        [sg.Text("Car Speed (m/s): "), sg.InputText(size=(15, 1), enable_events=True, do_not_clear=True, key="-CarSpeed-")],
        [sg.Text("Distance (m): "), sg.InputText(size=(15, 1), enable_events=True, do_not_clear=True, key="-Dist-"), sg.Button("Calculate time")],
        [sg.Text("Required Time (s) "), sg.InputText(size=(15, 1), enable_events=True, key="-ReqTime-"), sg.Button("Calculate KOH mass")],
        [sg.Text("Required KOH (g) "), sg.InputText(size=(15, 1), enable_events=True, do_not_clear=True, key="-ReqKOH-")],
        [sg.Button("Clear")]
    ]
    return sg.Window(title = "Competition Mode", layout=layout_competition, font = font, finalize=True)

def input_test(dependency, output):

    return True

# Construct the layout of the result table window
result_table = []
headings_table = ['R', 'G', 'B', 'C', 'time', 'measured_time']
def make_result_window(headings_table): 
    layout_table = [
        [sg.Text('Reaction time: ', font = font), sg.Text('NA', font = font_2, key = '-ReactionTime-')],  # Add stop watch
        [sg.Text('Stop time: ', font = font), sg.Text('NA', font = font_2, key = '-StopTime-')], # Indicate total reaction time once the reaction stops
        [sg.Table( values = result_table,
                    headings = headings_table,
                    max_col_width=40,
                    auto_size_columns=False,
                    def_col_width=10,
                    display_row_numbers=True,
                    justification='middle',
                    num_rows=20,
                    key = '-ResultTable-',
                    row_height=30
        )]
    ]
    return sg.Window(title = "Sensor Reading", layout=layout_table, size=(800, 600), font = font, finalize=True, resizable=True)

# Create the window
window1 = sg.Window(title = "Reactions Test Bench GUI Demo", layout = layout_1, size=(600, 400), font = font, finalize=True)
window_result = None

# Open Pyplot interactive tool
plt.ion()
fig, ax = plt.subplots()
plt.xlabel("Time (s)")
plt.ylabel("C value")
bg = fig.canvas.copy_from_bbox(fig.bbox)

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
        if window == window_result:     # if closing win 2, mark as closed
            window_result = None
        elif window == window1:         # if closing win 1, exit program
            break
        elif window == window_competition: # if closing window_competition, mark as closed
            window_competition = None
    
    elif event == "Date":
        date = sg.popup_get_date()
        if date:
            month, day, year = date
            window['-Date-'].update(f"{year}-{month:0>2d}-{day:0>2d}")

    # Pop up result table
    elif event == "See Results" and not window_result:
        window_result = make_result_window(headings_table)
        table = window_result['-ResultTable-']
        table_widget = table.Widget
        table.expand(expand_x=True, expand_y=True)          # Expand table in both directions of 'x' and 'y'
        for cid in headings_table:
            table_widget.column(cid, stretch=True)          # Set column stretchable when window resiz

    # Pop up Competition Mode window
    elif event == "Competition Mode":
        window_competition = make_competition_window()

    elif window == window_competition:
        if event == "Calculate time":
            Req_time = float(values["-Dist-"]) / float(values["CarSpeed"])
            Req_time = round(Req_time, 4)
            window_competition["-ReqTime-"].update(Req_time)
        elif event == "Calculate KOH mass":
            KOH_mass = np.log((float(values["-ReqTime-"])-40)/396.3304)/-0.1415
            KOH_mass = round(KOH_mass, 4)
            window_competition["-ReqKOH-"].update(KOH_mass)
        elif event == "Clear":
            window_competition["-ReqTime-"].update(" ")
            window_competition["-ReqKOH-"].update(" ")


    # Save the data as a csv file using the designated path
    elif event == "Save as csv":
        if 'df_cb' in globals():
            # Data_list = [[1,2,3,4,5,6]]
            save_csv(values["-Date-"], values["-TestBench-"], values["-KOHConc-"], values["-trial-"], df_cb, values["-FOLDER-"])
            previous_trial = values["-trial-"]
            window['-PreviousTrial-'].update(previous_trial)
            sg.popup("csv file saved for test bench" + values["-TestBench-"][0], "The csv file is save at: " + values["-FOLDER-"])
        else:
            sg.popup("No data has been received", title = "Error Message")

    # Send command to Arduino and show realtime sensor readings in a plot    
    elif event == "Run":
        if window_result == None: 
            window_result = make_result_window(headings_table)
            table = window_result['-ResultTable-']
            table_widget = table.Widget
            table.expand(expand_x=True, expand_y=True)          # Expand table in both directions of 'x' and 'y'
            for cid in headings_table:
                table_widget.column(cid, stretch=True)          # Set column stretchable when window resiz

        elif values["-Arduino_Comand-"][0] == "s":
            Arduino_Run(values["-Arduino_Comand-"][0])
            measured_time = 0   # initialized the reaction time
            df_cb = []          # create a list to temporarily hold all dataframes 
            result_table = []   # Initialize the result table again
            plt.xlabel("Time (s)")
            plt.ylabel("C value")

            # Reads output
            while True: 
                output = ser.readline()
                result = read_output(output)
                if type(result) == float:
                    measured_time = result
                elif type(result) == pd.DataFrame:
                    df_cb.append(result)
                    # plt.scatter(float(result.time), int(result.C), color = 'lightblue')
                    # plt.show()
                    # plt.pause(0.001)
                    dot, = ax.plot(float(result.time), int(result.C),'.', color = 'lightblue', markersize = 5)
                    ax.draw_artist(dot)
                    fig.canvas.blit(fig.bbox) 

                    if result_table != None: 
                        result_table_row = [result.iloc[0]['R'], result.iloc[0]['G'], result.iloc[0]['B'], result.iloc[0]['C'], result.iloc[0]['time'], result.iloc[0]['measured_time']]
                        result_table.append(result_table_row)
                        window_result['-ResultTable-'].update(result_table)
                        window_result['-ReactionTime-'].update(result.iloc[0]['time'])

                        table_widget.yview_moveto(1) # Always show the last row of the table

                    if measured_time != 0 and float(result.measured_time) != 0: # When the endpoint of the reaction is detected
                        # dot, = ax.axvline(x = float(measured_time), ymin = 0, ymax = int(result['C']), color = 'red')
                        # ax.draw_artist(dot)
                        # fig.canvas.blit(fig.bbox) 
                        window_result['-StopTime-'].update(measured_time)

                    if measured_time != 0 and float(result.measured_time) == 0: # When Arduino stop printing output (The last line of the output end with "Measured_Time: 0.0000000000" )
                        sg.popup("The reaction has reached the endpoint at " + str(measured_time) + "s", title = "Reaction Message")
                        break
                else:
                    sg.popup("Unknown error happen during reading Arduino data", title = "Error Message")
                    break
                
                # Add Pause buttom to stop the program
                event, values = window1.read(timeout=1)
                if event == "Pause":
                    Arduino_Run("t")
                    break
            if len(df_cb) != 0: 
                df_cb = pd.concat(df_cb, axis=0, ignore_index=True) # df_cb is the dataframe that stores all data points
        else:
            Arduino_Run(values["-Arduino_Comand-"][0])
    
    elif event == "Pause":
        Arduino_Run("t")

    elif event == "Clear":
        Arduino_Run("t")
        ser.reset_output_buffer()
        df_cb = [] # create a list to temporarily hold all dataframes 
        result_table = [] # Initialize the result table again
        if result_table != None: 
            window_result['-ResultTable-'].update(result_table)

        # time.sleep(1)
        # sg.popup(str(df_cb), title = "Output")
    
    elif event == "Reset":
        window_result['-ReactionTime-'].update('NA') # Clear Reaction timer
        ax.cla()  # Clear the plot
        Arduino_Run("t")
        time.sleep(0.1)
        ser.close() # Restart serial port
        ser.open()
        time.sleep(1)
        msg = ser.readline()
        if msg.decode('utf-8').rstrip() == 'Found sensor':
            sg.popup("Sensor is working properly")
        else:
            sg.popup("Sensor not detected, please check your connection")

 
window1.close()