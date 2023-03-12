import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import numpy as np
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plotting Example")

        # Create a plot widget and add it to the main window
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        # Create two plot items (curves)
        self.curve1 = self.plot_widget.plot(pen=pg.mkPen(color=(244, 0, 2)))
        self.curve2 = self.plot_widget.plot(pen=pg.mkPen(color=(0, 1, 2), style=pg.QtCore.Qt.DotLine))

        # Initialize data arrays for the curves
        self.x = np.linspace(0, 10, 1000)
        self.y1 = np.zeros_like(self.x)
        self.y2 = np.zeros_like(self.x)

        # Set up a timer to update the first curve in real-time
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(50)

    def update_data(self):
        # Generate new random data for the first curve
        self.y1 = np.random.rand(len(self.x))

        # Update the first curve
        self.curve1.setData(self.x, self.y1)

        # Update the second curve to be a horizontal line at the maximum value of the first curve
        max_y1 = np.max(self.y1)
        self.y2 = np.full_like(self.x, max_y1)
        self.curve2.setData(self.x, self.y2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
