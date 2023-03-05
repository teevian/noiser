import os

def searchForFile(folder, file):
    return [f.name for f in os.scandir('/dev') if f.name.startswith('ttyACM')]

def icon(iconName):
    """Returns the relative path of the icon from its name"""
    return './icons/ic_' + iconName + '.svg'