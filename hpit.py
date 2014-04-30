import json
from itertools import groupby
from bson.objectid import ObjectId
from flask import Flask, request, render_template, url_for, jsonify
from flask.ext.pymongo import PyMongo
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'hpit_development'

mongo = PyMongo(app)

HPIT_STATUS = {
    'tutors': [],
    'plugins': []
}

def _map_mongo_document(document):
    mapped_doc = {k: v for k, v in document.items()}
    mapped_doc['id'] = str(mapped_doc['_id'])
    del mapped_doc['_id']
    return mapped_doc


@app.route("/tutor/connect/<name>", methods=["POST"])
def connect_tutor(name):
    """
    SUPPORTS: POST

    Stub for handling connection to HPIT.
    Currently not yet implemented.

    Returns: 200:STUB
    """
    if name not in HPIT_STATUS['tutors']:
        HPIT_STATUS['tutors'].append(name)

    return "STUB"

@app.route("/plugin/connect/<name>", methods=["POST"])
def connect_plugin(name):
    """
    SUPPORTS: POST

    Stub for handling connection to HPIT.
    Currently not yet implemented.

    Returns: 200:STUB
    """
    if name not in HPIT_STATUS['plugins']:
        HPIT_STATUS['plugins'].append(name)

    return "STUB"

@app.route("/tutor/disconnect/<name>", methods=["POST"])
def disconnect_tutor(name):
    """
    SUPPORTS: POST

    Stub for handling connection to HPIT.
    Currently not yet implemented.

    Returns: 200:STUB
    """
    if name not in HPIT_STATUS['tutors']:
        HPIT_STATUS['tutors'] = [tutor for tutor in HPIT_STATUS['tutors'] if tutor != name]

    return "STUB"

@app.route("/plugin/disconnect/<name>", methods=["POST"])
def disconnect_plugin(name):
    """
    SUPPORTS: POST

    Stub for handling connection to HPIT.
    Currently not yet implemented.

    Returns: 200:STUB
    """
    if name not in HPIT_STATUS['plugins']:
        HPIT_STATUS['plugins'] = [plugin for plugin in HPIT_STATUS['plugins'] if plugin != name]

    return "STUB"

@app.route("/plugin/<name>/subscribe/<event>", methods=["POST"])
def subscribe(name, event):
    """
    SUPPORTS: POST

    Start listening to an event type <event> for a specific plugin with
    the name <name>.

    Returns: 200:OK or 200:EXISTS
    """
    payload = {
        'name': name,
        'event': event
    }

    found = mongo.db.plugin_subscriptions.find_one(payload)

    if not found:
        mongo.db.plugin_subscriptions.insert(payload)
        return "OK"
    else:
        return "EXISTS"

@app.route("/plugin/<name>/unsubscribe/<event>", methods=["POST"])
def unsubscribe(name, event):
    """
    SUPPORTS: POST

    Stop listening to an event type <event> for a specific plugin with
    the name <name>.

    Returns: 200:OK or 200:DOES_NOT_EXIST
    """

    payload = {
        'name': name,
        'event': event
    }

    found = mongo.db.plugin_subscriptions.find_one(payload)

    if found:
        mongo.db.plugin_subscriptions.remove(payload)
        return "OK"
    else:
        return "DOES_NOT_EXIST"

@app.route('/plugin/<name>/subscriptions')
def plugin_list_subscriptions(name):
    """
    SUPPORTS: GET
    Lists the event names for transactions this plugin will listen to.
    If you are using the library then this is done under the hood to make sure
    when you perform a poll you are recieving the right transactions.

    Returns the event_names as a JSON list.
    """

    def _map_subscriptions(subscription):
        return subscription['name']

    subscriptions = list(mongo.db.plugin_subscriptions.find({'name': name}))
    subscriptions = [_map_subscriptions(sub) for sub in subscriptions]
    return jsonify({'subscriptions': subscriptions})


