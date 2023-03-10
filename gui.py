#!/usr/bin/env python

import json, time, os
import pyqtgraph as pg
import factory, connection

from platform import system
from msgid import _, egg
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
        QAction, QDoubleSpinBox, QCheckBox, QGridLayout, QTextEdit
        )
from PyQt5.QtGui import (
        QIcon, QIntValidator, QColor
        )


class NoiserGUI(QMainWindow):
    """
        Implements the main window for a Noisr instance
    """
    def __init__(self, parent=None):
        super(NoiserGUI, self).__init__(parent)
        self.initUI(self.loadConfigs())


    def initUI(self, configs):
        """
            Sets up the layout and user interface
        """
        ## window setup
        window = configs['main_window']

        self.setupEnvironment()

        self.ICON_SIZE = QSize(window['ic_size'], window['ic_size'])
        self.filename = 'instance_name.IAD'

        self.setWindowTitle(window['title']) # TODO + version
        self.setWindowIcon(QIcon(window['icon']))
        self.resize(QSize(window['width'], window['height']))

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
        self._createMainLayout()

        self.log.i(_('ENV_OK'))

        # TODO auto-start connection // improve code (redundant calls)
        self.serial_connection = None
        arduino_port = self.ids['comboboxConnectedPorts'].currentText()
        self.openConnection(arduino_port)
        self.serial_thread = connection.SerialReader(
            arduino_port, self.ids['readRateSpinbox'].value(), self)
        self.is_reading = False
        self.serial_thread.data_ready.connect(self.update)


    def openConnection(self, port):
        """
            Opens connection with Arduino
        """
        try:
            self.serial_connection = connection.openConnection(port)
            handshake = connection.handshake(self.serial_connection)
            self.log.v(_('CON_SERIAL_OK'))
            self.log.i(_('CON_ARDUINO_SAYS') + handshake)
        except Exception as err:
            self.log.e(_('CON_SERIAL_ERR'), err)
            print(err)


    class Logger(QTextEdit):
        """
            NoiserGUI.Logger class to communicate with user
        """
        def __init__(self, parent=None):
            super(NoiserGUI.Logger, self).__init__(parent)
            self.setReadOnly(True)

            self.error    = '<span style="color:#c0392b;">{}</span>'
            self.warning  = '<span style="color:orange;">{}</span>'
            self.valid    = '<span style="color:green;">{}</span>'


        def i(self, message):   # logs info messages
            logMessage = time.strftime("%H:%M:%S", time.localtime()) + ' ' + message
            self.append(logMessage)

        def v(self, message):
            logMessage = time.strftime("%H:%M:%S", time.localtime()) + ' ' + message
            self.append(self.valid.format(logMessage))

        def e(self, message, err):
            logMessage = time.strftime("%H:%M:%S", time.localtime()) + ' ' + str(err) + ': ' + message
            self.append(self.error.format(logMessage))

    def update(self, value):
        print(value)

    def _createMainLayout(self):
        """
            Creates the layout for the application
        """
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


    def onClick(self):
        pass

    def onConnectButtonClick(self):
        """
            Handshakes Arduino
        """
        self.log.i(_('CON_NEW'))
        self.log.i(_('CON_CHECKING_PORTS'))
        self.getPorts()
        self.openConnection()

    def onReadStopButtonClick(self):
        print("test")
        if not self.is_reading:
            connection.startReadingPin(self, self.serial_thread.serial_connection, 0)
        else:
            connection.stopReadingPin(self, self.serial_thread.serial_connection, 0)
 
    def onRead2StopButtonClick(self):
        if not self.is_reading:
            self.stopReadingData()
            self.btPlayPause.setText('PLAY')
        else:
            self.startReadingData()
            self.btPlayPause.setText('PAUSE')


    def readPin(self, pin):
        pass#connect.listenToPin(self.serialConnection, 0, 1)

    def getPorts(self):
        """
            Checks for ports with connected boards
        """
        ports = ['no board']
        try:
            ports = connection.getPorts(self.system)
            self.log.v(_('CON_ARDUINO_OK') + str(ports))
        except Exception as err:
            self.log.e(_('CON_ARDUINO_ERR'), err)
            print(err)
        finally:
            return ports


    def thresholdValidator(self):
        validator = QIntValidator()
        validator.setRange(-25, 25)
        return validator

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
        if self.isReading :
            self.stopReadingData()
            self.btScheduledRead.setText('SCHEDULE')
        else:
            self.startReadingData()
            self.btScheduledRead.setText('READING')

    def setReadRate(self):
        #self.serial_thread.rate = rate
        pass

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

    ## TODO IMPROVE THIS
    def setupEnvironment(self, path='./configs/toolbars.json'):
        """
            Sets up global attributes for the window
        """
        self.system = system()
        self.ids = {}
        with open(path, 'r') as ids:
            env = json.load(ids)
            for key in env:
                for item in env[key]['actions']:
                    if '@id' in item:
                        self.ids[item['@id']] = ''


    # TODO missing args from the caller
    def loadConfigs(self, configsPath='./configs/settings.json'):
        """
            Sets up the global environment according to the configs.json file
        """
        with open(configsPath, 'r') as configsDefault:
            return json.load(configsDefault)