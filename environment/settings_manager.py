from .debug.server_settings import ServerSettings as DebugServerSettings
from .test.server_settings import ServerSettings as TestServerSettings
from .travis.server_settings import ServerSettings as TravisServerSettings

from .debug.plugin_settings import PluginSettings as DebugPluginSettings
from .test.plugin_settings import PluginSettings as TestPluginSettings
from .travis.plugin_settings import PluginSettings as TravisPluginSettings



class SettingsManager:
    server_settings_instance = None
    plugin_settings_instance = None


    @classmethod
    def get_server_settings(cls):
        if not cls.server_settings_instance:
            raise Exception("Instance never initialized")

        return cls.server_settings_instance


    @classmethod
    def get_plugin_settings(cls):
        if not cls.plugin_settings_instance:
            raise Exception("No settings found for environment: " + cls.environment)

        return cls.plugin_settings_instance


    @classmethod
    def init_instance(cls, environment):
        cls.environment = environment

        if not cls.server_settings_instance:
            if environment == 'test':
                cls.server_settings_instance = TestServerSettings
                cls.plugin_settings_instance = TestPluginSettings
            elif environment == 'debug':
                cls.server_settings_instance = DebugServerSettings
                cls.plugin_settings_instance = DebugPluginSettings
            elif environment == 'travis':
                cls.server_settings_instance = TravisServerSettings
                cls.plugin_settings_instance = TravisPluginSettings
            else:
                raise Exception("No settings found for environment: " + environment)

        return cls.server_settings_instance

