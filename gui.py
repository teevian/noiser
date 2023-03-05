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

"""
Class for the main window
"""
class NoiserWindow(QMainWindow):
    def __init__(self, parent = None):
        super(NoiserWindow, self).__init__(parent)
        self.setupGlobalVariables()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.resize(QSize(1000, 800))

        self._createMenuBar()
        self._createToolBars()
        self._createStatusBar()

        self.createPlotAnalyzer()
        self.createTableDataAnalyzer()
        self.createGroupAnalogPinChoice()
        self.createGroupControllers()

        # plotter
        layoutLeftContainer = QVBoxLayout()
        layoutLeftContainer.addWidget(self.tabPlotter, alignment=Qt.AlignTop)
        layoutLeftContainer.addStretch()

        # logger
        self.logger = QPlainTextEdit()
        self.logger.setReadOnly(True)
        self.logger.setFixedHeight(self.logger.fontMetrics().lineSpacing() * 12)
        layoutLeftContainer.addWidget(self.logger)

        # note taking block - misses ADD and CLEAR note
        self.note = QTextEdit()
        self.note.setUndoRedoEnabled(False)
        self.note.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.note.setFixedHeight(80)
        self.note.setFixedWidth(235) # TODO automate this
        self.note.insertPlainText('note #1 \n')

        layoutRightContainer = QVBoxLayout()
        layoutRightContainer.addWidget(self.note)
        layoutRightContainer.addWidget(self.groupPinChoice)
        layoutRightContainer.addWidget(self.groupControllers)
        
        layout = QHBoxLayout()
        layout.addWidget(self.btPlayPause)

        layoutRightContainer.addLayout(layout)
        layoutRightContainer.addStretch()

        # main container that disposes the widgets into two columns
        layoutMainContainer = QHBoxLayout()
        layoutMainContainer.addLayout(layoutLeftContainer)
        layoutMainContainer.addLayout(layoutRightContainer)

        container = QWidget()
        container.setLayout(layoutMainContainer)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setCentralWidget(container)

    # TODO
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("File", self)
        menuBar.addMenu(fileMenu)
        # Creating menus using a title
        helpMenu = menuBar.addMenu("Help")

    # TODO improve this programatically
    def _createToolBars(self):
        self._toolBarInstance()
        self._toolbarConnection()
        self._toolbarWorkspace()

    def _toolBarInstance(self):
        # Toolbar instance
        # handles instance and file (new, save, load, delete)
        toolbarFile = QToolBar('Instance management toolbar')
        toolbarFile.setIconSize(QSize(24, 24))
        toolbarFile.setMovable(False)
        self.addToolBar(toolbarFile)

        # new instance
        btNewInstance = QAction(QIcon('./data/res/new.svg'), 'New', self)
        btNewInstance.setStatusTip('Creates new .IAD instance')
        #btNewInstance.setCheckable(True)
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
        # Toolbar connection settings
        # handles connection settings with arduino
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
        self.btPlayPause.setIconSize(QSize(48, 48))
        self.btPlayPause.setCheckable(True)
        self.btPlayPause.toggled.connect(self.btPlayPauseOnToggled)

        self.groupControllers.setLayout(layoutVContainer)

    def createTableDataAnalyzer(self):

        self.table = QWidget()
        tableWidget = QTableWidget(5, 2)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)

        self.table.setLayout(tab1hbox)

    def createPlotAnalyzer(self):
        self.tabPlotter = QTabWidget()
        self.tabPlotter.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        
        tabSimple = QWidget()

        # simple graph
        plotSimple = pg.PlotWidget()
        plotSimple.plot(range(0, 20), [3, 4, 2, 4, 7, 3, 4, 2, 4, 7, 3, 4, 2, 4, 7, 3, 4, 2, 4, 7])
        plotSimple.setAspectLocked(lock=True, ratio=1)

        tabPlotContainer = QVBoxLayout()
        tabPlotContainer.setContentsMargins(5, 5, 5, 5)
        tabPlotContainer.addWidget(plotSimple)

        plotOptionsContainer = QHBoxLayout()
        plotOptionsContainer.addWidget(QLabel('moving average: '))
        plotOptionsContainer.addWidget(QCheckBox())
        plotOptionsContainer.addStretch()

        tabPlotContainer.addLayout(plotOptionsContainer)
        tabSimple.setLayout(tabPlotContainer)

        # table data
        tabTable = QWidget()
        tableWidget = QTableWidget(5, 4)
        tableWidget.setHorizontalHeaderLabels(['Time(s)', 'Voltage(V)', 'Moving Average', 'PWM', ''])
        tableWidget.horizontalHeader().setStretchLastSection(True)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)

        tabTable.setLayout(tab1hbox)

        self.tabPlotter.addTab(tabSimple, "Plot")
        self.tabPlotter.addTab(tabTable, "Table")

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
        self.isReading = configs['settings']['startup_reading']
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