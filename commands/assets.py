import os

from clint.textui import puts, colored

from gears.environment import Environment
from gears.assets import build_asset
from gears.finders import FileSystemFinder
from gears.exceptions import FileNotFound

class Command:
    description = "Build Gears assets for production deployments."
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def get_absolute_path(path):
        return os.path.normpath(os.path.abspath(os.path.join(os.getcwd(), path)))

    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        self.environment = Environment(self.get_absolute_path(self.args.output))
        self.environment.finders.register(FileSystemFinder([self.get_absolute_path(self.args.source)]))
        self.environment.register_defaults()

        for path in self.environment.public_assets:
            try:
                asset = build_asset(self.environment, path)
            except FileNotFound:
                continue

            self.environment.save_file(path, str(asset))
            source_path = os.path.relpath(asset.absolute_path)
            output_path = os.path.relpath(os.path.join(self.environment.root, path))
            puts(colored.green('- compiled %s to %s' % (source_path, output_path)))
