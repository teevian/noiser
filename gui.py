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
            self.configs['main_window']['dimen_height']))

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

        self.log('Everything is ready to go!')


    # TODO
    def _createMenuBar(self):
        pass


    def _createToolBars(self, path = './configs/toolbars.json'):
        """Creates the toolbars in a smart way"""

        with open(path, 'r') as toolbarsFile:
            toolbars = json.load(toolbarsFile)
            for toolbarName in toolbars:
                self._createToolbar(toolbars[toolbarName])


    def _createToolbar(self, toolbar):
        """Wizard code to deal with toolbars simplier - new way of doing!"""

        toolbarInstance = QToolBar('test name')
        toolbarInstance.setIconSize(QSize(
            self.configs['toolbars']['icon_size'],
            self.configs['toolbars']['icon_size'])
            )

        toolWidgets = toolbar['actions']
        settings = toolbar['settings']

        # TODO create util function from this
        movable     = settings.get('movable', 'True').lower() == 'true'
        floatable   = settings.get('floatable', 'True').lower() == 'true'
        position    = settings.get('position', 'top')

        TOOLBAR_AREAS = {
            'top' : Qt.TopToolBarArea,
            'left' : Qt.LeftToolBarArea,
            'bottom' : Qt.LeftToolBarArea,
            'right' : Qt.RightToolBarArea
            }
        position = settings.get('position', 'top')

        toolbarInstance.setMovable(movable)
        toolbarInstance.setFloatable(floatable)
        self.addToolBar(TOOLBAR_AREAS[position], toolbarInstance)

        # TODO create an exception
        for action in toolWidgets:
            if action['type'] == 'button':
                btAction = QAction(QIcon(action['icon']), action['name'], self)
                btAction.setStatusTip(action['status'])
                btAction.triggered.connect(getattr(self, action['action']))
                toolbarInstance.addAction(btAction)
            elif action['type'] == 'separator':
                toolbarInstance.addSeparator()
            elif action['type'] == 'label':
                toolbarInstance.addWidget(QLabel(action['text']))
            elif action['type'] == 'combobox':
                comboBoxPorts = QComboBox()
                itemsFunction = getattr(self, action['action'])
                items = itemsFunction()
                comboBoxPorts.addItems(items)
                toolbarInstance.addWidget(comboBoxPorts)
            elif action['type'] == 'spinbox':
                toolbarInstance.addWidget(QSpinBox())
            elif action['type'] == 'lineEdit':
                editLine = QLineEdit()
                editLine.setFixedWidth(int(action['width']))
                editValidator = getattr(self, action['validator']) # TODO validator not working
                editLine.setValidator(editValidator())
                toolbarInstance.addWidget(editLine)
            elif action['type'] == 'break':
                self.insertToolBarBreak(toolbarInstance)


    def onClick(self):
        print("test")


    def thresholdValidator(self):
        validator = QIntValidator()
        validator.setRange(-25, 25)
        return validator


    def getPorts(self):
        """Shows the ports whose connection is made with Arduino (LINUX ONLY!!)"""

        ports = [f.name for f in os.scandir('/dev') if f.name.startswith('ttyACM')]
        return ports if ports else ['no board']


    def _createStatusBar(self):
        """Creates status bar"""

        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("background-color: rgb(0, 122, 204);")
        self.statusbar.showMessage("Viva!", 3000)

        self.labelFilename = QLabel('instance_name.iad') # TODO filename
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
        #tabPlotContainer.setColor("background-color: rgb(0, 0, 0);")
        tabPlotContainer.addWidget(plot)

        # table
        tabTable = QWidget()
        tableWidget = QTableWidget(5, 4)
        tableWidget.setHorizontalHeaderLabels(['Time(s)', 'Voltage(V)', 'Moving Average', 'PWM', ''])
        tableWidget.horizontalHeader().setStretchLastSection(True)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
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

        self.log('Stopped reading.')


    def log(self, message, type='info'):
        """Writes the string @message to the logger - sometimes with an emoji :)"""

        logMessage = time.strftime("%H:%M:%S", time.localtime()) + '\t' + message# + '\t' + self.configs.emojis[type]
        self.logger.appendPlainText(logMessage)


    # TODO missing args from the caller
    def setupEnvironment(self, configsPath='./configs/settings.json'):
        """Sets up the global environment according to the .configs.json file"""

        with open(configsPath, 'r') as file_configs:
            self.configs = json.load(file_configs)