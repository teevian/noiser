#!/usr/bin/env python

import os, time
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
    if arduinoPort:
        try:
            return serial.Serial(arduinoPort, timeout=1)
        except serial.SerialException:
            pass
    raise Exception('Serial monitor not found!')