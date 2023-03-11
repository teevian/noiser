#!/usr/bin/env python

import json, time, os, serial
import pyqtgraph as pg
import factory, connection

from platform import system
from msgid import _, egg
from events import *
from PyQt5.QtCore import (
        QSize, Qt, pyqtSlot, QDateTime
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

######################################################################
# PyQt window for a Noisr instance
######################################################################         

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
        self.is_reading = False

        self.setWindowTitle(window['title']) # TODO + version
        self.setWindowIcon(QIcon(window['icon']))
        self.resize(QSize(window['width'], window['height']))

        ## create Noisr widgets
        self.log = NoiserGUI.Logger()
        self.log.i(_('ENV_CREATE'))

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
  
        self.openConnection()
 
    # handshake
    def openConnection(self, baudrate=9600):
        """
            Opens connection w/ current selected port
        """
        try:    # https://superfastpython.com/thread-context-manager/
            # the 'with' ensures that the connection is closed
            with serial.Serial(self.ids['combobox_connected_ports'].currentText(), baudrate) as serial_connection:
                #print("got here!")
                self.serial_connection = serial_connection
                #self.serial_thread = connection.SerialReader(
                #    self.serial_connection,
                #    self.ids['readRateSpinbox'].value(),
                #    self)
                #self.serial_thread.data_ready.connect(self.update)
                #print("FIRST: " + str(self.serial_connection))
                handshake = connection.handshake(self.serial_connection)
                self.log.v(_('CON_SERIAL_OK'))
                self.log.i(_('CON_ARDUINO_SAYS') + handshake)
        except connection.ConnectionError as err:
            self.log.x(err, _('CON_SOL_SERIAL'))
        print("SECOND: " + str(self.serial_connection))


    def syncArduinoPorts(self):
        """
            Syncs the combobox for ports for new ports
        """
        self.ids['combobox_connected_ports'].clear()
        self.ids['combobox_connected_ports'].addItems(self.getArduinoPorts())


    def getArduinoPorts(self):
        """
            Sets up the combobox with ports connected with Arduino.
        """
        self.log.i(_('CON_PORTS'))
        try:
            ports = connection.getPorts(self.system)
            self.log.v(_('CON_OK_PORTS') + str(ports))
        except connection.PortError as err:
            self.log.x(err, _('CON_SOL_PORTS'))
            return [_('NO_BOARD')]
        return ports


    def onReadStopButtonClick(self):
        """
            Button: activates (odd clicks) and interrupts (even clicks) receiving the data from arduino
        """
        if not self.is_reading:
            try:
                self.serial_connection = serial.Serial(
                    self.ids['combobox_connected_ports'].currentText(),
                    9600)
                self.serial_thread = connection.SerialReader(
                    self.serial_connection,
                    self.ids['readRateSpinbox'].value(),
                    self)
                self.serial_thread.data_ready.connect(self.update)

                self.serial_connection.write(b'\x01')

                # wait for acknowledgement from Arduino for 5 seconds (timeoout)
                timeout = time.time() + 5
                while self.serial_connection.read() != b'\x06':
                    if time.time() > timeout:
                        raise connection.ConnectionTimeout(_('CON_ERR_TIMEOUT'))

                # pin to read from
                pin = 1
                self.serial_connection.write(pin.to_bytes(pin, byteorder='little', signed=False))

                self.is_reading = True
                self.btPlayPause.setText("Stop")
                self.serial_thread.start()
            except connection.ConnectionError as err:
                self.log.x(err)

        else:
            # Send command to Arduino to stop sending analog values
            self.serial_connection.write(b'\x04')

            self.btPlayPause.setText("Start")
            self.is_reading = False
            self.serial_thread.terminate() # Stop the serial reader thread


    def setReadRate(self, rate):
        self.serial_thread.rate = rate


    def set_read_rate(self, rate):
        self.serial_thread.rate = rate


    ############################
    # Inner classes
    ############################
    class Logger(QTextEdit):
        """
            Class to handle communication w/ user through the Logger
        """
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setReadOnly(True)

            self.formats = {
                'info': '{}',
                'error': '<span style="color:#c0392b;">{}</span>',
                'warning': '<span style="color:orange;">{}</span>',
                'valid': '<span style="color:green;">{}</span>'
            }

        def _log(self, message, level='info'):
            """
                Logs message of the given level
            """
            formatted_message = self.formats[level].format(message)
            log_message = QDateTime.currentDateTime().toString('[hh:mm:ss] ') + formatted_message
            self.append(log_message)

        def i(self, message):
            """
                Logs info messages
            """
            self._log(message)

        def v(self, message):
            """
                Logs validation and confirmation messages
            """
            self._log(message, 'valid')

        def e(self, message):
            """
                Logs error messages (no need to be exception)
            """
            self._log(message, 'error')

        def x(self, err, solution=''):
            """
                Logs Exceptions messages and preferably provides a solution
            """
            message = type(err).__name__ + ': ' + str(err)
            self._log(message, 'error')
            if solution:
                self.i(solution)
    

    ############################
    # Event handling methods
    ############################
    def update(self, value):
        """
            Updates the user interface on iterations of the Serial thread
        """
        print(value)
    
    def closeEvent(self, event):
        """
            Disallows the window to be closed while Serial thread is running
        """
        if self.is_reading == False:
            event.accept()
        else:
            self.log.e("Stop the Thread first! You wouldn't want to explode your expensive Raspberry PI")
            event.ignore()

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

    def onBoardInfoClick(self):
        factory.boardInfo()
    
    def onBoardCodeClick(self):
        factory.boardCode('./noiserino/noiserino.ino')

    def onClick(self):
        pass

    def onConnectButtonClick(self):
        """
            Handshakes Arduino
        """
        self.log.i(_('CON_NEW'))
        self.log.i(_('CON_CHECKING_PORTS'))
        self.getArduinoPorts()
        self.openConnection()

    def readPin(self, pin):
        pass#connect.listenToPin(self.serialConnection, 0, 1)

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

    ############################
    # Utility Methods
    ############################
    def doNothing(self):
        """
            That's right: this function does nothing.
        """
        pass


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