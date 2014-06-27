import platform
import sys

from server.settings import ServerSettingsManager

if 'test' in sys.argv:
    settings = ServerSettingsManager.init_instance('test')
elif 'production' in sys.argv:
    settings = ServerSettingsManager.init_instance('production')
else:
    settings = ServerSettingsManager.init_instance('debug')

manager = None
if platform.system() == "Windows":
    from win_manager import WindowsManager
    manager = WindowsManager()
else:
    from unix_manager import UnixManager
    manager = UnixManager()

import server.views.api
import server.views.dashboard
import server.models

if manager:
    manager.run_manager()
