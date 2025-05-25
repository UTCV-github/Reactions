from pathlib import Path
import pandas as pd
import numpy as np

class dsp_file:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.header = {}
        self.wavelengths = []
        self.absorbance = []
        self.read()

    def read(self):
        """
        Reads and parses a VisionLite .dsp text file.

        This method performs the following steps:
        - Loads the .dsp file and strips blank lines.
        - Parses header metadata from the top of the file.
        - Searches for the '#DATA' line that indicates the start of absorbance values.
        - Reads the absorbance values into a NumPy array.
        - Constructs a NumPy array of wavelength values using the start, end, and increment from the header.

        Raises:
            ValueError: If the '#DATA' marker is not found or if the number of data points doesn't match the header.
        """
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = lines = ['' if line == '\n' else line.strip() for line in f] # Strip the '\n' at the end of the line but keep empty lines

        # Find the #DATA line index
        try:
            data_index = lines.index('#DATA')
        except ValueError:
            raise ValueError("No #DATA line found in DSP file.")

        self.header['file_id'] = lines[0]
        self.header['mode'] = lines[1]
        self.header['scan_number'] = lines[2]
        self.header['filename'] = lines[3]
        self.header['wavelength_unit'] = lines[4]
        self.header['start_wavelength'] = float(lines[5])
        self.header['end_wavelength'] = float(lines[6])
        self.header['interval'] = float(lines[7])
        self.header['num_points'] = int(lines[8])
        self.header['measurement_mode'] = lines[9]

        self.header['Operator'] = lines[13]
        self.header['Description'] = lines[14]
        self.header['Created'] = lines[15]
        self.header['Last_modified'] = lines[16]
        self.header['Baseline'] = lines[17]

        self.header['Method'] = lines[20]

        self.header['Spectrophotometer'] = lines[28]
        self.header['Firmware'] = lines[29]
        self.header['Serial_Number'] = lines[29]

        self.header['Software_version'] = lines[42]

        self.header['Scan_speed'] = lines[62]
        

        # Determine the y axis name based on measurement mode
        self.yaxis_name = 'Unknown'
        if self.header['measurement_mode'] == "A":
            self.yaxis_name = 'Absorbance'
        if self.header['measurement_mode'] == "%T":
            self.yaxis_name = 'Transmittance'

        self.wavelengths = np.linspace(
            self.header['start_wavelength'],
            self.header['end_wavelength'],
            self.header['num_points']
            )
        self.absorbance = np.array(lines[data_index +1 :data_index + 1 + self.header['num_points']], dtype=float)

    def to_dataframe(self):
        """Return the spectral data as a pandas DataFrame."""
        return pd.DataFrame({
            f"Wavelength ({self.header['wavelength_unit']})": self.wavelengths,
            self.yaxis_name: self.absorbance
        })