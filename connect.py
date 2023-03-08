#!/usr/bin/env python

from msgid import egg
import os, time, random
import serial.tools.list_ports  # should pip install esptool


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


def openConnection(arduinoPort):
    """
        Opens the connection with arduino through @arduinoPort
    """
    if bool(arduinoPort):
        try:
            # https://pyserial.readthedocs.io/en/stable/pyserial_api.html
            return serial.Serial(arduinoPort, 9600, timeout=1)
        except serial.SerialException:
            raise Exception('Serial monitor not found!')


def listenToPin(connection, pin=0):
    connection.reset_input_buffer()

    connection.write(pin if 0 <= pin <= 5 else 0)
    
    while True:
        if connection.in_waiting > 0:   # checks if any data is available
            voltage = connection.readline().decode('utf-8').rstrip()
            print(time.strftime("%H:%M:%S", time.localtime()) + " : " + voltage)


def parseConnectionInfo(connection):
    """
        Receives a @connection string and returns a representative dict
    """
    pairsList = connection.split("(")[1].split(")")[0].split(",")   # remove special characters
    pairsList = [pair.strip() for pair in pairsList]                # removes white spaces

    parsedConnection = {}
    for pair in pairsList:                                          # splits into key-value pairs
        key, value = pair.split("=")
        parsedConnection[key.strip()] = value.strip()

    return parsedConnection


def testConnection(connection): # TODO missing arduino sending signal
    """
        Handshake between me and the Arduino: he gives a random number
    """
    return egg(random.randint(0, 100))