#!/usr/bin/env python

import json, time, os
import pyqtgraph as pg
import factory

from msgid import _
from events import *
from PyQt5.QtCore import (
        QSize, Qt, pyqtSlot
        )
from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QPushButton,
        QLabel, QLineEdit, QVBoxLayout, QWidget,
        QHBoxLayout, QRadioButton, QGroupBox,
        QComboBox, QDialog, QTabWidget, QSizePolicy,
        QTextEdit, QTableWidget, QDial, QLCDNumber, QSpinBox,
        QLineEdit, QPlainTextEdit, QMenuBar, QMenu, QToolBar,
        QAction, QDoubleSpinBox, QCheckBox, QGridLayout
        )
from PyQt5.QtGui import (
        QIcon, QIntValidator
        )


class NoiserGUI(QMainWindow):
    """
        Implements the main window for a Noisr instance
    """
    def __init__(self, parent=None):
        super(NoiserGUI, self).__init__(parent)
        configs = self.setupEnvironment()
        self.initUI(configs)


    def initUI(self, configs):
        """
            Sets up the layout and user interface
        """
        ## window setup and global attributes
        window = configs['main_window']

        self.setWindowTitle(window['title'])
        self.setWindowIcon(QIcon(window['icon']))
        self.resize(QSize(window['width'], window['height']))

        self.ICON_SIZE = QSize(window['ic_size'], window['ic_size'])
        self.filename = 'instance_name.iad'

        ## create Noisr widgets
        self.log = NoiserGUI.Logger()

        factory.ToolBars(self, configs['env_paths']['toolbars'])
        factory.MenuBar(self, 'path to menu file')
        factory.StatusBar(self, self.filename)

        factory.Noter(self, configs['notes_colors'])
        factory.AnalogPinChoicer(self)
        factory.Scheduler(self)
        factory.Controllers(self)

        self.createAnalyzer()

        ## left board - for data analysis
        containerLeft = QVBoxLayout()
        containerLeft.addStretch()
        containerLeft.addWidget(self.analyzer, alignment = Qt.AlignTop)
        containerLeft.addStretch()
        containerLeft.addWidget(self.log)

        ## right board - for data handling
        containerRight = QVBoxLayout()
        containerRight.addWidget(self.tabNoter)
        containerRight.addWidget(self.groupPinChoice)
        containerRight.addWidget(self.groupSchedule)
        containerRight.addLayout(self.layoutControllers)
        containerRight.addStretch()

        ## main container - disposes boards into two columns
        containerMain = QHBoxLayout()
        containerMain.addLayout(containerLeft)
        containerMain.addLayout(containerRight)

        ## render layout into QWidget
        NoisrWidget = QWidget()
        NoisrWidget.setLayout(containerMain)
        self.setCentralWidget(NoisrWidget)

        self.log.i(_('ENV_OK'))


    class Logger(QPlainTextEdit):
        """
            NoiserGUI.Logger class to communicate with user
        """
        def __init__(self, parent=None):
            super(NoiserGUI.Logger, self).__init__(parent)
            self.setReadOnly(True)


        def i(self, message):   # logs info messages
            logMessage = time.strftime("%H:%M:%S", time.localtime()) + '\t' + message
            self.appendPlainText(logMessage)
        

        def e(self, message, exception):   # logs error messages // TODO red text
            logMessage = time.strftime("%H:%M:%S", time.localtime()) + '\t' + message
            self.appendPlainText(logMessage)

    def onClick(self):
        pass

    def thresholdValidator(self):
        validator = QIntValidator()
        validator.setRange(-25, 25)
        return validator


    def getPorts(self):
        """
            Shows ports whose connection is made with Arduino - LINUX COMPATIBLE
        """
        ports = [f.name for f in os.scandir('/dev') if f.name.startswith('ttyACM')]
        return ports if ports else ['no board']


    def btPlayPauseClicked(self):
        if(self.isReading):
            self.stopReadingData()
            self.btPlayPause.setText('PLAY')
        else:
            self.startReadingData()
            self.btPlayPause.setText('PAUSE')
    
    
    def btPlayPauseOnToggled(self, pushed):
        if pushed:
            self.btPlayPause.setIcon(QIcon('./data/icons/warning.svg'))
        else:
            self.btPlayPause.setIcon(QIcon('./data/icons/target.svg'))
    

    # TODO APPLY TO A TOGGLE
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


    def createAnalyzer(self):
        """
            Generates the display from which data can be analyzed
        """
        ## tab container and style
        self.analyzer = QTabWidget(movable=True, tabPosition=QTabWidget.South)
        self.analyzer.setStyleSheet("QTabWidget::pane { border: 0; }")

        ## plot
        plot = pg.PlotWidget()
        x, y = range(20), [3, 4, 2, 4, 7, 3, 4, 2, 4, 7, 3, 4, 2, 4, 7, 3, 4, 2, 4, 7]
        plot.plot(x, y)
        plot.setAspectLocked(lock=True, ratio=1)

        ## table
        table = QTableWidget(20, 4)
        table.setStyleSheet('background-color: rgb(0, 0, 0);')
        table.horizontalHeader().setStretchLastSection(True)
        table.setHorizontalHeaderLabels(['Time(s)', 'Voltage(V)', 'Moving Average', 'Comment'])
        table.verticalHeader().setVisible(False)

        ## generates tabs compatible with analyzer board
        tabPlot = factory.AnalyzerTab(QHBoxLayout, plot)
        tabTable = factory.AnalyzerTab(QHBoxLayout, table)
  
        self.analyzer.addTab(tabPlot, QIcon('./data/icons/ic_read.svg'), 'Plot')
        self.analyzer.addTab(tabTable, QIcon('./data/icons/ic_sum'), 'Table')


    def startReading(self):
        """
            Change program mode to start reading data
        """
        self.isReading = True
        self.setWindowTitle(self.title + ' (🟢 reading...)')
        
        self.log('Started reading...', 'record')


    def stopReading(self):
        """
            Change program mode to stop reading data
        """
        self.isReading = False
        self.setWindowTitle(self.title)

        self.log('Stopped reading.')


    # TODO missing args from the caller
    def setupEnvironment(self, configsPath='./configs/settings.json'):
        """
            Sets up the global environment according to the configs.json file
        """
        with open(configsPath, 'r') as configsDefault:
            return json.load(configsDefault)