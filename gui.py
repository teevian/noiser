#!/usr/bin/env python

import json, time, os, serial
import pyqtgraph as pg
import factory, connection
import random
import utils

import numpy as np
from collections import deque
from platform import system
from msgid import _, egg
from events import *
from PyQt5.QtCore import (
        QSize, Qt, pyqtSlot, QDateTime, QTimer, QTime
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
        window  = configs['main_window']
        meta    = configs['meta']

        self.setupEnvironment()

        self.name       = meta['name']
        self.filename   = utils.getFunName(meta['extension'], '_')
        self.title_canonical = f"{self.name} {meta['version']} {meta['dev_phase']}"
        self.title      = f'{self.title_canonical} — {self.filename}'

        self.ICON_SIZE  = QSize(window['ic_size'], window['ic_size'])
        self.NO_BOARD   = _('NO_BOARD')
        self.is_reading = False
        self.is_saved   = False
        self.is_signal_stabilized = False
        self.serial_connection = None

        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(window['icon']))
        self.resize(QSize(window['width'], window['height']))

        ## create Noisr widgets
        self.log = NoiserGUI.Logger()
        self.log.i(_('ENV_CREATE'))

        factory.ToolBars(self, configs['env_paths']['toolbars'])
        factory.MenuBar(self, 'path to menu file')
        factory.StatusBar(self, self.filename)
        factory.Noter(self, configs['notes_colors'])

        self.createAnalyzer()
        factory.AnalogPinChoicer(self)
        factory.Scheduler(self)
        factory.Controllers(self)

        self._createMainLayout()

        self.log.i(_('ENV_OK'))

        self.getArduinoPorts()
        self.onConnectButtonClick()


    def setPlotterRange(self):
        """
            Changes scale of the plotter according to max and min values
        """
        self.Yscale_min = self.ids['Yscale_min'].value()
        self.Yscale_max = self.ids['Yscale_max'].value()

        # disallow inverting values
        self.ids['Yscale_min'].setMaximum(self.Yscale_max - 1)
        self.ids['Yscale_max'].setMinimum(self.Yscale_min + 1)

        self.plotter.setYRange(self.Yscale_min, self.Yscale_max, padding=0)


    def onAutoScaleClick(self):
        """
            Changes scale of the plotter according to max and min values
        """
        if self.data_queue:
            voltages_in_queue = self.data_voltages_queue
            min_val, max_val = min(voltages_in_queue), max(voltages_in_queue)

            # sets the min and max according to voltages and gives a padding TODO needs work
            min_val = max(int(min_val), -12)
            max_val = min(int(max_val + 1), 12)

            self.ids['Yscale_min'].setValue(min_val)
            self.ids['Yscale_max'].setValue(max_val)
        else:
            self.log.i(_('PLOT_ERR_AUTOSCALE'))

        self.setPlotterRange()
        self.statusbar.showMessage(_('STATUSBAR_SCALE_CHANGED') + str([self.Yscale_min, self.Yscale_max]), 1000)
    

    def onConnectButtonClick(self, baudrate=9600):
        """
            Opens connection to ackwonledge Arduino
        """
        if self.is_reading:
            self.log.e(_('ERR_THREAD_RUNNING'))
            return

        try:
            port = self.ids['combobox_connected_ports'].currentText()
            if port != self.NO_BOARD:
                with serial.Serial(port, baudrate) as serial_connection:
                    self.serial_connection = serial_connection
                    handshake = connection.handshake(self.serial_connection)
                    self.log.v(_('CON_SERIAL_OK'))
                    self.log.i(_('CON_ARDUINO_SAYS') + handshake)
            else:
                self.log.e(_('CON_ERR_PORTS'))
        except (connection.ConnectionError, serial.serialutil.SerialException) as err:
            self.log.x(err, _('CON_SOL_PORTS'))


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
            Activates (odd clicks) and interrupts (even clicks) receiving the data from arduino
        """
        if not self.is_reading:
            try:
                self.serial_connection = serial.Serial(
                    self.ids['combobox_connected_ports'].currentText(), 9600)
                self.serial_thread = connection.SerialReader(
                    self.serial_connection,
                    self.ids['readRateSpinbox'].value(),
                    self)
                self.serial_thread.data_ready.connect(self.update_plot)

                self.serial_connection.write(b'\x01')

                # wait for acknowledgement from Arduino for 5 seconds (timeoout)
                timeout = time.time() + 5
                while self.serial_connection.read() != b'\x06':
                    if time.time() > timeout:
                        raise connection.ConnectionTimeout(_('CON_ERR_TIMEOUT'))

                pin = self.reading_pin
                self.serial_connection.write(pin.to_bytes(1, byteorder='little', signed=False))

                self.serial_thread.start()
                self.__startReadingSetup()
            except (connection.ConnectionError, serial.SerialException) as err:
                self.log.x(err)
        else:
            # Send command to Arduino to stop sending analog values
            self.serial_connection.write(b'\x04')

            self.serial_thread.terminate()
            self.__stopReadingSetup()
        
        self.is_reading = not self.is_reading   # toggles every time button is clicked


    def __startReadingSetup(self):
        self.log.i(_('READ_START'))

        self.btPlayPause.setText("Stop")
        self.statusbar.setStyleSheet('background-color: rgb(118, 178, 87);')
        self.statusbar.showMessage(_('STATUSBAR_READ_START'), 1000)
        self.setWindowTitle(f'{self.title} (🟢 reading...)')


    def __stopReadingSetup(self):
        self.log.i(_('READ_STOP'))

        self.btPlayPause.setText('Start')
        self.statusbar.setStyleSheet('background-color: rgb(0, 122, 204);')
        self.statusbar.showMessage(_('STATUSBAR_READ_STOP'), 1000)
        self.setWindowTitle(self.title)

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
 
    def closeEvent(self, event):
        """
            Disallows the window to be closed while Serial thread is running
        """
        #self.serial_reader.stop()
        #self.serial_reader.wait()
        if not self.is_reading:
            event.accept()
        else:
            self.log.e(_('ERR_THREAD_RUNNING'))
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
        factory.boardInfoDialog()
    

    def onBoardCodeClick(self):
        factory.boardCodeDialog('./noiserino/noiserino.ino')


    def thresholdValidator(self):
        validator = QIntValidator()
        validator.setRange(-25, 25)
        return validator


    def btPlayPauseOnToggled(self, pushed):
        if pushed:
            self.btPlayPause.setIcon(QIcon('./data/icons/warning.svg'))
        else:
            self.btPlayPause.setIcon(QIcon('./data/icons/target.svg'))


    def onAnalogPinChanged(self):
        """
            Sets up environment when the user chooses another analog pin to read from
        """
        self.reading_pin = self.groupbox.checkedId()
        self.plotter.setTitle(f'Data from PIN A{self.reading_pin}')
        self.statusbar.showMessage(_('STATUSBAR_PIN_CHANGED') + str(self.reading_pin), 1000)


    def createAnalyzer(self):
        """
            Generates the display from which data can be analyzed
        """
        ## tab container and style
        self.analyzer = QTabWidget(movable=True, tabPosition=QTabWidget.South)
        self.analyzer.setStyleSheet("QTabWidget::pane { border: 0; }")

        ## plotter
        self.plotter = pg.PlotWidget(useOpenGL=True)
        self.plotter.setLabel('left', 'Voltage', units='V', size='18pt')
        self.plotter.setLabel('bottom', 'Time', units='s', size='18pt')
        self.plotter.showGrid(x=True, y=True, alpha=0.7)
        self.plotter.setLimits(xMin = 0, yMin = -12, yMax = 12)
        #self.plotter.setAspectLocked(lock=True, ratio=1)
        self.plotter.setMouseEnabled(x=True,y=False) 

        vb = self.plotter.getViewBox()                     
        vb.setAspectLocked(lock=False)            
        vb.setAutoVisible(y=1.0)                
        vb.enableAutoRange(axis='y', enable=True)

        self.setPlotterRange()
        self.setStabilizationDeviation()

        # TODO CONSIDERATIONS for 'essential mode
        #self.plotter.setDownsampling(auto=True)

        deque_len = 50
        self.data_queue = deque(maxlen=deque_len)
        self.data_voltages_queue = deque(maxlen=deque_len)   # optimizing for speed

        self.time = np.zeros(deque_len)
        self.voltage = np.zeros(deque_len)

        # Plot the initial data
        self.signal_plot = self.plotter.plot(self.time, self.voltage, pen='g', width=5, name='Voltage')
        self.threshold_line = pg.InfiniteLine(
            angle=0, movable=True, # TODO enable user to move the threshold - sync with qdoublespinbox
            pen=pg.mkPen(color='r',
            width=3,
            style=Qt.DashLine))
        self.threshold_line.sigDragged.connect(self.updateThresholdSpinBox)

        self.threshold_line.setPos(float(self.ids['threshold_reference'].value()))
        self.plotter.addItem(self.threshold_line)

        ## table
        table = QTableWidget(20, 4)
        table.setStyleSheet('background-color: rgb(0, 0, 0);')
        table.horizontalHeader().setStretchLastSection(True)
        table.setHorizontalHeaderLabels(['Time', 'Voltage', 'Moving Average', 'Comment'])
        table.verticalHeader().setVisible(False)

        ## generates tabs compatible with analyzer board
        tabPlot = factory.AnalyzerTab(QHBoxLayout, self.plotter)
        tabTable = factory.AnalyzerTab(QHBoxLayout, table)
  
        self.analyzer.addTab(tabPlot, QIcon('./data/icons/ic_read.svg'), 'Oscilloscope')
        self.analyzer.addTab(tabTable, QIcon('./data/icons/ic_sum'), 'Spreadsheet')


    def update_plot(self, new_voltage):
        """
            Updates the plot with data
        """
        new_time = self.time[-1] + (1 / self.serial_thread.rate)

        self.data_queue.append((new_time, new_voltage))
        self.data_voltages_queue.append(new_voltage)

        #print(str(self.time) + ' > ' + str(self.voltage))
        self.time, self.voltage = zip(*self.data_queue)

        if self.checkStabilization() != self.is_signal_stabilized:
            self.toggleStabilization()
    
        self.signal_plot.setData(self.time, self.voltage)
        self.plotter.setYRange(self.Yscale_min, self.Yscale_max, padding=0)
        self.plotter.setXRange(self.time[-20], self.time[-1], padding=0)
        #self.label.setPos(self.x_data[-1], 1)
        #self.label.setText(f"Y = {self.y_data[-1]:.2f}")


    def updateThresholdSpinBox(self):
        """
            Updates the threshold value if the threshold is manually moved
        """
        new_threshold = self.threshold_line.value()
        self.ids['threshold_reference'].setValue(new_threshold)


    def updateThresholdLine(self, new_threshold):
        """
            Updates the threshold line in our friend plotter
        """
        self.threshold_line.setPos(new_threshold)
        self.threshold_reference = new_threshold


    def toggleStabilization(self):
        """
            Updates the GUI and the curve according to stabilization change
        """
        if self.is_signal_stabilized:
            self.signal_plot.setPen(pg.mkPen(color=(0, 122, 204), width=4))
            self.log.i(_('SIGNAL_NOT_STABILIZED') + ' since ' + str(self.data_queue[0]))
        else:
            self.signal_plot.setPen(pg.mkPen(color=(118, 178, 87),  width=4))
            self.log.i(_('SIGNAL_STABILIZED') + ' since ' + str(self.data_queue[0]))
        self.is_signal_stabilized = not self.is_signal_stabilized


    def setThreshold(self):
        """
            Changes the threshold
        """
        self.threshold_reference = self.ids['threshold_reference'].value()


    def checkStabilization(self):
        """
            Checks if the signal is stabilized
        """
        voltages_std_dev = np.std(self.data_voltages_queue)
        return voltages_std_dev < self.stabilization_deviation


    def setStabilizationDeviation(self):
        """
            Updates the stabilization value
        """
        self.stabilization_deviation = self.ids['stabilization_deviation'].value()
        print(self.stabilization_deviation)


    def setReadRate(self, rate):
        """
            Changes the read rate from arduino
        """
        if self.is_reading:
            self.serial_thread.rate = rate


    ############################
    # Utility Methods
    ############################
    def doNothing(self):
        """
            That's right: this function does nothing :)
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