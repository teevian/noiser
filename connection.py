#!/usr/bin/env python

from msgid import egg
import threading
import os, time
import random
import serial
import serial.tools.list_ports  # should pip install esptool (?)

from PyQt5.QtCore import QThread, pyqtSignal

######################################################################
# IAD protocol
######################################################################
# Created this protocol based on control characters in the likes of
# old system protocols for data transmission
######################################################################

IAD_PROTOCOL = {            # https://theasciicode.com.ar
    'START'     : b'\x01',  # SOH: start header control character  
    'PAUSE'     : b'\x03',  # ETX: indicates that it is the end of the message (interrupt)
    'STOP'      : b'\x04',  # EOT: indicates the end of transmission
    'ENQUIRE'   : b'\x05',  # ENQ: requests a response from arduino to confirm it is ready (Equiry)
    'OK'        : b'\x06',  # ACK: acknowledgement
    'SYNC'      : b'\x16',  # DLE: synchronous Idle (used for transmission)
    'ERROR'     : b'\x21'   # NAK: exclaim(error) special character
}

timeRate = 10
delay = 1 / timeRate # make sure it is not zero!
stop_flag = False

######################################################################
# Classes and Threads
######################################################################

class SerialReader(QThread):
    """
        Opens the serial to read asynchronosusly
    """
    data_ready = pyqtSignal(str)
    def __init__(self, _path, read_rate, parent=None):
        super().__init__(parent)
        self.serial_connection = serial.Serial(_path, 9600) ## ATTENTION TO THIS
        self.read_rate = read_rate

    def run(self):
        while True:
            if self.serial_connection.readable():
                analog_value = self.serial_connection.readline().decode().strip()
                # Emit a signal to update the GUI with the analog value
                self.data_ready.emit(analog_value)
            QThread.msleep(1000 // self.read_rate)


######################################################################
# Functions and utils
######################################################################

# TODO this function should return an integer; the string part should be handled on gui
def handshake(connection):
    """
        Handshake with Arduino. Retuns a string
    """
    connection.reset_input_buffer()
    connection.write(IAD_PROTOCOL['ENQUIRE'])

    time.sleep(0.1)
    if connection.readable():
        # readable is cool because it doesn't block I/O, as is_waiting does :)
        random_number = int(connection.readline().decode().strip())
        # print(f"Random: {random_number}")
        return egg(int(random_number))
    else:
        return "Arduino is down"


## TODO this should raise some kind of exception
def startReadingPin(self, connection, pin):
    """
        Starts reading input
    """
    connection.write(IAD_PROTOCOL['START'])

    # Wait for acknowledgement from Arduino TODO create timeout here
    while True:
        response = connection.read()
        if response == IAD_PROTOCOL['OK']:
            print(response)
            break

    # pin to read from
    pin = 1
    connection.write(pin.to_bytes(1, byteorder='little', signed=False))

    #
    self.btPlayPause.setText("Stop")
    self.is_reading = True
    self.serial_thread.start() # Start the serial reader thread

def stopReadingPin(self, connection, port):
    """
        Stops reading input
    """
    # Send command to Arduino to stop sending analog values
    connection.write(IAD_PROTOCOL['STOP'])

    self.btPlayPause.setText("Start")
    self.is_reading = False
    self.serial_thread.terminate() # Stop the serial reader thread


def getPorts(system):
    """
        Shows ports whose connection is made with Arduino - MacOS and Linux only, Windows is for humanities majors
    """
    ports = []
    if system.lower() == 'linux':       # Linux
        ports = [f.name for f in os.scandir('/dev') if f.name.startswith('ttyACM')]
    elif system.lower() == 'darwin':    # MacOS
        ports = [   
            port.device
            for port in serial.tools.list_ports.comports()
            if 'Arduino' in port.description and 'usbmodem' in port.device
        ]
    if not ports:
        raise Exception('BoardNotFound')
    return ports


def openConnection(port):
    """
        Opens the connection with arduino through @arduinoPort
    """
    if bool(port):
        try:
            # https://pyserial.readthedocs.io/en/stable/pyserial_api.html
            return serial.Serial(port, 9600, timeout=1)
        except serial.SerialException:
            raise Exception('Serial monitor not found!')


def info():
    """
        Receives a @connection string and returns a representative dict
    """
    pairsList = str(connection).split("(")[1].split(")")[0].split(",")      # remove special characters
    pairsList = [pair.strip() for pair in pairsList]                        # removes white spaces

    parsedConnection = {}
    for pair in pairsList:                                                  # splits into key-value pairs
        key, value = pair.split("=")
        parsedConnection[key.strip()] = value.strip()

    return parsedConnection

def stopListenToPin(pin = 0):
    ser.write(b"analog\n")
    response = ser.readline().decode().strip()
    print("Analog input values:", response)

def info():
    ser.write(b"info\n")
    response = ser.readline().decode().strip()
    print("Arduino information:", response)


CONTROLS = {
    "listen" : startReadingPin,
    "info" : info,
    "interrupt" : stopListenToPin,
    "test" : handshake
}