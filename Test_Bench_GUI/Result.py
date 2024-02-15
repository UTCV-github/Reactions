import pandas as pd

class result():
    def __init__(self):
        self.output = pd.DataFrame()
        self.Output_list = []                # Output data frame list to be converted to Output dataframe
        self.Output_save = pd.DataFrame()    # Output data frame to be saved