from .app import ServerApplication
from .settings import TestServerSettings, ServerSettings

application = ServerApplication.get_instance()

__all__ = ['application', 'TestServerSettings', 'ServerSettings']
