import os
import shutil

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
    
from server.settings import ServerSettingsManager
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
            },
            public_assets=(
                os.path.join(settings.PROJECT_DIR, 'server/assets/css/style.css'), 
                os.path.join(settings.PROJECT_DIR, 'server/assets/js/script.js')
            )
        )

        parser.add_argument('dest', type=str, help="The destination directory of where to put these assets.")

    
    def get_absolute_path(self, path):
        return os.path.normpath(os.path.abspath(os.path.join(settings.PROJECT_DIR, path)))


    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        dest_path = self.arguments.dest

        if not os.path.isabs(dest_path):
            dest_path = os.path.join(os.getcwd(), dest_path)

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        assets = self.gears.get_public_assets(app)
        environment = self.gears.get_environment(app)
        environment.root = dest_path

        for path in assets:
            try:
                asset = build_asset(environment, path)
            except FileNotFound:
                continue
            except TypeError:
                continue

            import pdb; pdb.set_trace()
            dest_filename = os.path.split(path)[1]
            asset_source = bytes(str(asset), 'utf-8')
            environment.save_file(dest_filename, asset_source)
            src_path = os.path.relpath(asset.absolute_path)
            dest_path = os.path.relpath(os.path.join(environment.root, path))
            puts(colored.green('- compiled %s to %s' % (src_path, dest_path)))
