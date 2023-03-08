import random

__MAP_MESSAGES = {
        "ENV_OK": "The environment is set and ready to go! ",
        "ENV_EXIT": "Live long and prosper! ",
        "CON_ERR_NOT_OK": "404: board not found ",
        "READ_START": "Reading... 🟢 ",
        "READ_STOP": "Stopped reading 🟥 ",
        "DATA_SAVE": "Saving the precious data... ",
        "DATA_LOAD": "Loading the precious data... ",
        "CON_NEW" : "Establishing a new connection... ",
        "CON_CHECKING_PORTS" : "Checking ports... ",
        "CON_ARDUINO_OK" : "Arduino found on port(s) ",
        "CON_SERIAL_OK" : "Serial connection established: Arduino says ",
        "CON_ARDUINO_ERR" : "Arduino not found ",
        "CON_SERIAL_ERR" : "Serial monitor not connected "
    }

def _(msgid):
    """
        Returns a message from the messages map
    """
    return __MAP_MESSAGES.get(msgid, msgid)


def egg():
    return random.choice(list({
        "EASTER_EGG_HTTP_418": "'HTTP 418: I'm a teapot 🫖' ",
        "EASTER_EGG_2001" : "'I'm sorry, Dave, I'm afraid I can't do that' ",
        "EASTER_EGG_HITCHHIKERS_GUIDE" : "'DON'T PANIC' ",
        "EASTER_EGG_HELLO_WORLD" : "'Hello, World!' ",
        "EASTER_EGG_APOLLO_13" : "Houston, we have a problem",
        "EASTER_EGG_PROF_LUIS_MELO_GREETING" : "'Viva!' "
    }.values()))