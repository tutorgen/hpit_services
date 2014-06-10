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

from gears_less import LESSCompiler
from gears_coffeescript import CoffeeScriptCompiler


#Comment out this block if you run this file directly. (Strictly for development purposes only)
from .flask_gears import Gears
from .sessions import MongoSessionInterface
from .settings import settings

#For running this file directly uncomment this and comment the block above it.
#from flask_gears import Gears
#from sessions import MongoSessionInterface
#from settings import MONGO_DBNAME, SECRET_KEY, DEBUG_MODE

gears = Gears(
    compilers={
    '.less': LESSCompiler.as_handler(),
    '.coffee': CoffeeScriptCompiler.as_handler(),
    #    '.hbs': 'gears_handlebars.HandlebarsCompiler'
    }
)

app = Flask(__name__)
gears.init_app(app)

app.config.from_object(settings)

mongo = PyMongo(app)
babel = Babel(app)
db = SQLAlchemy(app)
mail = Mail(app)
md = Markdown(app)

#Session Store
app.session_interface = MongoSessionInterface(app, mongo)

from server.models import User
db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)

HPIT_STATUS = {
    'tutors': [],
    'plugins': []
}

def _map_mongo_document(document):
    mapped_doc = {k: v for k, v in document.items()}

    if '_id' in mapped_doc:
        mapped_doc['id'] = str(mapped_doc['_id'])
        del mapped_doc['_id']

    return mapped_doc

@app.errorhandler(401)
def custom_401(error):
    return Response('You must establish a connection with HPIT first.', 
        401, {'WWWAuthenticate':'Basic realm="Login Required"'})

from server.views.api import *
from server.views.dashboard import *
from server.models import *

__all__ = ['app', 'mongo', 'db', 'babel', 'user_manager']
