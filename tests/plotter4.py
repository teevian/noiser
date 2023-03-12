import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window and layout
        self.setWindowTitle('Linked Plots')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        # Create the plots
        self.plot1 = pg.PlotWidget(title='Plot 1')
        self.plot2 = pg.PlotWidget(title='Plot 2')

        # Set up the y-axis scaling for the plots
        self.plot1.setYRange(-1, 1)
        self.plot2.setYRange(-0.1, 0.1)

        # Link the x-axes of the plots
        self.plot1.setXLink(self.plot2)

        # Add the plots to the layout
        self.layout.addWidget(self.plot1, 0, 0)
        self.layout.addWidget(self.plot2, 1, 0)

        # Generate some test data
        x = np.linspace(0, 10, 1000)
        y1 = np.sin(x)
        y2 = np.cos(x)

        # Add the data to the plots
        self.plot1.plot(x, y1, pen='g')
        self.plot2.plot(x, y2, pen='b')

if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
