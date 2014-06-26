import platform
import sys

from server.settings import ServerSettingsManager

if 'test' in sys.argv:
    settings = ServerSettingsManager.init_instance('test')
elif 'production' in sys.argv:
    settings = ServerSettingsManager.init_instance('production')
else:
    settings = ServerSettingsManager.init_instance('debug')

if platform.system() == "Windows":
    from win_manager import WindowsManager
    manager = WindowsManager()
    manager.run_manager()
else:
    from unix_manager import UnixManager
    manager = UnixManager()
    manager.run_manager()
