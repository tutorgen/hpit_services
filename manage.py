import platform
import os

from hpit.management.settings_manager import SettingsManager

try:
    settings = SettingsManager.init_instance(os.environ['HPIT_ENV'])
except KeyError:
    settings = SettingsManager.init_instance('debug')

manager = None
if platform.system() == "Windows":
    from hpit.management.win_manager import WindowsManager
    manager = WindowsManager()
else:
    from hpit.management.unix_manager import UnixManager
    manager = UnixManager()

import hpit.server.views.api
import hpit.server.views.dashboard
import hpit.server.models

if manager:
    manager.run_manager()
