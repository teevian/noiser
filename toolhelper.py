def addButton(action, toolbar_instance, self):
    btAction = QAction(QIcon(action['icon']), action['name'], self)
    btAction.setStatusTip(action['status'])
    btAction.triggered.connect(getattr(self, action['action']))
    toolbar_instance.addAction(btAction)

def addSeparator(action, toolbar_instance, self):
    toolbar_instance.addSeparator()

def addLabel(action, toolbar_instance, self):
    toolbar_instance.addWidget(QLabel(action['text']))

def addCombobox(action, toolbar_instance, self):
    comboBoxPorts = QComboBox()
    itemsFunction = getattr(self, action['action'])
    items = itemsFunction()
    comboBoxPorts.addItems(items)
    toolbar_instance.addWidget(comboBoxPorts)

def addSpinbox(action, toolbar_instance, self):
    toolbar_instance.addWidget(QSpinBox())

def addLineEdit(action, toolbar_instance, self):
    editLine = QLineEdit()
    editLine.setFixedWidth(int(action['width']))
    editValidator = getattr(self, action['validator'])
    editLine.setValidator(editValidator())
    toolbar_instance.addWidget(editLine)

def addBreak(action, toolbar_instance, self):
    self.insertToolBarBreak(toolbar_instance)

actions = {
    'button': addButton,
    'separator': addSeparator,
    'label': addLabel,
    'combobox': addCombobox,
    'spinbox': addSpinbox,
    'lineEdit': addLineEdit,
    'break': addBreak
}

# to be called in another file
for action in actions:
    action_type = action['type']
    action_function = action_functions[action_type]
    action_function(action, toolbar_instance, self)