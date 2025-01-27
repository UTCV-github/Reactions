import serial

class status():
    def __init__(self):
        self.Arduino_connection_real = False # Real status of the Arduino connection
        self.Arduino_connection = False # Used to cheat in test mode
        self.ser = None
        self.TestMode = False
        self.SensorDataSelect = ['R', 'G', 'B', 'C'] # Used to store what data (rgbc) to be read from the sensor
        self.colourdict = {}
        self.stopping_trigger = False # Indicator for whether the stopping algorithm should be triggered
        self.msgtrigger = False # Indicator for whether the end point mas has been displayed
        self.LegendTrigger = True # Indicator of whether the first data point has been plotted (so that legend can be displayed)
        self.ChemicalSelected = ['Bottle ID: NA', 'KOH conc: NA', 'Dex conc: NA', 'KMnO\u2084 conc: NA']
        self.ChemicalSelectedNew = ['Bottle ID: NA', 'KOH conc: NA', 'Dex conc: NA', 'KMnO\u2084 conc: NA']
        self.folderpath = ''