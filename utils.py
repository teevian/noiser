import os

def searchForFile(folder, file):
    return [f.name for f in os.scandir('/dev') if f.name.startswith('ttyACM')]