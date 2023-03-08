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
        "CON_SERIAL_OK" : "Serial connection established! ",
        "CON_ARDUINO_SAYS" : "Arduino says: ",
        "CON_ARDUINO_ERR" : "Arduino not found ",
        "CON_SERIAL_ERR" : "Serial monitor not connected "
    }

def _(msgid):
    """
        Returns a message from the messages map
    """
    return __MAP_MESSAGES.get(msgid, msgid)

def egg(randomInt):
    eggs = [
        "'HTTP 418: I'm a teapot 🫖' ",                     # HTTP: 418
        "'I'm sorry, Dave, I'm afraid I can't do that' ",   # 2001 Space Odissey
        "'DON'T PANIC' ",                                   # Hitchhikers Guide to the Galaxy
        "'Hello, World!' ",                                 # Hello world
        "'Houston, we have a problem' ",                    # Apollo 13
        "'Viva!' "                                          # Prof Luis Melo greeting
    ]
    return eggs[randomInt % len(eggs)]