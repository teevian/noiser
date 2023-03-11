#!/usr/bin/env python

import json

from msgid import _
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
    QAction, QDoubleSpinBox, QCheckBox, QGridLayout, QFormLayout, QLayout
)
from PyQt5.QtGui import (
    QIcon, QIntValidator, QPixmap
)


######################################################################
# Widgets and stuff
######################################################################

def Noter(self, colors):
    """
        Factors a tab with notes for user input
    """
    self.tabNoter = QTabWidget(movable=True, tabPosition=QTabWidget.East)
    self.tabNoter.setStyleSheet('QTabWidget::pane { border: 0; }')

    for i, color in enumerate(colors):
        note = QTextEdit()
        note.setStyleSheet(f"background-color: {colors[color]}; color: black")
        self.tabNoter.setFixedHeight(note.fontMetrics().lineSpacing() * 8)
        self.tabNoter.setFixedWidth(note.fontMetrics().width('W') * 18)

        note.setPlainText(f'note #{i+1}')
        self.tabNoter.addTab(note, '')


def AnalyzerTab(layoutType, widget):
    """
        Factors a tab for the analyzer board
    """
    analyzerTab = QWidget()
    layout = layoutType(analyzerTab)
    layout.setContentsMargins(0, 0, 0, 0)
    analyzerTab.setLayout(layout)
    layout.addWidget(widget)

    return analyzerTab


def AnalogPinChoicer(self):
    """
        Factors a group for radio pins
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


def Scheduler(self):
    """
        Factors a scheduler for controlling time while reading
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
    self.btPlayPause.toggled.connect(self.onReadStopButtonClick)

    self.btRegister = QPushButton(QIcon('./data/icons/save_data.svg'), '')
    self.btRegister.setIconSize(self.ICON_SIZE)
    self.btRegister.setCheckable(True)
    self.btRegister.toggled.connect(self.btPlayPauseOnToggled)

    self.groupSchedule.setLayout(layoutVContainer)


def Controllers(self):
    self.layoutControllers = QHBoxLayout()
    self.layoutControllers.addWidget(self.btPlayPause)
    self.layoutControllers.addWidget(self.btRegister)


def boardInfo():
    dialog = QDialog()
    dialog.setWindowTitle("Arduino Information")
    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.setLayout(QVBoxLayout())

    # create arduino information section
    arduino_info_section = QGroupBox("Arduino Information")
    arduino_info_section_layout = QFormLayout()
    arduino_info_section_layout.setAlignment(Qt.AlignLeft)

    # create image
    arduino_image = QLabel()
    arduino_pixmap = QPixmap("./data/icons/img_arduino_uno.png")
    arduino_pixmap = arduino_pixmap.scaledToWidth(300)
    arduino_image.setPixmap(arduino_pixmap)
    arduino_image.setAlignment(Qt.AlignCenter)
    arduino_info_section_layout.addRow(arduino_image)

    # create arduino model label and value
    arduino_model_label = QLabel("<b>Model:</b>")
    arduino_model_value = QLabel("Arduino Uno")
    arduino_model_label.setAlignment(Qt.AlignLeft)
    arduino_model_value.setAlignment(Qt.AlignLeft)
    arduino_info_section_layout.addRow(arduino_model_label, arduino_model_value)

    # create arduino memory label and value
    arduino_memory_label = QLabel("<b>Memory:</b>")
    arduino_memory_value = QLabel("32 KB Flash, 2 KB SRAM, 1 KB EEPROM")
    arduino_memory_label.setAlignment(Qt.AlignLeft)
    arduino_memory_value.setAlignment(Qt.AlignLeft)
    arduino_info_section_layout.addRow(arduino_memory_label, arduino_memory_value)

    # create arduino ports label and value
    arduino_ports_label = QLabel("<b>Ports:</b>")
    arduino_ports_value = QLabel("1 x USB, 1 x Serial")
    arduino_ports_label.setAlignment(Qt.AlignLeft)
    arduino_ports_value.setAlignment(Qt.AlignLeft)
    arduino_info_section_layout.addRow(arduino_ports_label, arduino_ports_value)

    arduino_info_section.setLayout(arduino_info_section_layout)

    # create connection information section
    connection_info_section = QGroupBox("Connection Information")
    connection_info_section_layout = QFormLayout()
    connection_info_section_layout.setAlignment(Qt.AlignLeft)

    # create connection type label and value
    connection_type_label = QLabel("<b>Type:</b>")
    connection_type_value = QLabel("Serial")
    connection_type_label.setAlignment(Qt.AlignLeft)
    connection_type_value.setAlignment(Qt.AlignLeft)
    connection_info_section_layout.addRow(connection_type_label, connection_type_value)

    # create last connection time label and value
    last_connection_time_label = QLabel("<b>Last Connection Time:</b>")
    last_connection_time_value = QLabel("2022-03-12 10:30:00")
    last_connection_time_label.setAlignment(Qt.AlignLeft)
    last_connection_time_value.setAlignment(Qt.AlignLeft)
    connection_info_section_layout.addRow(last_connection_time_label, last_connection_time_value)

    connection_info_section.setLayout(connection_info_section_layout)

    # add sections to dialog layout
    dialog.layout().addWidget(arduino_info_section)
    dialog.layout().addWidget(connection_info_section)

    # create close button
    close_button = QPushButton("Close")
    close_button.setMaximumWidth(100)
    close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    close_button.clicked.connect(dialog.accept)

    # add close button to dialog layout
    dialog.layout().addWidget(close_button, alignment=Qt.AlignRight)

    # show dialog
    dialog.exec_()


