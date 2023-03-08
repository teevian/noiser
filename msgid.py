__MAP_MESSAGES = {
        "ENV_OK": "The environment is set and ready to go!",
        "ENV_EXIT": "Goodbye!",
        "CON_OK": "Connection established: Arduino says hi!",
        "CON_NOT_OK": "404: board not found",
        "READ_START": "Reading... 🟢",
        "READ_STOP": "Stopped reading 🟥",
        "DATA_SAVE": "Saving the precious data...",
        "DATA_LOAD": "Loading the precious data...",
        "EASTER_EGG": "HTTP 418: I'm a teapot 🫖",
        "LUIS_MELO_GREETING" : "Viva!",

        "CON_ARDUINO_CONNECTED" : "Arduino found on port(s) ",
        "CON_ERR_ARDUINO_NOT_CONNECTED" : "Arduino not found",
        "CON_ERR_SERIAL_NOT_CONNECTED" : "Serial monitor not connected"
    }

def _(msgid):
    """
        Returns a message from the messages map
    """

    return __MAP_MESSAGES.get(msgid, msgid)