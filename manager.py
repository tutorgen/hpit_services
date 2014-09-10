import platform
import os

from environment.settings_manager import SettingsManager

try:
    settings = SettingsManager.init_instance(os.environ['HPIT_ENV'])
except KeyError:
    settings = SettingsManager.init_instance('debug')

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
