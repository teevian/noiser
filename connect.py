import serial, time, os

PATH_SERIAL_ARDUINO = '/dev/ttyACM0'
names = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']

# securely opens serial connection with arduino
# TODO improve this
def openConnection(PATH_SERIAL_ARDUINO = '/dev/ttyACM0'):
    try:
        serial_connection = serial.Serial(PATH_SERIAL_ARDUINO, 9600, timeout=1)
    except serial.SerialException:
        raise Exception('Arduino not connected')
    else:
        time.sleep(1)

        if serial_connection.isOpen():
            print("Connection Established")
            return serial_connection
        else:
            print("Arduino not found!")

def requestLiveDataFromPin(pin = 0):
    serial_connection = openConnection()
    serial_connection.reset_input_buffer()
    serial_connection.write(pin if 0 <= pin <= 5 else 0)
    
    while True:
        if serial_connection.in_waiting > 0:   # checks if any data is available
            voltage = serial_connection.readline().decode('utf-8').rstrip()
            print(time.strftime("%H:%M:%S", time.localtime()) + " : " + voltage)


def sendData():
    serial_con = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    serial_con.reset_input_buffer()

    while True:
        serial_con.write('{ID, ANALOG, DATA}'.econde('utf-8'))
        line = serial_con.readline().decode('utf-8').rstrip()

        time.sleep(1)

def getData():
    serial_con = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    serial_con.reset_input_buffer()

    while True:
            if serial_con.in_waiting > 0:
                line = serial_con.readline().decode('utf-8').rstrip()
                print(line)

requestLiveDataFromPin(0);

"""
if not os.path.isfile(PATH_SERIAL_ARDUINO):
        raise Exception('No file was found at ' + PATH_SERIAL_ARDUINO + '. Check USB cable.')
    else:
"""