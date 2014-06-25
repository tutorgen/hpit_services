class ConnectionError(Exception):
    """
    This exception indicates a generic HPIT connection problem.
    """

class AuthenticationError(Exception):
    """
    This exception raised on HPIT 403.
    """
    pass

class ResourceNotFoundError(Exception):
    """
    This exception raised on HPIT 403.
    """
    pass

class InternalServerError(Exception):
    """
    This exception raised on HPIT 500.
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

class InvalidMessageNameException(Exception):
    """
    This exception is raised when a user attempts to use a system message name, like 'transaction'.
    """
    
class BadCallbackException(Exception):
    """
    Raised when a callback is not callable
    """
    
