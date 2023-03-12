import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from pyqtgraph import PlotWidget


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the main widget
        widget = QWidget(self)
        self.setCentralWidget(widget)

        # Create the vertical layout
        layout = QVBoxLayout(widget)

        # Create the plots
        self.plot1 = PlotWidget()
        self.plot2 = PlotWidget()

        # Add the plots to the layout
        layout.addWidget(self.plot1)
        layout.addWidget(self.plot2)

        # Set the x-axis range and enable auto-scaling on the y-axis
        self.plot1.setXRange(0, 100)
        self.plot1.setYRange(0, 6)
        self.plot1.enableAutoRange(axis=pg.ViewBox.YAxis)

        self.plot2.setXRange(0, 100)
        self.plot2.setYRange(0, 1)
        self.plot2.enableAutoRange(axis=pg.ViewBox.YAxis)

        # Generate random data for the first plot
        self.data = np.random.rand(100) * 6

        # Create the plot curves
        self.curve1 = self.plot1.plot(self.data, pen='r')
        self.curve2 = self.plot2.plot(pen='b')

        # Link the x-axes of the plots
        self.plot2.setXLink(self.plot1)

        # Connect the plot update function to a timer
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        # Generate new data for the first plot
        self.data[:-1] = self.data[1:]
        self.data[-1] = np.random.rand() * 6

        # Update the first plot curve
        self.curve1.setData(self.data)

        # Update the second plot curve based on the values of the first plot
        y = np.zeros_like(self.data)
        y[self.data >= 3] = 1
        self.curve2.setData(y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
