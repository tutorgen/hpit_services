import json
from itertools import groupby
from uuid import uuid4
from bson.objectid import ObjectId
from flask import Flask, request, session, abort, Response
from flask import render_template, url_for, jsonify
from flask.ext.pymongo import PyMongo

from gears_less import LESSCompiler
from gears_coffeescript import CoffeeScriptCompiler


#Comment out this block if you run this file directly. (Strictly for development purposes only)
from .flask_gears import Gears
from .sessions import MongoSessionInterface
from .settings import MONGO_DBNAME, SECRET_KEY, DEBUG_MODE

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

app.config['MONGO_DBNAME'] = MONGO_DBNAME
app.config['DEBUG'] = DEBUG_MODE
app.secret_key = SECRET_KEY

mongo = PyMongo(app)
app.session_interface = MongoSessionInterface(app, mongo)

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

__all__ = ['app']
