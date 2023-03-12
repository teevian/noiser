import sys
import random
from collections import deque
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Analog PIN')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        # Set up the plot widget
        self.plot_widget = pg.PlotWidget(title='Analog PIN')
        self.plot_widget.setLabel('left', 'Voltage (V)', size='18pt')
        self.plot_widget.setLabel('bottom', 'Time (s)', size='18pt')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.plot_widget.setYRange(-1, 1, padding=0)
        self.plot_widget.setFixedHeight(400)  # Prevent moving in y-axis ?

        # Add the plot widget to the layout
        self.layout.addWidget(self.plot_widget, 0, 0)

        # Initialize the data arrays
        self.data = deque(maxlen=100)
        self.x_data = np.zeros(100)
        self.y_data = np.zeros(100)

        # Plot the initial data
        self.curve = self.plot_widget.plot(self.x_data, self.y_data, pen='g', width=2, name='Voltage')

        # Add a legend to the plot
        self.plot_widget.addLegend(size=(150, 80), offset=(-10, 10))
        self.plot_widget.plotItem.legend.setLabelTextSize(16)

        # Add a label to show y-value
        self.label = pg.TextItem(anchor=(0, 1), color=(200, 200, 200))
        self.plot_widget.addItem(self.label)

        # Set up a timer to update the plot
        self.timer = QTimer(timeout=self.update_plot)
        self.timer.start(1)

    def update_plot(self):
        # Generate some random data
        new_x = self.x_data[-1] + 0.01
        new_y = 2 * random.random() - 1

        # Append the new data to the deque
        self.data.append((new_x, new_y))

        # Check if the plot needs to be updated
        if len(self.data) >= self.data.maxlen:
            self.x_data, self.y_data = zip(*self.data)
            self.curve.setData(self.x_data, self.y_data)
            self.plot_widget.setXRange(self.x_data[0], self.x_data[-1], padding=0)
            self.label.setPos(self.x_data[-1], 1)
            self.label.setText(f"Y = {self.y_data[-1]:.2f}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
