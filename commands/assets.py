import os

from clint.textui import puts, colored

from gears.environment import Environment
from gears.assets import build_asset
from gears.finders import FileSystemFinder
from gears.exceptions import FileNotFound

from server.flask_gears import Gears
from gears_less import LESSCompiler
from gears_coffeescript import CoffeeScriptCompiler

from server.app import ServerApp
app = ServerApp.get_instance().app
    
from .settings import ServerSettingsManager
settings = ServerSettingsManager.get_instance().settings

class Command:
    description = "Build Gears assets for production deployments."
    
    def __init__(self, manager, parser):
        self.manager = manager
        self.gears = Gears(
            compilers={
            '.less': LESSCompiler.as_handler(),
            '.coffee': CoffeeScriptCompiler.as_handler(),
            #    '.hbs': 'gears_handlebars.HandlebarsCompiler'
            }
        )

        parser.add_argument('src', metavar='src', type=str, 
                            help='The source directory of the assets to compile.',
                            default=os.path.join(settings.PROJECT_DIR, 'server/assets'))
        parser.add_argument('dest', type=str, 
                            help="The destination directory of where to put these assets.")

    
    def get_absolute_path(self, path):
        return os.path.normpath(os.path.abspath(os.path.join(settings.PROJECT_DIR, path)))


    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        assets = self.gears.get_public_assets(app)
        environment = self.gears.get_environment(app)

        for path in assets:
            try:
                asset = build_asset(environment, path)
            except FileNotFound:
                continue
            except TypeError:
                continue

            environment.save_file(path, str(asset))
            src_path = os.path.relpath(asset.absolute_path)
            dest_path = os.path.relpath(os.path.join(self.environment.root, path))
            puts(colored.green('- compiled %s to %s' % (src_path, dest_path)))
