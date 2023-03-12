
import numpy as np
import pyqtgraph as pg

from collections import deque


class Plotter(pg.PlotWidget):
    def __init__(self):
        super().__init__(title='Analog PIN')

        self.setLabel('left', 'Voltage (V)', size='18pt')
        self.setLabel('bottom', 'Time (s)', size='18pt')

        self.showGrid(x=True, y=True, alpha=0.6)
        #self.setYRange(-1, 1, padding=0)
        #self.setFixedHeight(400)  # Prevent moving in y-axis
        self.setAspectLocked(lock=True, ratio=1)

        self.addLegend(size=(150, 80), offset=(-10, 10))
        self.plotItem.legend.setLabelTextSize(16)

        # Add a label to show y-value
        self.label = pg.TextItem(anchor=(0, 1), color=(200, 200, 200))
        self.addItem(self.label)

        self.data = deque(maxlen=100)
        self.x_data = np.zeros(100)
        self.y_data = np.zeros(100)

        #self.curve = self.plot(self.x_data, self.y_data, pen='g', width=2, name='Voltage')
    
    def update(self, data, flag=''):
        pass


