import pandas as pd
from statistics import mean
from CTkMessagebox import CTkMessagebox
from Global_var import status

from Result import result

def default():
    diff = None
    if len(result.Output_list) > 10: # check if the result list has at least 10 elements
        df_last = result.Output_list[-1]
        if type(df_last) == pd.core.frame.DataFrame: # check if the result list contain pd dataframe
            if 'Time' in df_last.columns: # Check if the dataframe contains a column named 'Time'
                if df_last.Time.iloc[0] > 20: # Only apply the algorithm after 20s after the reaction started
                    R2_avg = mean([i.R.iloc[0] for i in result.Output_list[-3:]]) # The avg of the last 3 entries in the last 10 data points
                    R1_avg = mean([i.R.iloc[0] for i in result.Output_list[-10:-7]]) # The avg of the first 3 entries in the last 10 data points
                    diff = R2_avg - R1_avg
                    msg_display = 'The reaction stopped at ' + str(df_last.Time.iloc[0]) + 's'

                    if diff > 2:
                        status.stopping_trigger = True

                    if diff == 0:
                        if status.stopping_trigger == True:
                            if status.msgtrigger == False:
                                msg = CTkMessagebox(title="End point", message=msg_display, option_1="OK")
                                status.msgtrigger = True
    return diff