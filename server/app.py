import json
from itertools import groupby
from uuid import uuid4
from bson.objectid import ObjectId
from flask import Flask, request, session, abort, Response
from flask import render_template, url_for, jsonify
from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.pymongo import PyMongo
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown
from flask.ext.user import current_user, login_required, UserManager, UserMixin, SQLAlchemyAdapter
from flask_wtf.csrf import CsrfProtect

from gears_less import LESSCompiler
from gears_coffeescript import CoffeeScriptCompiler

#Comment out this block if you run this file directly. (Strictly for development purposes only)
from .flask_gears import Gears
from .sessions import MongoSessionInterface

#For running this file directly uncomment this and comment the block above it.
#from flask_gears import Gears
#from sessions import MongoSessionInterface
#from settings import MONGO_DBNAME, SECRET_KEY, DEBUG_MODE

from .settings import ServerSettingsManager
settings_manager = ServerSettingsManager.get_instance()

class ServerApp:
    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            instance = ServerApp()

        return instance

    def __init__(self):
        self.gears = Gears(
            compilers={
            '.less': LESSCompiler.as_handler(),
            '.coffee': CoffeeScriptCompiler.as_handler(),
            #    '.hbs': 'gears_handlebars.HandlebarsCompiler'
            }
        )

        self.app = Flask(__name__)
        self.gears.init_app(self.app)

        self.app.config.from_object(settings_manager.settings)

        self.mongo = PyMongo(self.app)
        self.babel = Babel(self.app)
        self.db = SQLAlchemy(self.app)
        self.mail = Mail(self.app)
        self.md = Markdown(self.app)
        self.csrf = CsrfProtect(self.app)

        self.app.session_interface = MongoSessionInterface(self.app, self.mongo)

    def bootstrap_user(self):
        from .models import User
        self.db_adapter = SQLAlchemyAdapter(self.db, User)
        self.user_manager = UserManager(self.db_adapter, self.app)

from .views.api import *
from .views.dashboard import *
from .models import *
