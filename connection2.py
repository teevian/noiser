import sys
import serial, time 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# THIS IS A TEST APPLICATION TO SEPARATE THE MODULE IN ORDER TO TEST COMMUNICATION

IAD_PROTOCOL = {            # https://theasciicode.com.ar
    'START'     : b'\x01',  # SOH: start header control character  
    'PAUSE'     : b'\x03',  # ETX: indicates that it is the end of the message (interrupt)
    'STOP'      : b'\x04',  # EOT: indicates the end of transmission
    'ENQUIRE'   : b'\x05',  # ENQ: requests a response from arduino to confirm it is ready (Equiry)
    'OK'        : b'\x06',  # ACK: acknowledgement
    'SYNC'      : b'\x16',  # DLE: synchronous Idle (used for transmission)
    'ERROR'     : b'\x21'   # NAK: exclaim(error) special character
}

class SerialReader(QThread):
    data_ready = pyqtSignal(str)

    def __init__(self, _ser, rate, parent=None):
        super().__init__(parent)
        self.ser = _ser
        self.rate = rate

    def run(self):
        while True:
            if self.ser.readable():
                analog_value = self.ser.readline().decode().strip()
                # Emit a signal to update the GUI with the analog value
                self.data_ready.emit(analog_value)
            QThread.msleep(1000 // self.rate)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set up serial communication with Arduino
        self.ser = serial.Serial('/dev/cu.usbmodem1101', 9600) 

        # Set up GUI
        self.setWindowTitle("Analog Value Reader")
        layout = QVBoxLayout(self)
        self.button = QPushButton("Start", clicked=self.start_stop_reading)
        layout.addWidget(self.button)
        self.text = QTextEdit()
        layout.addWidget(self.text)

        self.read_rate_label = QLabel("Read Rate (Hz):")
        layout.addWidget(self.read_rate_label)
        self.read_rate_spin_box = QSpinBox()
        self.read_rate_spin_box.setRange(1, 100)
        self.read_rate_spin_box.setValue(10)
        self.read_rate_spin_box.valueChanged.connect(self.set_read_rate)
        layout.addWidget(self.read_rate_spin_box)

        # Set up timer to read serial data
        self.serial_thread = SerialReader(self.ser, self.read_rate_spin_box.value(), self)
        self.serial_thread.data_ready.connect(self.update_gui)
        
        self.is_reading = False
        self.randomNumber = None

        self.random_button = QPushButton("Random Number", clicked=self.get_random_number)
        layout.addWidget(self.random_button)

    def get_random_number(self):
        self.ser.reset_input_buffer()
        self.ser.write(b'g')

        time.sleep(0.1)
        if self.ser.readable(): # ser readable doesnt block I/O
            self.random_number = int(self.ser.readline().decode().strip())
            print(f"Random: {self.random_number}")
        else:
            print("No data received")
            
    def start_stop_reading(self):
        if not self.is_reading:
            # Send command to Arduino to start sending analog values
            self.ser.write(IAD_PROTOCOL['START'])

            # Wait for acknowledgement from Arduino TODO create timeout here
            while True:
                response = self.ser.read()
                if response == IAD_PROTOCOL['OK']:
                    print(response)
                    break

            analog_pin = 1
            self.ser.write(analog_pin.to_bytes(1, byteorder='little', signed=False))

            self.button.setText("Stop")
            self.is_reading = True
            self.serial_thread.start() # Start the serial reader thread
        else:
            # Send command to Arduino to stop sending analog values
            self.ser.write(IAD_PROTOCOL['STOP'])
            self.button.setText("Start")
            self.is_reading = False
            self.serial_thread.terminate() # Stop the serial reader thread

    def update_gui(self, analog_value):
        self.text.append(f"{analog_value}")

    def set_read_rate(self, rate):
        self.serial_thread.rate = rate
    
    def closeEvent(self, event):
        if self.is_reading == False:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
