from ftplib import FTP
from io import BytesIO
import pandas as pd
import customtkinter
from CTkMessagebox import CTkMessagebox

class chemicals(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.file_path = '/'
        self.title("Chemical registeration")
        self.geometry("400x400")
        self.after(10, self.lift) # Add this to keep the new window float atop

        self.label_KohConc = customtkinter.CTkLabel(self, text="Input the KOH concentration", anchor="w")
        self.label_KohConc.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_KohConc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_KohConc.grid(row=5, column=0, padx=10, pady=(0, 10))

        self.entry_KohConc = customtkinter.CTkEntry(self, placeholder_text="KOH concentration")
        self.entry_KohConc.grid(row=5, column=1, columnspan=2, padx=(20, 0), pady=(0, 10), sticky="nsew")

        self.label_DexConc = customtkinter.CTkLabel(self, text="Input the Dextrose concentration", anchor="w")
        self.label_DexConc.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_DexConc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_DexConc.grid(row=7, column=0, padx=10, pady=(0, 10))

        self.entry_DexConc = customtkinter.CTkEntry(self, placeholder_text="Dex concentration")
        self.entry_DexConc.grid(row=7, column=1, columnspan=2, padx=(20, 0), pady=(0, 10), sticky="nsew")

        self.label_Kmno4Conc = customtkinter.CTkLabel(self, text="Input the KMnO\u2084 concentration", anchor="w")
        self.label_Kmno4Conc.grid(row=8, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.optionmenu_Kmno4Conc = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                        values=["g/500mL", "g/100mL", "g/25mL", "M", "wt%"])
        self.optionmenu_Kmno4Conc.grid(row=9, column=0, padx=10, pady=(0, 20))

        self.entry_Kmno4Conc = customtkinter.CTkEntry(self, placeholder_text="KMnO\u2084 concentration")
        self.entry_Kmno4Conc.grid(row=9, column=1, columnspan=2, padx=(20, 0), pady=(0, 20), sticky="nsew")

    def ftp_to_dataframe(hostname, username, password, filename):
        # Connect to the FTP server
        with FTP(hostname) as ftp:
            ftp.login(username, password)
            
            # Navigate to the directory containing the CSV file
            ftp.cwd('/')
            
            # Download the CSV file
            csv_data = BytesIO()
            ftp.retrbinary('RETR ' + filename, csv_data.write)
            csv_data.seek(0)  # Reset file pointer to beginning
            
            # Convert CSV data to pandas DataFrame
            df = pd.read_csv(csv_data)
            
            return df
        
    def dataframe_to_ftp(df, hostname, username, password, filename):
        # Convert DataFrame to CSV string
        csv_data = df.to_csv(index=False)
        
        # Connect to the FTP server
        with FTP(hostname) as ftp:
            ftp.login(username, password)
            
            # Navigate to the directory where you want to save the CSV file
            ftp.cwd('/path/to/directory')
            
            # Upload the modified CSV file
            ftp.storbinary('STOR ' + filename, BytesIO(csv_data.encode()))
            print("File updated successfully.")