def boardCode(path='./noiserino/noiserino.ino'):
    with open(path, "r") as f:
        code = f.read()

    dialog = QDialog()
    dialog.setWindowTitle("Noiserino code:")
    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.resize(800, 600)

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    # create title label for code section
    code_label = QLabel("Noiserino code:")
    code_label.setAlignment(Qt.AlignLeft)
    layout.addWidget(code_label)

    # create PlainTextEdit with the code
    code_editor = QPlainTextEdit()
    code_editor.setPlainText(code)
    layout.addWidget(code_editor)

    # create close button
    close_button = QPushButton("Close")
    close_button.setMaximumWidth(100)
    close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    close_button.clicked.connect(dialog.accept)

    # add close button to dialog layout
    layout.addWidget(close_button, alignment=Qt.AlignRight)

    # show dialog
    dialog.exec_()


######################################################################
# Menus and Bars
######################################################################

def MenuBar(window, path):
    """
        Factors a StatusBar from a json file
    """
    pass


def StatusBar(window, filename, backgroundColor='background-color: rgb(0, 122, 204);'):
    """
        Factors the statusbar
    """

    # status bar with Professor's type of greeting
    statusbar = window.statusBar()
    statusbar.setStyleSheet(backgroundColor)
    statusbar.showMessage(_('EASTER_EGG_LUIS_MELO_GREETING'), 3000)

    label_filename = QLabel(filename)
    statusbar.addPermanentWidget(label_filename)


def ToolBars(self, path='./configs/toolbars.json'):
    """
        Factors the toolbars in a smarter way
    """
    with open(path, 'r') as toolbars_file:
        toolbars = json.load(toolbars_file)
        for toolbar_name in toolbars:
            ToolBar(self, toolbars[toolbar_name], toolbar_name)


def ToolBar(self, toolbarModel, name):
    """
        Wizard code to deal with toolbars - new way of doing!
    """
    # sets up this @toolbar instance
    toolbar = QToolBar(name)
    toolbar.setIconSize(self.ICON_SIZE)

    actions = toolbarModel['actions']
    settings = toolbarModel['settings']

    # sets up geometry settings into code
    movable = settings.get('movable', 'True').lower() == 'true'
    floatable = settings.get('floatable', 'True').lower() == 'true'
    position = settings.get('position', 'top')

    toolbar.setMovable(movable)
    toolbar.setFloatable(floatable)
    self.addToolBar({
        'top': Qt.TopToolBarArea,
        'left': Qt.LeftToolBarArea,
        'bottom': Qt.BottomToolBarArea,
        'right': Qt.RightToolBarArea
    }[position],
        toolbar)

    # TODO create an exception AND OPTIMIZE THIS CODE BEFORE PROJECT SUBMISSION TODO TODO TODO TODO
    # toolbar factory from lambda dictionary
    for action in actions:
        if action['type'] == 'button':
            button = QAction(QIcon(action['icon']), action['name'], self)
            button.setStatusTip(action['status'])
            button.triggered.connect(getattr(self, action['action']))
            toolbar.addAction(button)
        elif action['type'] == 'separator':
            toolbar.addSeparator()
        elif action['type'] == 'label':
            toolbar.addWidget(QLabel(action['text']))
        elif action['type'] == 'combobox':
            comboBoxPorts = QComboBox()
            function = getattr(self, action['action'])
            if '@id' in action:
                id = action['@id']
                self.ids[id] = comboBoxPorts
            items = function()
            comboBoxPorts.addItems(items)
            toolbar.addWidget(comboBoxPorts)
        elif action['type'] == 'spinbox':
            spinBox = QSpinBox()
            spinBox.setStatusTip(action['status'])
            spinBox.setValue(int(action['value']))
            spinBox.setRange(int(action['min']), int(action['max']))
            function = getattr(self, action['action'])
            spinBox.valueChanged.connect(function)
            if '@id' in action:
                id = action['@id']
                self.ids[id] = spinBox
            toolbar.addWidget(spinBox)
        elif action['type'] == 'lineEdit':
            editLine = QLineEdit()
            editLine.setFixedWidth(int(action['width']))
            # TODO validator not working
            editValidator = getattr(self, action['validator'])
            editLine.setValidator(editValidator())
            toolbar.addWidget(editLine)
        elif action['type'] == 'break':
            self.insertToolBarBreak(toolbar)
