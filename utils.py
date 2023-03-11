import os

def searchForFile(folder, file):
    return [f.name for f in os.scandir('/dev') if f.name.startswith('ttyACM')]

def icon(iconName):
    """Returns the relative path of the icon from its name"""
    return './icons/ic_' + iconName + '.svg'


class USBWatcher(QObject):
    deviceAdded = pyqtSignal(str)
    deviceRemoved = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._udev = pyudev.Context()
        self._monitor = pyudev.Monitor.from_netlink(self._udev)
        self._monitor.filter_by(subsystem='usb')
        self._observer = pyudev.MonitorObserver(self._monitor, self._onDeviceEvent)
        
    def start(self):
        self._observer.start()
        
    def stop(self):
        self._observer.stop()
        
    def _onDeviceEvent(self, action, device):
        if action == 'add':
            self.deviceAdded.emit(device.device_path)
        elif action == 'remove':
            self.deviceRemoved.emit(device.device_path)
