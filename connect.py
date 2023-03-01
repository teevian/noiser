import serial, time

##  IAD protocol {Id Analog Data}
# We've created a protocol for communications between Raspberry and Arduino
# 

# securely checks for serial connection with arduino
def checkConnection(PATH_SERIAL_ARDUINO = '/dev/ttyACM0'):
    try:
        serial_con = serial.Serial(PATH_SERIAL_ARDUINO, 9600, timeout=1)
    except serial.SerialException:
        raise Exception('No Arduino is connected to the serial port!')
    else:
        time.sleep(1)

        if serial_con.isOpen():
            print("Arduino found!")
            return serial_con
        else:
            print("Arduino not found!")

# securely opens serial connection with arduino
def openConnection(PATH_SERIAL_ARDUINO = '/dev/ttyACM0'):
    try:
        serial_con = checkConnection()
    except Exception as err:
        print('Connection failed: ' + str(err))

        return serial_con
    else:
        print('Connection established')

def sendData():
    serial_con = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    serial_con.reset_input_buffer()

    while True:
        serial_con.write('{ID, ANALOG, DATA}'.econde('utf-8'))
        line = serial_con.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(1)

def requestLiveDataFromPin(pin):
    serial_con = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    serial_con.reset_input_buffer()

    serial_con.write(str(0).encode('utf-8'))
    
    while True:
        if serial_con.in_waiting > 0:   # checks if any data is available
            line = serial_con.readline().decode('utf-8').rstrip()
            print(line)


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