from ftplib import FTP
from io import BytesIO
from typing import Tuple
import pandas as pd
import customtkinter
from CTkMessagebox import CTkMessagebox
from CTkTable import *
from CTkTableRowSelector import *
import json
import os
import datetime
import random

from FTPBackup import FTPCommunication
from Global_var import status

class ChemicalRegister(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.register_status = False # Check if all requirent is met before uploading to ftp server
        self.config_path = 'Config/Config.json'

        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as json_file:
                data = json.load(json_file)['ftp'][0]

            self.hostname = data['hostname']
            self.username = data['username']
            self.pswd = data['password']
            self.group = data['group']
            self.FileName = data['file name']

        else: 
            msg = CTkMessagebox(title="FTP error", message = 'Cannot find FTP configuration', icon="cancel", option_1="OK")

        self.file_path = '/' # default ftp filepath
        self.title("Chemical registeration")
        self.geometry("400x400")
        self.after(10, self.lift) # Add this to keep the new window float atop

        self.label_KohConc = customtkinter.CTkLabel(self, text="Input the KOH concentration", anchor="w")
        self.label_KohConc.grid(row=4, column=0, padx=10, pady=(5, 0), sticky="nsew")

        self.optionmenu_KohConc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_KohConc.grid(row=5, column=0, padx=10, pady=(0, 10))

        self.entry_KohConc = customtkinter.CTkEntry(self, placeholder_text="KOH concentration")
        self.entry_KohConc.grid(row=5, column=1, columnspan=2, padx=(20, 0), pady=(0, 5), sticky="nsew")

        self.label_DexConc = customtkinter.CTkLabel(self, text="Input the Dextrose concentration", anchor="w")
        self.label_DexConc.grid(row=6, column=0, padx=10, pady=(5, 0), sticky="nsew")

        self.optionmenu_DexConc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_DexConc.grid(row=7, column=0, padx=10, pady=(0, 5))

        self.entry_DexConc = customtkinter.CTkEntry(self, placeholder_text="Dex concentration")
        self.entry_DexConc.grid(row=7, column=1, columnspan=2, padx=(20, 0), pady=(0, 5), sticky="nsew")

        self.label_Kmno4Conc = customtkinter.CTkLabel(self, text="Input the KMnO\u2084 concentration", anchor="w")
        self.label_Kmno4Conc.grid(row=8, column=0, padx=10, pady=(5, 0), sticky="nsew")

        self.optionmenu_Kmno4Conc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/500mL", "g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_Kmno4Conc.grid(row=9, column=0, padx=10, pady=(0, 5))

        self.entry_Kmno4Conc = customtkinter.CTkEntry(self, placeholder_text="KMnO\u2084 concentration")
        self.entry_Kmno4Conc.grid(row=9, column=1, columnspan=2, padx=(20, 0), pady=(0, 5), sticky="nsew")

        self.label_Maker = customtkinter.CTkLabel(self, text="The chemical is prepared by", anchor="w")
        self.label_Maker.grid(row=10, column=0, padx=10, pady=(5, 0), sticky="nsew")

        self.entry_Maker = customtkinter.CTkEntry(self, placeholder_text="Your name (Optional)")
        self.entry_Maker.grid(row=11, column=0, columnspan=3, padx=(20, 0), pady=(0, 5), sticky="nsew")

        self.label_Note = customtkinter.CTkLabel(self, text="Note", anchor="w")
        self.label_Note.grid(row=12, column=0, padx=10, pady=(5, 0), sticky="nsew")

        self.entry_Note = customtkinter.CTkEntry(self, placeholder_text="Note (Optional)")
        self.entry_Note.grid(row=13, column=0, columnspan=3, padx=(20, 0), pady=(0, 5), sticky="nsew")

        self.button_register = customtkinter.CTkButton(self, text="REGISTER", command=self.ChemicalRegister)
        self.button_register.grid(row=14, column=0, padx=10, pady=(10,0), sticky="ew")

    def ChemicalRegister(self):
        KohConc = self.entry_KohConc.get()
        DexConc = self.entry_DexConc.get()
        KMnO4Conc = self.entry_Kmno4Conc.get()
        Maker = self.entry_Maker.get()
        Note = self.entry_Note.get()

        KohUnit = self.optionmenu_KohConc.get()
        DexUnit = self.optionmenu_DexConc.get()
        KMnO4Unit = self.optionmenu_Kmno4Conc.get()

        if KohConc == '':
            msg = CTkMessagebox(title="Misssing value", message = 'KOH concentration is missing', icon="warning", option_1="OK")
        else:
            if DexConc == '':
                msg = CTkMessagebox(title="Misssing value", message = 'Dextrose concentration is missing', icon="warning", option_1="OK")
            else:
                if KMnO4Conc == '':
                    msg = CTkMessagebox(title="Misssing value", message = 'KMnO\u2084 concentration is missing', icon="warning", option_1="OK")
                else:
                    self.register_status = True

        # Convert the unit user select into the format that the csv accepts
        dict_UnitConversion = {"g/500mL": 'g_500mL', "g/100mL": 'g_100mL', "g/25mL": 'g_25mL', "M": 'M', "wt%": 'wt'}
        KohUnit_save = dict_UnitConversion[KohUnit]
        DexUnit_save = dict_UnitConversion[DexUnit]
        KMnO4Unit_save = dict_UnitConversion[KMnO4Unit]

        if self.register_status == True:
            df_ChemicalList = self.ftp_to_dataframe(self.hostname, self.username, self.pswd, self.FileName)
            print('FTP: file downloaded')

            ls_Sol_ID_existing = df_ChemicalList['Sol_ID'].tolist()
            sol_ID = self.group + self.SolIDGenerator(ls_Sol_ID_existing)

            new_row = {'Sol_ID': [sol_ID], 
                    'KOH_conc': [KohConc], 'KOH_unit': [KohUnit_save],
                    'Dex_conc': [DexConc], 'Dex_unit': [DexUnit_save], 
                    'KMnO4_conc': [KMnO4Conc], 'KMnO4_unit': [KMnO4Unit_save], 
                    'Producer': [Maker], 
                    'Time': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")], 
                    'Notes': [Note]}
            
            df_new_row = pd.DataFrame(new_row)

            df_ChemicalList = pd.concat([df_ChemicalList, df_new_row], ignore_index=True)
            self.dataframe_to_ftp(df_ChemicalList, self.hostname, self.username, self.pswd, self.FileName)

        else:
            msg = CTkMessagebox(title="FTP error", message = 'Registration filed', icon="cancel", option_1="OK")

        

    def SolIDGenerator(self, existing_list):
        while True:
            new_ID = '{:04d}'.format(random.randint(0, 9999)) # Generate a 4-digit code randomly
            if new_ID not in existing_list:
                return new_ID


    def ftp_to_dataframe(self, hostname, username, password, filename):
        # Connect to the FTP server
        with FTP(hostname) as ftp:
            ftp.login(username, password)
            print('FTP: successfully log in')
            
            # Navigate to the directory containing the CSV file
            ftp.cwd('/')
            
            # Download the CSV file
            csv_data = BytesIO()
            ftp.retrbinary('RETR ' + filename, csv_data.write)
            csv_data.seek(0)  # Reset file pointer to beginning
            
            print('FTP: file read')
            # Convert CSV data to pandas DataFrame
            df = pd.read_csv(csv_data)
            
            ftp.quit()

        return df
        
    def dataframe_to_ftp(self, df, hostname, username, password, filename):
        # Convert DataFrame to CSV string
        csv_data = df.to_csv(index=False)
        
        # Connect to the FTP server
        with FTP(hostname) as ftp:
            ftp.login(username, password)
            
            # Navigate to the directory where you want to save the CSV file
            ftp.cwd('/')
            
            # Upload the modified CSV file
            ftp.storbinary('STOR ' + filename, BytesIO(csv_data.encode()))
        
        msg = CTkMessagebox(title="FTP message", message = 'Chemical registered successfully', icon="check", option_1="OK")

class ChemicalSelection(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.FTP = FTPCommunication()
        self.config_path = 'Config/Config.json'

        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as json_file:
                data = json.load(json_file)['ftp'][0]

            self.hostname = data['hostname']
            self.username = data['username']
            self.pswd = data['password']
            self.group = data['group']
            self.FileName = data['file name']
        else: 
            msg = CTkMessagebox(title="FTP error", message = 'Cannot find FTP configuration', icon="cancel", option_1="OK")

        self.title("Chemical selection")
        self.geometry("940x500")
        self.after(10, self.lift) # Add this to keep the new window float atop

        self.df_raw = self.DfDownload()
        self.ls_table = self.Df2Table(self.df_raw)
        self.HeaderContent = [['Bottle ID', 'KOH conc','Dex conc', 'KMnO\u2084 conc', 'Prepared by', 'Time']]

        self.header = CTkTable(self, row=1, column=6, values=self.HeaderContent, header_color='lightblue', corner_radius=0, width=145)
        self.header.grid(padx=0, pady=(5,5), row=0, column=0, columnspan=3)

        self.tableframe = customtkinter.CTkScrollableFrame(self, width=900, height=410)
        self.tableframe.grid(padx=5, pady=0, row=1, column=0, columnspan=3)

        self.table = CTkTable(self.tableframe, row=20, column=6, values=self.ls_table, corner_radius=5, pady=1, width=145)
        self.table.grid(padx=13, pady=0, row=1, column=0, columnspan=3)

        self.button_update = customtkinter.CTkButton(self, text="Update", command=self.TableUpdate)
        self.button_update.grid(row=2, column=0, padx=10, pady=(5,0), sticky="ew")

        self.button_select = customtkinter.CTkButton(self, text="Select", command=self.ChemicalSelect)
        self.button_select.grid(row=2, column=1, padx=10, pady=(5,0), sticky="ew")

        self.button_delete = customtkinter.CTkButton(self, text="Delete", command=self.RowDeleteSelection)
        self.button_delete.grid(row=2, column=2, padx=10, pady=(5,0), sticky="ew")

        self.row_selector = CTkTableRowSelector(self.table, can_select_headers=True)

    def DfDownload(self):
        df_new_raw = self.FTP.ftp_to_dataframe(self.hostname, self.username, self.pswd, self.FileName)
        df_new_raw = df_new_raw.fillna('NaN') # Avoid nan values in the final list because it cannot be recognised
        return df_new_raw

    # Only used after DfDownload in the __ini__ part
    def Df2Table(self, df: pd.DataFrame):
        df_new = df[['Sol_ID', 'KOH_conc', 'Dex_conc', 'KMnO4_conc', 'Producer', 'Time']]
        return df_new.values.tolist()

    def TableDownload(self):
        df_new_raw = self.DfDownload()
        df_new = df_new_raw[['Sol_ID', 'KOH_conc', 'Dex_conc', 'KMnO4_conc', 'Producer', 'Time']]
        return df_new.values.tolist() # return list

    def TableUpdate(self):
        self.ls_table = self.TableDownload()
        self.table.update_values(self.ls_table)

    def RowSelect(self):
        selected_row = self.row_selector.get() # get a list ([] or [['','','','']])
        if selected_row == []:
            msg = CTkMessagebox(title="Selection error", message = 'Please slect a row', icon="cancel", option_1="OK")
        else:
            if selected_row[0] in self.ls_table:
                return selected_row[0] # return a list
            
            else:
                msg = CTkMessagebox(title="Selection error", message = 'Please slect a row with data', icon="cancel", option_1="OK")

    def ChemicalSelect(self):
        selected_row = self.RowSelect()
        if selected_row != None:
            SolID = selected_row[0]
            df_SelectedRow = self.df_raw[self.df_raw['Sol_ID'] == SolID]

            dict_UnitConversion_reverse = {'g_500mL': "g/500mL", 'g_100mL': "g/100mL", 'g_25mL': "g/25mL", 'M': "M", 'wt': "wt%"}

            SolID = df_SelectedRow['Sol_ID'].iloc[0]
            KOH_conc = df_SelectedRow['KOH_conc'].iloc[0]
            KOH_unit = df_SelectedRow['KOH_unit'].iloc[0]
            Dex_conc = df_SelectedRow['Dex_conc'].iloc[0]
            Dex_unit = df_SelectedRow['Dex_unit'].iloc[0]
            KMnO4_conc = df_SelectedRow['KMnO4_conc'].iloc[0]
            KMnO4_unit = df_SelectedRow['KMnO4_unit'].iloc[0]

            SolID_complete = 'Bottle ID: ' + SolID
            KOH_ConcUnit = 'KOH conc: ' + str(KOH_conc) + ' ' + dict_UnitConversion_reverse[KOH_unit]
            Dex_ConcUnit = 'Dex conc: ' + str(Dex_conc) + ' ' + dict_UnitConversion_reverse[Dex_unit]
            KMnO4_ConcUnit = 'KMnO\u2084 conc: ' + str(KMnO4_conc) + ' ' + dict_UnitConversion_reverse[KMnO4_unit]

            status.ChemicalSelectedNew = [SolID_complete, KOH_ConcUnit, Dex_ConcUnit, KMnO4_ConcUnit]

    def RowDeleteSelection(self):
        selected_row = self.RowSelect()
        if selected_row != None:
            if selected_row in self.ls_table:
                msg_displayed = 'Are you sure you want to delete the selected row? This action is permanent!'
                msg = CTkMessagebox(title="Delete Warning", message = msg_displayed, icon="warning", option_1="Cancel", option_2 = "Confirm")
                if msg.get()=="Confirm":
                    self.RowDelete(selected_row)
            else:
                msg = CTkMessagebox(title="Selection error", message = 'Row selected does not exist', icon="cancel", option_1="OK")

    # Complete the delete operation
    def RowDelete(self, selected_row):
        self.ls_table.remove(selected_row)
        self.table.update_values(self.ls_table)
        SolID_delete = selected_row[0]
        self.df = self.df_raw[self.df_raw['Sol_ID'] != SolID_delete]
        self.FTP.dataframe_to_ftp(self.df, self.hostname, self.username, self.pswd, self.FileName)


class SolutionSelected(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.label_SolID = customtkinter.CTkLabel(self, text='Bottle ID: NA', width=300, anchor='w')
        self.label_SolID.grid(row = 0, column=0, padx=8, pady=(2,0))
        self.label_KOH_conc = customtkinter.CTkLabel(self, text='KOH conc: NA', width=300, anchor='w')
        self.label_KOH_conc.grid(row = 1, column=0, padx=8, pady=(2,0))
        self.label_Dex_conc = customtkinter.CTkLabel(self, text='Dex conc: NA', width=300, anchor='w')
        self.label_Dex_conc.grid(row = 2, column=0, padx=8, pady=(2,0))
        self.label_KMnO4_conc = customtkinter.CTkLabel(self, text='KMnO\u2084 conc: NA', width=300, anchor='w')
        self.label_KMnO4_conc.grid(row = 3, column=0, padx=8, pady=(2,0))

         
if __name__ == '__main__':
    root = customtkinter.CTk()

    TestButton = customtkinter.CTkButton(root, text="ChemicalRegister", command=ChemicalRegister)
    TestButton.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")

    TestButton = customtkinter.CTkButton(root, text="ChemicalSeletion", command=ChemicalSelection)
    TestButton.grid(row=1, column=0, padx=10, pady=(10,0), sticky="ew")

    # with open('Config/test.json', "r") as json_file:
    #     data = json.load(json_file)['ftp'][0]

    # hostname = data['hostname']
    # username = data['username']
    # pswd = data['password']
    
    # df_test = ChemicalRegister.ftp_to_dataframe(hostname, username, pswd, 'Test_file.csv')

    # print(df_test.columns)

    root.mainloop()
         