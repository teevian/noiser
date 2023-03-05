#!/usr/bin/env python

import json, time, os
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
        QLineEdit, QPlainTextEdit, QMenuBar, QMenu, QToolBar,
        QAction, QDoubleSpinBox, QCheckBox, QGridLayout
        )
from PyQt5.QtGui import (
        QIcon, QIntValidator
        )

class NoiserWindow(QMainWindow):
    """Class for handling a GUI instance"""

    def __init__(self, parent = None):
        super(NoiserWindow, self).__init__(parent)
        self.setupEnvironment()
        self.initUI()

    def initUI(self):
        """Sets up the graphical user interface"""

        self.setWindowTitle(self.configs['main_window']['title'])
        self.setWindowIcon(QIcon('./data/icons/avicon.svg'))
        self.resize(QSize(
            self.configs['main_window']['dimen_width'],
            self.configs['main_window']['dimen_height'])
            )

        # create basic interface
        self._createMenuBar()
        self._createToolBars()
        self._createStatusBar()

        self.createAnalyzer()
        self.createGroupAnalogPinChoice()
        self.createGroupControllers()

        # plotter
        layoutLeftContainer = QVBoxLayout()
        layoutLeftContainer.addWidget(self.tabPlotter, alignment = Qt.AlignTop)
        layoutLeftContainer.addStretch()

        # logger
        self.logger = QPlainTextEdit()
        self.logger.setReadOnly(True)
        #self.logger.setFixedHeight(self.logger.fontMetrics().lineSpacing() * 8)
        layoutLeftContainer.addWidget(self.logger)

        # note taking block - misses ADD and CLEAR note
        self.note = QTextEdit()
        self.note.setUndoRedoEnabled(False)
        self.note.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.note.setFixedHeight(self.note.fontMetrics().lineSpacing() * 4)
        self.note.setFixedWidth(235) # TODO automate this to become the minimum
        self.note.insertPlainText('note #1 \n')

        layoutRightContainer = QVBoxLayout()
        layoutRightContainer.addWidget(self.note)
        layoutRightContainer.addWidget(self.groupPinChoice)
        layoutRightContainer.addWidget(self.groupControllers)
        
        layout = QHBoxLayout()
        layout.addWidget(self.btPlayPause)
        layout.addWidget(self.btRegister)

        layoutRightContainer.addLayout(layout)
        layoutRightContainer.addStretch()

        # main container that disposes the widgets into two columns
        layoutMainContainer = QHBoxLayout()
        layoutMainContainer.addLayout(layoutLeftContainer)
        layoutMainContainer.addLayout(layoutRightContainer)

        container = QWidget()
        container.setLayout(layoutMainContainer)
        self.setCentralWidget(container)

    # TODO
    def _createMenuBar(self):
        pass

    # TODO improve this programatically
    def _createToolBars(self):
        self._toolBarInstance()
        self._toolbarConnection()
        self._toolbarWorkspace()
        self._toolbarParameters()
        self._toolbarNumerics()

    def _toolBarInstance(self):
        # Toolbar instance
        #toolbarTest = QToolBar('')

        toolbarFile = QToolBar('Instance management toolbar')
        toolbarFile.setIconSize(QSize(24, 24))
        toolbarFile.setMovable(False)
        self.addToolBar(toolbarFile)

        # new instance
        btNewInstance = QAction(QIcon('./data/res/new.svg'), 'New', self)
        btNewInstance.setStatusTip('Creates new .IAD instance')
        toolbarFile.addAction(btNewInstance)

        # save instance
        btSaveInstance = QAction(QIcon('./data/res/instance_save.svg'), 'Save', self)
        btSaveInstance.setStatusTip("Saves current instance to a .IAD file")
        toolbarFile.addAction(btSaveInstance)

        # load instance
        btLoadInstance = QAction(QIcon('./data/res/instance_load.svg'), 'Load', self)
        btLoadInstance.setStatusTip("Loads new instance from a .IAD file")
        #button_action.triggered.connect(self.onMyToolBarButtonClick)
        toolbarFile.addAction(btLoadInstance)

        toolbarFile.addSeparator()

        # load instance
        btSaveDataCSV = QAction(QIcon('./data/res/save_data_csv.svg'), 'Save data CSV', self)
        btSaveDataCSV.setStatusTip("Saves data into a .csv file")
        toolbarFile.addAction(btSaveDataCSV)

        # load instance
        btSaveDataTXT = QAction(QIcon('./data/res/save_data_txt.svg'), 'Save data TXT', self)
        btSaveDataTXT.setStatusTip("Saves data into a .txt file")
        toolbarFile.addAction(btSaveDataTXT)

    def _toolbarConnection(self):
        """Settings about connection with the board"""
        
        toolbarConnectionSettings = QToolBar('Connection settings with Arduino')
        toolbarConnectionSettings.setIconSize(QSize(24, 24))
        self.addToolBar(toolbarConnectionSettings)

        # info board instance
        btInfoBoard = QAction(QIcon('./data/res/info_board.svg'), 'Info board', self)
        btInfoBoard.setStatusTip("Provides info about the connected board")
        toolbarConnectionSettings.addAction(btInfoBoard)        

        # list comprehension to extract all files starting with "ttyACM" at /dev
        ports = [f.name for f in os.scandir('/dev') if f.name.startswith('ttyACM')]
        comboBoxPorts = QComboBox()
        comboBoxPorts.addItems(ports if ports else ['no board'])
        toolbarConnectionSettings.addWidget(comboBoxPorts)

        toolbarConnectionSettings.addWidget(QLabel('rate:'))
        toolbarConnectionSettings.addWidget(QSpinBox())


    def _toolbarWorkspace(self):
        toolbarWorkspace = QToolBar('Workstation objects')
        toolbarWorkspace.setIconSize(QSize(24, 24))
        self.addToolBar(toolbarWorkspace)

        # info board instance
        btInfoBoard = QAction(QIcon('./data/res/notes.svg'), 'Notes taken for this instance', self)
        btInfoBoard.setStatusTip('All notes taken at this .IAD instance')
        toolbarWorkspace.addAction(btInfoBoard)

    def _toolbarParameters(self):
        """Parameters for working plot and data analysis"""

        toolbarParameters = QToolBar('Parameters for data analyzer')
        toolbarParameters.setIconSize(QSize(24, 24))
        self.addToolBar(toolbarParameters)

        self.insertToolBarBreak(toolbarParameters)

        self.editThreshold = QLineEdit()
        self.editThreshold.setFixedWidth(50)
        #self.editThreshold.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        validateThreshold = QIntValidator()
        validateThreshold.setRange(-25, 25)
        self.editThreshold.setValidator(validateThreshold)
        
        comboThresholdUnits = QComboBox()
        comboThresholdUnits.addItems(('V', 'mV'))

        toolbarParameters.addWidget(QLabel('threshold:'))
        toolbarParameters.addWidget(self.editThreshold)
        toolbarParameters.addWidget(comboThresholdUnits)


    def _toolbarNumerics(self):
        """Numerical computations to real-time data analysis"""

        toolbar = QToolBar('Numeric Methods')
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setFloatable(True)
        toolbar.setMovable(True)
        toolbar.setOrientation(Qt.Vertical)

        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        btMovingAverage = QAction(QIcon('./data/res/plot_mean.svg'), 'Notes taken for this instance', self)
        btMaxMinVoltage = QAction(QIcon('./data/res/plot_peaktopeak.svg'), 'Notes taken for this instance', self)
        btStdDeviation  = QAction(QIcon('./data/res/plot_measures.svg'), 'Notes taken for this instance', self)
        btThreshold     = QAction(QIcon('./data/res/plot_tolerance.svg'), 'Notes taken for this instance', self)

        btMovingAverage.setStatusTip('Moving average')
        btMaxMinVoltage.setStatusTip('Maximum and minimum')
        btStdDeviation.setStatusTip('Standard Deviation')
        btThreshold.setStatusTip('Threshold voltage')

        toolbar.addAction(btMovingAverage)
        toolbar.addAction(btMaxMinVoltage)
        toolbar.addAction(btStdDeviation)
        toolbar.addAction(btThreshold)


    def _createStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("background-color: rgb(0, 122, 204);")
        self.statusbar.showMessage("Arduino Connected!", 3000)

        self.labelFilename = QLabel('instance_name.iad')
        self.statusbar.addPermanentWidget(self.labelFilename)


    def btPlayPauseClicked(self):
        if(self.isReading):
            self.stopReadingData()
            self.btPlayPause.setText('PLAY')
        else:
            self.startReadingData()
            self.btPlayPause.setText('PAUSE')
    
    
    def btPlayPauseOnToggled(self, pushed):
        if pushed:
            self.btPlayPause.setIcon(QIcon('./data/res/warning.svg'))
        else:
            self.btPlayPause.setIcon(QIcon('./data/res/target.svg'))
    

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


    """
        Creates the group for radio pins
    """
    def createGroupAnalogPinChoice(self):
        layoutGridPins = QGridLayout()
        self.groupPinChoice = QGroupBox('Analog PIN')

        self.analogPin = []
        for i in range(6):
            row, col = i // 3, i % 3    # organizes in a 2x3 grid
            btRadio = QRadioButton(f'A{i}')
            layoutGridPins.addWidget(btRadio, row, col)
            self.analogPin.append(btRadio)

        self.analogPin[0].setChecked(True)
        self.groupPinChoice.setLayout(layoutGridPins)


    def createGroupControllers(self):
        # time box (parses input)
        editTime = QLineEdit()
        editTime.setFixedWidth(50)
        validateTime = QIntValidator()
        validateTime.setBottom(0)
        editTime.setValidator(validateTime)
        
        comboTimeUnits = QComboBox()
        comboTimeUnits.addItems(('s', 'ms'))

        layoutHTime = QHBoxLayout()
        layoutHTime.addWidget(QLabel('Time:'))
        layoutHTime.addWidget(editTime)
        layoutHTime.addWidget(comboTimeUnits)

        # stars at box
        comboStartAt = QComboBox()
        comboStartAt.addItems(('right away', 'when stabilized'))

        layoutHStartAt = QHBoxLayout()
        layoutHStartAt.addWidget(QLabel('Starting:'))
        layoutHStartAt.addWidget(comboStartAt)

        layoutVContainer = QVBoxLayout()
        layoutVContainer.addLayout(layoutHTime)
        layoutVContainer.addLayout(layoutHStartAt)

        layoutVContainer.addStretch()

        self.groupControllers = QGroupBox('Schedule')
        self.groupControllers.setCheckable(True)
        self.groupControllers.setChecked(False)
        self.groupControllers.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btPlayPause = QPushButton(QIcon('./data/res/target.svg'), '')
        self.btPlayPause.setIconSize(QSize(24, 24))
        self.btPlayPause.setCheckable(True)
        self.btPlayPause.toggled.connect(self.btPlayPauseOnToggled)

        self.btRegister = QPushButton(QIcon('./data/res/save_data.svg'), '')
        self.btRegister.setIconSize(QSize(24, 24))
        self.btRegister.setCheckable(True)
        self.btRegister.toggled.connect(self.btPlayPauseOnToggled)

        self.groupControllers.setLayout(layoutVContainer)


    def createAnalyzer(self):
        """Generates the Tab screen from which the user will analyze data"""

        self.tabPlotter = QTabWidget()
        self.tabPlotter.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
            )

        # plot
        plot = pg.PlotWidget()
        plot.plot(range(0, 20), [3, 4, 2, 4, 7, 3, 4, 2, 4, 7, 3, 4, 2, 4, 7, 3, 4, 2, 4, 7])
        plot.setAspectLocked(lock=True, ratio=1)

        ## plot numerical analysis options
        tabPlotContainer = QVBoxLayout()
        tabPlotContainer.setContentsMargins(5, 5, 5, 5)
        tabPlotContainer.addWidget(plot)

        # table
        tabTable = QWidget()
        tableWidget = QTableWidget(5, 4)
        tableWidget.setHorizontalHeaderLabels(['Time(s)', 'Voltage(V)', 'Moving Average', 'PWM', ''])
        tableWidget.horizontalHeader().setStretchLastSection(True)

        tab1hbox = QHBoxLayout()
        #tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)

        tabTable.setLayout(tab1hbox)

        tabSimple = QWidget()
        tabSimple.setLayout(tabPlotContainer)

        self.tabPlotter.addTab(tabSimple, "Plot")
        self.tabPlotter.addTab(tabTable, "Table")

    def startReadingData(self):
        """Change program mode to start reading data"""
        self.isReading = True
        self.setWindowTitle(self.title + ' (🟢 reading...)')
        
        self.log('Started reading...', 'record')
        
    def stopReadingData(self):
        """Change program mode to stop reading data"""

        self.isReading = False
        self.setWindowTitle(self.title)

        self.log('Stopped reading.', 'stop')


    def log(self, message, type='info'):
        """Writes the string @message to the logger - sometimes with an emoji"""

        logMessage = time.strftime("%H:%M:%S", time.localtime()) + '\t' + message + '\t' + self.emoji_dict[type]
        self.logger.appendPlainText(logMessage)

    # TODO missing args from the caller
    def setupEnvironment(self, configsPath='./configs/settings.json'):
        """Sets up the global environment according to the .configs.json file"""

        with open(configsPath, 'r') as file_configs:
            self.configs = json.load(file_configs)