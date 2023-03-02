#!/usr/bin/env python

import pyqtgraph as pg

from PyQt5.QtCore import (
        QSize, Qt, pyqtSlot
        )
from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QPushButton,
        QLabel, QLineEdit, QVBoxLayout, QWidget,
        QHBoxLayout, QRadioButton, QGroupBox,
        QComboBox, QDialog, QTabWidget, QSizePolicy,
        QTextEdit, QTableWidget
        )

class NoiserWindow(QDialog):
    def __init__(self, parent = None):
        super(NoiserWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Noisr - wave analyser')
        self.setFixedSize(QSize(800, 600))
        self.setMinimumSize(QSize(600, 400))

        self.createGroupPinChoice()
        self.createTabDataAnalyzer()

        ports = ['port 1', 'port 2']
        comboBoxPorts = QComboBox()
        comboBoxPorts.addItems(ports)

        # top widgets
        layoutTop = QHBoxLayout()
        layoutTop.addWidget(QLabel("Ports:"))
        layoutTop.addWidget(comboBoxPorts)
        layoutTop.addWidget(self.groupPinChoice)
        
        # data analysis widgets (middle)
        layoutMiddle = QHBoxLayout()
        layoutMiddle.addWidget(self.bottomLeftTabWidget)
        
        # general info about connection
        layoutBottom = QHBoxLayout()
        labelArduinoDescription = QLabel('Arduino Connected')
        layoutBottom.addWidget(labelArduinoDescription)
        
        # layouts generator
        layoutMain = QVBoxLayout()

        # positioning
        layoutMain.addLayout(layoutTop)
        layoutMain.addStretch(1)
        layoutMain.addLayout(layoutMiddle)
        layoutMain.addStretch(3)
        layoutMain.addLayout(layoutBottom)

        self.setLayout(layoutMain)

    def createGroupPinChoice(self):
        layout = QHBoxLayout()
        self.groupPinChoice = QGroupBox('Analog PIN')

        buttons = [QRadioButton('A{}'.format(i)) for i in range(6)]
        buttons[0].setChecked(True)

        for pin in buttons:
            layout.addWidget(pin)

        #for pin in ['A0', 'A1', 'A2', 'A3', 'A4', 'A5']:
        #    radio_pin = QRadioButton(pin)
        #    layout.addWidget(radio_pin)

        layout.addStretch(1)
        self.groupPinChoice.setLayout(layout)

    def createTabDataAnalyzer(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Ignored)
        
        # graph
        tab2 = QWidget()
        textEdit = QTextEdit()

        plot = pg.PlotWidget()
        plot.plot([1, 2, 3, 4], [3, 4, 2, 4])

        #layout.addWidget(plot)

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(plot)
        tab2.setLayout(tab2hbox)

        # table
        tab1 = QWidget()
        tableWidget = QTableWidget(10, 10)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)

        tab1.setLayout(tab1hbox)


        self.bottomLeftTabWidget.addTab(tab1, "&Table")
        self.bottomLeftTabWidget.addTab(tab2, "Text &Edit")


def main():
    import sys
    import numpy as np

    # application singleton instance
    app = QApplication(sys.argv)
    noiserStation = NoiserWindow()
    noiserStation.show()

    sys.exit(app.exec_())


if  __name__ == '__main__':
    main()
