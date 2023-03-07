#!/usr/bin/env python

import json, time, os
import pyqtgraph as pg

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

    def __init__(self, parent = None):
        super(NoiserGUI, self).__init__(parent)
        configs = self.setupEnvironment()
        self.initUI(configs)

    def initUI(self, configs):
        """
            Sets up the layout and user interface
        """

        ## window setup
        window = configs['main_window']

        self.setWindowTitle(window['title'])
        self.setWindowIcon(QIcon(window['icon']))
        self.resize(QSize(window['width'], window['height']))

        ## global interface variables
        self.ICON_SIZE = QSize(window['ic_size'], window['ic_size'])
        self.filename = 'instance_name.iad'

        ## create menus
        self._createMenuBar()
        self._createToolBars()
        self._createStatusBar()

        ## create widgets
        self.log = NoiserGUI.Logger()

        self.createAnalyzer()
        self.createNoter()
        self.createGroupAnalogPinChoice()
        self.createGroupSchedule()
        self.createControllers()

        ## left board - data analyzer
        containerLeft = QVBoxLayout()
        containerLeft.addStretch()
        containerLeft.addWidget(self.analyzer, alignment = Qt.AlignTop)
        containerLeft.addStretch()
        containerLeft.addWidget(self.log)

        ## right board - data handler
        containerRight = QVBoxLayout()
        containerRight.addWidget(self.tabNoter )
        containerRight.addWidget(self.groupPinChoice)
        containerRight.addWidget(self.groupSchedule)
        containerRight.addLayout(self.layoutControllers)
        containerRight.addStretch()

        ## main container - disposes into two columns
        containerMain = QHBoxLayout()
        containerMain.addLayout(containerLeft)
        containerMain.addLayout(containerRight)

        ## pasting layout into QWidget
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
        
        def e(self, message, exception):   # logs error messages
            logMessage = time.strftime("%H:%M:%S", time.localtime()) + '\t' + message
            self.appendPlainText(logMessage)


    def createNoter(self):
        """
            Creates a noter input text
        """

        self.tabNoter = QTabWidget(movable=True, tabPosition=QTabWidget.East)
        self.tabNoter.setStyleSheet('QTabWidget::pane { border: 0; }')

        notesColors = ['#F5DEB3', '#B5EAEA', '#E0B0FF', '#9AC48A']
        for i, color in enumerate(notesColors):
            note = QTextEdit()
            note.setStyleSheet(f"background-color: {color}; color: black")
            self.tabNoter.setFixedHeight(note.fontMetrics().lineSpacing() * 8 )
            self.tabNoter.setFixedWidth(note.fontMetrics().width('W') * 18 )

            note.setPlainText(f'note #{i+1}')
            self.tabNoter.addTab(note, '')

    # TODO
    def _createMenuBar(self):
        pass


    def _createToolBars(self, path='./configs/toolbars.json'):
        """
            Creates the toolbars in a smarter way
        """

        with open(path, 'r') as toolbars_file:
            toolbars = json.load(toolbars_file)
            for toolbar_name in toolbars:
                self._createToolbar(toolbars[toolbar_name], toolbar_name)

    def _createToolbar(self, toolbar, name):
        """
            Wizard code to deal with toolbars - new way of doing!
        """

        ## sets up this @toolbar instance
        toolbar_instance = QToolBar(name)
        toolbar_instance.setIconSize(self.ICON_SIZE)

        actions = toolbar['actions']
        settings = toolbar['settings']

        ## set up geometry settings into code
        movable     = settings.get('movable', 'True').lower() == 'true'
        floatable   = settings.get('floatable', 'True').lower() == 'true'
        position    = settings.get('position', 'top')

        toolbar_instance.setMovable(movable)
        toolbar_instance.setFloatable(floatable)
        self.addToolBar({
            'top' : Qt.TopToolBarArea,
            'left' : Qt.LeftToolBarArea,
            'bottom' : Qt.BottomToolBarArea,
            'right' : Qt.RightToolBarArea
            }[position],
            toolbar_instance)

        # TODO create an exception AND IMPROVE THIS
        ## toolbar factory from lambda dictionary
        for action in actions:
            if action['type'] == 'button':
                btAction = QAction(QIcon(action['icon']), action['name'], self)
                btAction.setStatusTip(action['status'])
                btAction.triggered.connect(getattr(self, action['action']))
                toolbar_instance.addAction(btAction)
            elif action['type'] == 'separator':
                toolbar_instance.addSeparator()
            elif action['type'] == 'label':
                toolbar_instance.addWidget(QLabel(action['text']))
            elif action['type'] == 'combobox':
                comboBoxPorts = QComboBox()
                itemsFunction = getattr(self, action['action'])
                items = itemsFunction()
                comboBoxPorts.addItems(items)
                toolbar_instance.addWidget(comboBoxPorts)
            elif action['type'] == 'spinbox':
                toolbar_instance.addWidget(QSpinBox())
            elif action['type'] == 'lineEdit':
                editLine = QLineEdit()
                editLine.setFixedWidth(int(action['width']))
                editValidator = getattr(self, action['validator']) # TODO validator not working
                editLine.setValidator(editValidator())
                toolbar_instance.addWidget(editLine)
            elif action['type'] == 'break':
                self.insertToolBarBreak(toolbar_instance)

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


    def _createStatusBar(self, background_color='background-color: rgb(0, 122, 204);'):
        """
            Creates status bar
        """

        ## status bar with greeting
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet(background_color)
        self.statusbar.showMessage(_('LUIS_MELO_GREETING'), 3000)

        self.label_filename = QLabel(self.filename) # TODO filename
        self.statusbar.addPermanentWidget(self.label_filename)


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


    def createGroupAnalogPinChoice(self):
        """
            Creates the group for radio pins
        """

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


    def createGroupSchedule(self):
        """
            Allows to schedule the measuring time
        """

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

        self.groupSchedule = QGroupBox('Schedule')
        self.groupSchedule.setCheckable(True)
        self.groupSchedule.setChecked(False)
        self.groupSchedule.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btPlayPause = QPushButton(QIcon('./data/icons/target.svg'), '')
        self.btPlayPause.setIconSize(self.ICON_SIZE)
        self.btPlayPause.setCheckable(True)
        self.btPlayPause.toggled.connect(self.btPlayPauseOnToggled)

        self.btRegister = QPushButton(QIcon('./data/icons/save_data.svg'), '')
        self.btRegister.setIconSize(self.ICON_SIZE)
        self.btRegister.setCheckable(True)
        self.btRegister.toggled.connect(self.btPlayPauseOnToggled)

        self.groupSchedule.setLayout(layoutVContainer)

    def createControllers(self):
        # TODO use grid layout
        self.layoutControllers = QHBoxLayout()
        self.layoutControllers.addWidget(self.btPlayPause)
        self.layoutControllers.addWidget(self.btRegister)

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

        tabPlot = self._analyzerTab(QHBoxLayout, plot)
        tabTable = self._analyzerTab(QHBoxLayout, table)
  
        self.analyzer.addTab(tabPlot, QIcon('./data/icons/ic_read.svg'), 'Plot')
        self.analyzer.addTab(tabTable, QIcon('./data/icons/ic_sum'), 'Table')

        table.setHorizontalHeaderLabels(['Time(s)', 'Voltage(V)', 'Moving Average', 'Comment'])
        table.verticalHeader().setVisible(False)

    def _analyzerTab(self, layoutType, widget):
        """
            Wizard creates a tab for the analyzer board
        """
        tab_widget = QWidget()

        layout = layoutType(tab_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        tab_widget.setLayout(layout)
        layout.addWidget(widget)

        return tab_widget

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