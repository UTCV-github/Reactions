from typing import Tuple
import customtkinter
from CTkTable import *
import pandas as pd
from CTkMessagebox import CTkMessagebox

from FTPBackup import FTPCommunication

class Inventory_window(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.HeaderContent = [['Item', 'Volume', 'VolumeUnit', 'Type', 'Material', 'Size', 'Accuracy', 'Usage', 'SKU', 'Brand', 'Quantity', 'Note', 'Location']]
        self.ls_table = []
        self.header = CTkTable(self, row=1, column=len(self.HeaderContent[0]), values=self.HeaderContent, header_color='lightblue', corner_radius=0, width=145)
        self.header.grid(padx=5, pady=(5,5), row=0, column=0, columnspan=6)

        self.tableframe = customtkinter.CTkScrollableFrame(self, width=146*len(self.HeaderContent[0])-1+13, height=1000)
        self.tableframe.grid(padx=5, pady=0, row=1, column=0, columnspan=6)

        self.table = CTkTable(self.tableframe, row=10, column=len(self.HeaderContent[0]), values=self.ls_table, corner_radius=5, pady=1, width=145)
        self.table.grid(padx=(0,13), pady=0, row=1, column=0, columnspan=6)

        self.button_Import = customtkinter.CTkButton(self, text="IMPORT", command=None)
        self.button_Import.grid(row=2, column=0, padx=10, pady=(10,0), sticky="ew")

        self.button_Add = customtkinter.CTkButton(self, text="Add", command=self.AddInventory)
        self.button_Add.grid(row=2, column=1, padx=10, pady=(10,0), sticky="ew")
        
        self.button_Remove = customtkinter.CTkButton(self, text="REMOVE", command=None)
        self.button_Remove.grid(row=2, column=2, padx=10, pady=(10,0), sticky="ew")

    def import_list(self):
        return None

    def AddInventory(self):
        self.AddInventory_window = AddInventoryWindow()
    
    def RemoveInventory(self):
        return None
    
class AddInventoryWindow(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("Inventory registeration")
        self.geometry("420x600")
        self.after(10, self.lift) # Add this to keep the new window float atop

        # Read pre set drop down menu values
        self.Menu_list = pd.read_csv('Inventory/Menu_list.csv')
        self.Menu_list = self.Menu_list.to_dict(orient='list')
        for key, value in self.Menu_list.items():
            self.Menu_list[key] = [x for x in value if not pd.isna(x)]

        for i, (key, value) in enumerate(self.Menu_list.items()):
            globals()[f"label_{key}"] = customtkinter.CTkLabel(self, text=key, anchor="w")
            globals()[f"label_{key}"].grid(row=i, column=0, padx=10, pady=(5, 0), sticky="nsew")
            globals()[f"input_{key}"] = self.InputBoxGenerator(key, value)
            globals()[f"input_{key}"].grid(row=i, column=1, padx=10, pady=(5, 0), sticky="nsew", columnspan = 2)

        self.button_Register = customtkinter.CTkButton(self, text="Register", command=self.RegisterInventory)
        self.button_Register.grid(row=i+1, column=2, padx=10, pady=(10,0), sticky="ew")



    def InputBoxGenerator(self, InputBobText, Menu_list):
        if type(Menu_list) == list:
            if len(Menu_list) == 0:
                output = customtkinter.CTkEntry(self, placeholder_text=InputBobText, width = 300)
            else:
                output = customtkinter.CTkOptionMenu(self, dynamic_resizing=False, values= Menu_list, width = 300)

            return output
        
    def RegisterInventory(self):
        ls_new_entry = []
        for i, (key, value) in enumerate(self.Menu_list.items()):
            ls_new_entry.append(globals()[f"input_{key}"].get())
        
        if input_Item.get() == '':
            msg = CTkMessagebox(title="System Error", message="Item name is needed to register inventory",
                    icon="warning", option_1="OK")
        else:    
            InventorySheet = pd.read_csv('Inventory/InventorySheet.csv')

            if InventorySheet.shape[1] != len(ls_new_entry):
                msg = CTkMessagebox(title="System Error", message="Current version of the inventory sheet is inconsitent with the template",
                        icon="warning", option_1="OK")
            else:
                InventorySheet.loc[len(InventorySheet)] = ls_new_entry
                InventorySheet.to_csv('Inventory/InventorySheet.csv', index=False)

        





