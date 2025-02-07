from ftplib import FTP
from io import BytesIO
import json
import os
from CTkMessagebox import CTkMessagebox
import pandas as pd

class FTPCommunication():
    def __init__(self):

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
            msg = CTkMessagebox(title="FTP error", message = 'Cannot find FTP configuration', icon="warning", option_1="OK")

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
        
        if df.equals(self.ftp_to_dataframe(hostname, username, password, filename)):
            msg = CTkMessagebox(title="FTP message", message = 'Chemical list updated!', icon="check", option_1="OK")