import json
from flask import Flask
from flask.ext.pymongo import PyMongo
app = Flask(__name__)
mongo = PyMongo(app)

@app.route("/tutor/register/:name", methods=["POST"])
def register_tutor(name):
    import pdb; pdb.set_trace()
    return "Hello World!"

@app.route("/tutor/unregister/:name", methods=["POST"])
def unregister_tutor(name):
    return "Hello World!"

#@app.route("/plugin/register/:name", methods=["POST"])
#def register_plugin(name):
#    import pdb; pdb.set_trace()
#    return "Hello World!"

@app.route("/tutor/unregister/:name")
@app.route("/plugin/unregister/:name")
def unregister():
    return "Hello World!"

@app.route("/plugin/:name/subscribe/:event")
def subscribe():
    return "Hello World!"

@app.route("/plugin/:name/unsubscribe/:event")
def unsubscribe():
    return "Hello World!"

@app.route("/plugin/:name/transactions")
def transactions():
    return "Hello World!"

@app.route("/transaction", methods=["POST"])
def transaction():
    return "Hello World!"

@app.route("/")
def index():
    return "Welcome to HPIT Hub."

if __name__ == "__main__":
    app.run(debug=True)