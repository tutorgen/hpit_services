import platform
import os

from hpit.management.settings_manager import SettingsManager

try:
    settings = SettingsManager.init_instance(os.environ['HPIT_ENV'])
except KeyError:
    settings = SettingsManager.init_instance('debug')

from hpit.management.entity_manager import EntityManager
manager = EntityManager()

import hpit.server.views.api
import hpit.server.views.dashboard
import hpit.server.models

if manager:
    manager.run_manager()
