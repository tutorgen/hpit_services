import os
import time
import shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from clint.textui import puts, colored

from gears.environment import Environment
from gears.assets import build_asset
from gears.finders import FileSystemFinder
from gears.exceptions import FileNotFound

from hpit.server.flask_gears import Gears
from gears_less import LESSCompiler
from gears_coffeescript import CoffeeScriptCompiler

from hpit.server.app import ServerApp
app = ServerApp.get_instance().app
    
from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()

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
                os.path.join(settings.PROJECT_DIR, 'hpit/server/assets/css/style.css'), 
                os.path.join(settings.PROJECT_DIR, 'hpit/server/assets/js/script.js')
            )
        )

        parser.add_argument('--dest', type=str, default="hpit/server/assets/compiled", help="The destination directory of where to put these assets.")
        parser.add_argument('--watch', action='store_true', help="Watch for changes to source files and compile on demand.")

    
    def get_absolute_path(self, path):
        return os.path.normpath(os.path.abspath(os.path.join(settings.PROJECT_DIR, path)))


    def _do_compilation(self, dest_path):
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

            dest_filename = os.path.split(path)[1]
            asset_source = bytes(str(asset), 'utf-8')
            environment.save_file(dest_filename, asset_source)
            src_path = os.path.relpath(asset.absolute_path)
            dest_path = os.path.relpath(os.path.join(environment.root, path))
            puts(colored.green('- compiled %s to %s' % (src_path, dest_path)))


    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        dest_path = self.arguments.dest

        me = self
        class RecompileAssetsEventHandler(FileSystemEventHandler):

            def on_any_event(self, event):
                me._do_compilation(dest_path)

        handle_file_change = RecompileAssetsEventHandler()

        if self.arguments.watch:
            observer = Observer()
            observer.schedule(
                handle_file_change, 'hpit/server/assets', recursive=True)
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        else:
            self._do_compilation(dest_path)

