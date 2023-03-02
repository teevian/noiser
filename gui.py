#!/usr/bin/env python

import json, time
import pyqtgraph as pg

from PyQt5.QtCore import (
        QSize, Qt, pyqtSlot
        )
from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QPushButton,
        QLabel, QLineEdit, QVBoxLayout, QWidget,
        QHBoxLayout, QRadioButton, QGroupBox,
        QComboBox, QDialog, QTabWidget, QSizePolicy,
        QTextEdit, QTableWidget, QDial, QLCDNumber, QSpinBox,
        QLineEdit, QPlainTextEdit
        )

"""
Class for the main window
"""
class NoiserWindow(QDialog):
    def __init__(self, parent = None):
        super(NoiserWindow, self).__init__(parent)
        self.setupGlobalVariables()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('NOISER - wave analyser')
        self.setFixedSize(QSize(800, 600))
        self.setMinimumSize(QSize(600, 400))

        self.createGroupAnalogPinChoice()
        self.createPlotAnalyzer()
        self.createTableDataAnalyzer()
        self.createGroupControllers()

        ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']
        comboBoxPorts = QComboBox()
        comboBoxPorts.addItems(ports)

        # top widgets
        layoutTop = QHBoxLayout()
        layoutTop.addWidget(QLabel("Ports:"))
        layoutTop.addWidget(comboBoxPorts)
        
        layoutTop.addWidget(QLabel("Frequency:"))
        layoutTop.addWidget(QSpinBox())

        layoutTop.addWidget(self.groupPinChoice)
        
        # data analysis widgets (middle)
        layoutMiddle = QHBoxLayout()
        layoutMiddle.addWidget(self.tabPlotter)
        layoutMiddle.addWidget(self.table)
        
        # data controllers
        layoutGround = QHBoxLayout()

        self.logger = QPlainTextEdit()
        self.logger.setReadOnly(True)
        layoutGround.addWidget(self.logger)
        self.log("isto e um teste")
        layoutGround.addWidget(self.groupControllers)

        # general info about connection
        layoutBottom = QHBoxLayout()
        labelArduinoDescription = QLabel('Arduino Connected')
        layoutBottom.addWidget(labelArduinoDescription)
        
        # layouts generator
        layoutMain = QVBoxLayout()

        # positioning and relative weight in the window
        layoutMain.addLayout(layoutTop)
        layoutMain.addStretch(1)
        layoutMain.addLayout(layoutMiddle)
        layoutMain.addStretch(4)
        layoutMain.addLayout(layoutGround)
        layoutMain.addStretch(1)
        layoutMain.addLayout(layoutBottom)

        self.setLayout(layoutMain)

    def btPlayPauseClicked(self):
        if(self.isReading):
            self.stopReadingData()
            self.btPlayPause.setText('PLAY')
        else:
            self.startReadingData()
            self.btPlayPause.setText('PAUSE')
    
    def btLiveReadPressed(self):
        self.startReadingData()
        self.btLiveRead.setText('READING')

    def btLiveReadReleased(self):
        self.stopReadingData()
        self.btLiveRead.setText('LIVE')

    def btScheduledClicked(self):
        if(self.isReading):
            self.stopReadingData()
            self.btScheduledRead.setText('SCHEDULE')
        else:
            self.startReadingData()
            self.btScheduledRead.setText('READING')

    def bt_plot_clicked(self):
        print(self.bt_plot.isChecked())
        self.bt_plot.setEnabled(False)

    """
        Creates the group for radio pins
    """
    def createGroupAnalogPinChoice(self):
        layout = QHBoxLayout()
        self.groupPinChoice = QGroupBox('Analog PIN')

        buttons = [QRadioButton('A{}'.format(i)) for i in range(6)]
        buttons[0].setChecked(True)

        for pin in buttons:
            layout.addWidget(pin)

        layout.addStretch(1)
        self.groupPinChoice.setLayout(layout)

    def createGroupControllers(self):
        layout = QHBoxLayout()
        self.groupControllers = QGroupBox('Arduino Controller')

        # TODO change button display
        self.btPlayPause = QPushButton('PLAY')
        self.btPlayPause.clicked.connect(self.btPlayPauseClicked)

        self.btLiveRead = QPushButton('LIVE')
        self.btLiveRead.pressed.connect(self.btLiveReadPressed)
        self.btLiveRead.released.connect(self.btLiveReadReleased)

        self.btScheduledRead = QPushButton('SCHEDULE')
        self.btScheduledRead.clicked.connect(self.btScheduledClicked)

        layout.addWidget(self.btPlayPause)
        layout.addWidget(self.btLiveRead)
        layout.addWidget(self.btScheduledRead)

        self.groupControllers.setLayout(layout)

    def createTableDataAnalyzer(self):
        self.table = QWidget()
        tableWidget = QTableWidget(5, 2)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)

        self.table.setLayout(tab1hbox)

    def createPlotAnalyzer(self):
        self.tabPlotter = QTabWidget()
        self.tabPlotter.setSizePolicy(QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Ignored)

        # simple graph
        tabSimple = QWidget()

        plotSimple = pg.PlotWidget()
        plotSimple.plot([1, 2, 3, 4], [3, 4, 2, 4])

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(plotSimple)
        tabSimple.setLayout(tab2hbox)

        # complete graph
        tabComplete = QWidget()

        plotComplete = pg.PlotWidget()
        plotComplete.plot([1, 2, 3, 4], [4, 3, 2, 1])

        tab3hbox = QHBoxLayout()
        tab3hbox.setContentsMargins(5, 5, 5, 5)
        tab3hbox.addWidget(plotComplete)
        tabComplete.setLayout(tab3hbox)

        self.tabPlotter.addTab(tabSimple, "Simple")
        self.tabPlotter.addTab(tabComplete, "Complete")

    def startReadingData(self):
        self.isReading = True
        self.setWindowTitle(self.title + ' (🟢 reading...)')
        
        self.log('Started reading...', 'record')
        
    def stopReadingData(self):
        self.isReading = False
        self.setWindowTitle(self.title)

        self.log('Stopped reading.', 'stop')

    def log(self, message, type='info'):
        logMessage = time.strftime("%H:%M:%S", time.localtime()) + '\t' + message + '\t' + self.emoji_dict[type]
        self.logger.appendPlainText(logMessage)

    def setupGlobalVariables(self, configs_path='./configs.json'):
        with open(configs_path, 'r') as file_configs:
            configs = json.load(file_configs)   # its a json object

        self.title = configs['main_window']['title']
        self.isReading = configs['settings']['reading_at_startup']
        self.emoji_dict = configs['emojis_dict']

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

# readstringuntil \n