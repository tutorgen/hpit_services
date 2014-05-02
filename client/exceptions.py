class ConnectionError(Exception):
    """
    This exception indicates that an connection to the HPIT central server
    could not be completed.
    """
    pass

class PluginRegistrationError(Exception):
    """
    This exception indicates that a plugin could not register with HPIT.
    """
    pass

class PluginPollError(Exception):
    """
    This exception indicates that a plugin could not poll HPIT.
    """
    pass

class ResponseDispatchError(Exception):
    """
    This exception indicates that a response from HPIT could not be dispatched to a callback.
    """
    pass
