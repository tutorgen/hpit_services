import os
import json

def lists_to_tuples(the_dict):
    return {k : tuple(v) if type(v) is list else v for k, v in the_dict.items()}

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

        json_data = None
        with open(os.path.join(os.getcwd(), 'settings.json')) as f:
            json_data = json.loads(f.read())

        cls.settings = {}
        for env, settings in json_data.items():
            cls.settings[env] = {
                'plugin': type('PluginSettings', (object, ), lists_to_tuples(settings['plugin'])),
                'server': type('ServerSettings', (object, ), lists_to_tuples(settings['server']))
            }

        if not cls.server_settings_instance:
            if environment in cls.settings:
                cls.server_settings_instance = cls.settings[environment]['server']
                cls.plugin_settings_instance = cls.settings[environment]['plugin']
            else:
                raise Exception("No settings found for environment: " + environment)

        return cls.server_settings_instance

