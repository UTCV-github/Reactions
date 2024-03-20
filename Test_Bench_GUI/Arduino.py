from Global_var import status
import customtkinter
from CTkMessagebox import CTkMessagebox
import pandas as pd
import re
import serial



class Arduino():
    def __init__(self):
        pass

    def execute(command):
        if status.Arduino_connection == False:
            msg = CTkMessagebox(title="Connection ERROR", message="Arduino is not connected", icon="warning", option_1="OK")
        elif command not in ["s", "t"]:
            msg = CTkMessagebox(title="Command ERROR", message="The command cannot be interpreted", icon="warning", option_1="OK")
        else:
            status.ser.write(str.encode(command))

    def read_output():
        ser = status.ser
        output_line = ser.readline()
        output_line = output_line.decode("utf-8")
        output_line = output_line[0:-5]
        output_line_split = re.split(', |:', output_line) # Split the result using ", " or "."
        if len(output_line_split) % 2 == 1:     # Make sure the length of the list is even
            output_line_split = output_line_split[:-1]
        output_dict = {output_line_split[i]: output_line_split[i + 1] for i in range(0, len(output_line_split), 2)}
        desired_keys = ['R', 'G', 'B', 'C', 'Time']
        filtered_dict = {key: [float(value)] for key, value in output_dict.items() if key in desired_keys}
        _time = float(filtered_dict['Time'][0])
        filtered_dict['Time'] = float("{:.3f}".format(_time))
        df = pd.DataFrame(filtered_dict)
        # print(df)
        # if output_type == "df": 
        #     return df
        
        # elif output_type == "dict":
        #     return filtered_dict
        
        # else:
            # return df 
        return df
    
    def read_output_raw():
        ser = status.ser
        output_line = ser.readline()
        output_line = output_line.decode("utf-8")
        output_line = output_line[0:-5] # remove " \n\r" at the end of the string

        return output_line 

    def clear_buffer():
        ser = status.ser
        ser.reset_output_buffer()
    
