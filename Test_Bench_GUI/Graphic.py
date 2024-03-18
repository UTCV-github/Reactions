import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import queue
import pandas as pd
from Global_var import status

# For testing
import threading
import time 

# SensorReadingQueue = queue.Queue()
# j = 0

class Plotting():

    def __init__(self, SensorReadingQueue):
        
        self.win = pg.GraphicsLayoutWidget(show=True, title='Chameleon: Sensor Reading')
        self.win.resize(600,400)
        self.win.setBackground('#EFE0B9')

        # Enable antialiasing for prettier plots
        # pg.setConfigOptions(antialias=True)

        self.p1 = self.win.addPlot(title="Sensor Reading")
        self.p1.getAxis('bottom').setPen('black')
        self.p1.getAxis('bottom').setTextPen('black')
        self.p1.getAxis('left').setPen('black')
        self.p1.getAxis('left').setTextPen('black')
        self.p1.showGrid(x=True, y=True)
        self.p1.addLegend()

        # for column in status.SensorDataSelect:
        #     self.p1.plot(x = None, y = None,  pen='y', name = column, symbol='o', symbolBrush=status.colourdict[column], symbolSize=5)

        # pg.exec()

        self.OutputQueue = SensorReadingQueue
        self.empty = False

        QtCore.qInstallMessageHandler(self.handler) # Inhibit the Qt Warning msg

    # Special function to inhibit the Qt warning msg
    def handler(self, msg_type, msg_log_context, msg_string):
        pass

    def update(self):
        data = self.OutputQueue.get()
        if isinstance(data, pd.DataFrame):
            if len(status.SensorDataSelect) > 0:
                if status.LegendTrigger == True: 
                    for column in status.SensorDataSelect:
                        x_value = data.Time.iloc[-1]
                        y_value = data[column].iloc[-1]
                        self.p1.plot(x = [x_value], y = [y_value], name = column,  pen='y', symbol='o', symbolBrush=status.colourdict[column], symbolSize=5)
                    status.LegendTrigger = False
                else:
                    for column in status.SensorDataSelect:
                        x_value = data.Time.iloc[-1]
                        y_value = data[column].iloc[-1]
                        self.p1.plot(x = [x_value], y = [y_value],  pen='y', symbol='o', symbolBrush=status.colourdict[column], symbolSize=5)

# ### For testing
# def test(test_Queue):
#     i = 0
#     while i < 50 :
#         _time = np.random.randint(100)
#         _r = np.random.randint(1000)
#         _g = np.random.randint(1000)
#         _b = np.random.randint(1000)
#         _c = np.random.randint(1000)
#         i += 1
#         test_pd = pd.DataFrame({'Time': [i], 'R': [_r], 'G': [_g], 'B': [_b], 'C': [_c]})
#         test_Queue.put(test_pd)
#         print('Data placed in Queue')
#         time.sleep(0.2)

# thread1 = threading.Thread(target=test, args=(SensorReadingQueue,))
# thread1.start() 

# if __name__ == '__main__':
#     # pg.exec()
#     Plotting(SensorReadingQueue)