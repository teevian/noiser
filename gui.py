## CODE

import pyqtgraph as pg

from PyQt5.QtCore import (
        QSize, Qt, pyqtSlot
        )
from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QPushButton,
        QLabel, QLineEdit, QVBoxLayout, QWidget,
        QHBoxLayout, QRadioButton, 
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Noisr - wave analyser')
        self.setFixedSize(QSize(800, 600))
        self.setMinimumSize(QSize(600, 400))

        self.label = QLabel()
        
        self.input = QLineEdit()
        self.input.textChanged.connect(self.label.setText)

        # plot button
        self.bt_plot = QPushButton('RECORD')
        self.bt_plot.setCheckable(True)
        self.bt_plot.clicked.connect(self.bt_plot_clicked)

        # live read (reads arduino while pressed)
        self.bt_liveRead = QPushButton('live read')
        self.bt_liveRead.setCheckable(True)
        self.bt_liveRead.pressed.connect(self.bt_liveRead_pressed)
        self.bt_liveRead.released.connect(self.bt_liveRead_released)

        layout = QVBoxLayout()
        layout_select_pin = QHBoxLayout()

        for i in range(6):
            bt_radio_pin = QRadioButton(str(i), self)
            bt_radio_pin.setChecked(False)
            layout_select_pin.addWidget(bt_radio_pin)
        
        plot = pg.PlotWidget()
        plot.plot([1, 2, 3, 4], [3, 4, 2, 4])

        layout.addLayout(layout_select_pin)
        layout.addWidget(plot)
        
        layout.addWidget(self.input)
        layout.addWidget(self.label)
        layout.addWidget(self.bt_liveRead)
        layout.addWidget(self.bt_plot)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    @pyqtSlot()
    def bt_plot_clicked(self):
        print(self.bt_plot.isChecked())
        self.bt_plot.setEnabled(False)

    @pyqtSlot()
    def bt_liveRead_pressed(self):
        title = 'Noiser GUI'
        self.setWindowTitle(title + ' (LIVE reading...)')

        print("reading...")

    @pyqtSlot()
    def bt_liveRead_released(self):
        title = 'Noiser GUI'
        self.setWindowTitle(title)

        print("stopped reading!")

def main():
    import sys
    import numpy as np

    # application singleton instance
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if  __name__ == '__main__':
    main()
