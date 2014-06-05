import mimetypes
import os
from io import BytesIO
from functools import partial
from flask import send_file, current_app, url_for, request
from jinja2 import Markup

from gears.assets import build_asset
from gears.compat import bytes
from gears.environment import Environment, DEFAULT_PUBLIC_ASSETS
from gears.exceptions import FileNotFound
from gears.finders import FileSystemFinder


class Gears(object):

    css_template = '<link rel="stylesheet" href="{url}">'
    js_template = '<script src="{url}"></script>'

    def __init__(self, app=None, defaults=True, assets_folder='assets',
                 compilers=None, compressors=None, public_assets=None,
                 extra_public_assets=None, cache=None, gzip=False):
        self.defaults = defaults
        self.assets_folder = assets_folder
        self.compilers = compilers
        self.compressors = compressors
        self.public_assets = public_assets
        self.extra_public_assets = extra_public_assets
        self.cache = None
        self.gzip = gzip
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['gears'] = {}
        self.init_environment(app)
        self.init_asset_view(app)

        @app.context_processor
        def gears_processor():
            return dict(
                css_tag=partial(self.html_tag, self.css_template),
                js_tag=partial(self.html_tag, self.js_template),
            )

    def init_environment(self, app):
        environment = Environment(
            root=self.get_static_folder(app),
            public_assets=self.get_public_assets(app),
            cache=self.get_cache(app),
            gzip=self.gzip,
        )
        if self.defaults:
            environment.register_defaults()
            environment.finders.register(self.get_default_finder(app))
        if self.compilers is not None:
            for extension, compiler in self.compilers.items():
                environment.compilers.register(extension, compiler)
        if self.compressors is not None:
            for mimetype, compressor in self.compressors.items():
                environment.compressors.register(mimetype, compressor)
        app.extensions['gears']['environment'] = environment

    def init_asset_view(self, app):
        app.extensions['gears']['static_view'] = app.view_functions['static']
        app.view_functions['static'] = self.asset_view

    def asset_view(self, filename):
        environment = current_app.extensions['gears']['environment']
        static_view = current_app.extensions['gears']['static_view']
        try:
            asset = build_asset(environment, filename)
        except FileNotFound:
            return static_view(filename)
        if request.args.get('body'):
            asset = asset.processed_source.encode('utf-8')
        mimetype, encoding = mimetypes.guess_type(filename)
        return send_file(BytesIO(bytes(asset)), mimetype=mimetype, conditional=True)

    def html_tag(self, template, logical_path, debug=False):
        environment = self.get_environment(current_app)
        if debug or self.debug(current_app):
            asset = build_asset(environment, logical_path)
            urls = []
            for requirement in asset.requirements:
                logical_path = requirement.attributes.logical_path
                url = url_for('static', filename=logical_path, body=1)
                urls.append(url)
        else:
            if logical_path in environment.manifest.files:
                logical_path = environment.manifest.files[logical_path]
            urls = (url_for('static', filename=logical_path),)
        return Markup('\n'.join(template.format(url=url) for url in urls))

    def get_environment(self, app):
        return app.extensions['gears']['environment']

    def get_default_finder(self, app):
        return FileSystemFinder(directories=(self.get_assets_folder(app),))

    def get_static_folder(self, app):
        return app.config.get('GEARS_ROOT', app.static_folder)

    def get_assets_folder(self, app):
        return os.path.join(app.root_path, self.assets_folder)

    def get_public_assets(self, app):
        if self.public_assets is not None:
            public_assets = tuple(self.public_assets)
        else:
            public_assets = DEFAULT_PUBLIC_ASSETS
        if self.extra_public_assets is not None:
            public_assets += tuple(self.extra_public_assets)
        return public_assets

    def get_cache(self, app):
        return self.cache

    def debug(self, app):
        return app.config.get('GEARS_DEBUG', app.debug)