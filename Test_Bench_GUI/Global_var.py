import serial

class status():
    def __init__(self):
        self.Arduino_connection_real = False # Real status of the Arduino connection
        self.Arduino_connection = False # Used to cheat in test mode
        self.ser = None
        self.TestMode = False
        self.SensorDataSelect = ['R', 'G', 'B', 'C'] # Used to store what data (rgbc) to be read from the sensor
        self.colourdict = {}
        self.stopping_trigger = False
        self.msgtrigger = False