@app.route("/plugin/<name>/history")
def plugin_transaction_history(name):
    """
    SUPPORTS: GET
    Lists the transaction history for a specific plugin - including queued transactions.
    Does not mark them as recieved. 

    If you wish to preview queued transactions only use the '/preview' route instead.
    If you wish to actually CONSUME the queue (mark as recieved) use the '/transactions' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR TRANSACTIONS -- ONLY TO VIEW THEIR HISTORY.

    Returns JSON for the transactions.
    """
    my_transactions = mongo.db.plugin_transactions.find({
        'plugin_name': name,
    })

    result = [{
        'event_name': t['event_name'],
        'transaction': _map_mongo_document(t['transaction_payload'])
        } for t in my_transactions]

    return jsonify({'history': result})


@app.route("/plugin/<name>/preview")
def plugin_transaction_preview(name):
    """
    SUPPORTS: GET
    Lists the transactions queued for a specific plugin. 
    Does not mark them as recieved. Only shows transactions not marked as received.
    If you wish to see the entire transaction history for 
    the plugin use the '/history' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR TRANSACTIONS -- ONLY TO PREVIEW THEM.

    Returns JSON for the transactions.
    """
    my_transactions = mongo.db.plugin_transactions.find({
        'sent_to_plugin': False,
        'plugin_name': name,
    })

    result = [{
        'event_name': t['event_name'],
        'transaction': _map_mongo_document(t['transaction_payload'])
        } for t in my_transactions]

    return jsonify({'preview': result})


@app.route("/plugin/<name>/transactions")
def plugin_transactions(name):
    """
    SUPPORTS: GET
    List the transactions queued for a specific plugin.

    !!!DANGER!!!: Will mark the transactions as recieved by the plugin 
    and they will not show again. If you wish to see a preview
    of the transactions queued for a plugin use the /preview route instead.

    Returns JSON for the transactions.
    """
    my_transactions = mongo.db.plugin_transactions.find({
        'sent_to_plugin': False,
        'plugin_name': name,
    })

    result = [
        (t['_id'], t['event_name'], _map_mongo_document(t['transaction_payload']))
        for t in my_transactions
    ]

    update_ids = [t[0] for t in result]
    result = [{
        'event_name': t[1],
        'transaction': t[2]} for t in result]

    mongo.db.plugin_transactions.update(
        {'_id':{'$in': update_ids}},
        {"$set": {'sent_to_plugin':True}}, 
        multi=True
    )

    return jsonify({'transactions': result})


@app.route("/transaction", methods=["POST"])
def transaction():
    """
    SUPPORTS: POST
    Submit a transaction to the HPIT server. Expect the data formatted as JSON
    with the application/json mimetype given in the headers. Expects two fields in
    the JSON data.
        - name : string => The name of the event transaction to submit to the server
        - payload : Object => A JSON Object of the DATA to store in the database

    If successful the server will respond 200:OK
    """
    name = request.json['name']
    payload = request.json['payload']
    transaction_id = mongo.db.transactions.insert(payload)

    plugins = mongo.db.plugin_subscriptions.find({'event': name})

    for plugin in plugins:
        mongo.db.plugin_transactions.insert({
            'plugin_name': plugin['name'],
            'event_name': name,
            'transaction_id': transaction_id,
            'transaction_payload': payload,
            'sent_to_plugin': False
        })

    return "OK"


@app.route("/")
def index():
    """
    SUPPORTS: GET
    Shows the status dashboard and API route links for HPIT.
    """
    links = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            docs = app.view_functions[rule.endpoint].__doc__

            if docs:
                docs = docs.replace('\n', '<br/>')

            links.append((rule.rule, docs))

    return render_template('index.html', 
        links=links, 
        tutor_count=len(HPIT_STATUS['tutors']),
        plugin_count=len(HPIT_STATUS['plugins'])
    )

if __name__ == "__main__":
    app.run(debug=True)