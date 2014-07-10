from uuid import uuid4
from bson.objectid import ObjectId
from datetime import datetime
from flask import session, jsonify, abort, request, Response


from server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app
mongo = app_instance.mongo
db = app_instance.db
csrf = app_instance.csrf

from server.models import Plugin, Tutor, Subscription


def _map_mongo_document(document):
    mapped_doc = {}

    for k, v in document.items():
        if k == '_id':
            v = str(v)
        elif k == 'message_id':
            v = str(v)
        elif isinstance(v, datetime):
            v = v.isoformat()

        mapped_doc[k] = v

    return mapped_doc


def bad_parameter_response(parameter):
    return ("Missing parameter: " + parameter, 401, dict(mimetype="application/json"))

def auth_failed_response():
    return ("Could not authenticate. Invalid entity_id/api_key combination.",
        403, dict(mimetype="application/json"))

def not_found_response():
    return ("Could not find the requested resource.", 404, dict(mimetype="application/json"))
   
def exists_response():
    return ("EXISTS", 200, dict(mimetype="application/json"))

def ok_response():
    return ("OK", 200, dict(mimetype="application/json"))

@app.errorhandler(401)
def custom_401(error):
    return Response('You must establish a connection with HPIT first.', 
        401, {'WWWAuthenticate':'Basic realm="Login Required"'})

    
@app.route("/version", methods=["GET"])
def version():
    """
    SUPPORTS: GET

    Gets the version of the HPIT server.

    Returns: 200:JSON with the following fields:
        - version : string -> version of HPIT
    """
    version_returned = {"version": settings.HPIT_VERSION}
    return jsonify(version_returned)


@csrf.exempt
@app.route("/connect", methods=["POST"])
def connect():
    """
    SUPPORTS: POST

    Establishes a RESTful session with HPIT.

    Accepts: JSON
        - entity_id : string -> Assigned entity id (unique)
        - api_key : string -> Assigned api key for connection authentication

    Returns: 
        200 on success
        404 if no entity or tutor is registered with the supplied entity_id
        403 if failed to authenticate (entity_id or api_key is invalid)
    """
    for x in ['entity_id', 'api_key']:
        if x not in request.json:
            return bad_parameter_response(x)

    entity_id = request.json['entity_id']
    api_key = request.json['api_key']

    entity = Tutor.query.filter_by(entity_id=entity_id).first()

    if not entity:
        entity = Plugin.query.filter_by(entity_id=entity_id).first()

    if not entity:
        return not_found_response()

    if not entity.authenticate(api_key):
        return auth_failed_response()

    #Clear the session
    session.clear()

    entity.connected = True

    #Renew Session
    session['entity_name'] = entity.name
    session['entity_description'] = entity.description
    session['entity_id'] = entity_id

    db.session.add(entity)
    db.session.commit()

    #All is well
    return ok_response()


@csrf.exempt
@app.route("/disconnect", methods=["POST"])
def disconnect():
    """
    SUPPORTS: POST

    Destroys the session for the entity calling this route.

    Accepts: JSON
        - entity_id : string -> Assigned entity id (unique)
        - api_key : string -> Assigned api key for connection authentication

    Returns: 
        200 on success
        404 if no entity or tutor is registered with the supplied entity_id
        403 if failed to authenticate (entity_id or api_key is invalid)
    """

    for x in ['entity_id', 'api_key']:
        if x not in request.json:
            return bad_parameter_response(x)

    if 'entity_id' not in session:
        return auth_failed_response()

    if session['entity_id'] != request.json['entity_id']:
        return auth_failed_response()

    entity_id = session['entity_id']
    api_key = request.json['api_key']

    entity = Tutor.query.filter_by(entity_id=entity_id).first()

    if not entity:
        entity = Plugin.query.filter_by(entity_id=entity_id).first()

    if not entity:
        return not_found_response()

    #Authenticate
    if not entity.authenticate(api_key):
        return auth_failed_response()

    entity.connected = False
    db.session.add(entity)
    db.session.commit()

    session.clear()

    return ok_response()


@csrf.exempt
@app.route("/log", methods=["POST"])
def log():
    """
    SUPPORTS: POST

    Stores a string as a log entry agains't the connected tutor or plugin.

    Accepts: JSON
        - log_entry - the text to log

    Returns: 
        403         - A connection with HPIT must be established first.
        404         - Could not find the entity stored in the session.
        200:OK      - Added the log entry
    """
    if 'log_entry' not in request.json:
        return bad_parameter_response()

    if 'entity_id' not in session:
        return auth_failed_response()

    mongo.db.entity_log.insert({
        'entity_id': session['entity_id'],
        'log_entry': request.json['log_entry'],
        'create_on': datetime.now().isoformat(),
        'deleted': False
    })

    return ok_response()


@csrf.exempt
@app.route("/log/list", methods=["GET"])
def log_list():
    """
    SUPPORTS: GET

    Returns a list of strings that are things that were logged.

    Returns: 
        403         - A connection with HPIT must be established first.
        404         - Could not find the entity stored in the session.
        200:JSON    - A list of strings.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    log_entries = mongo.db.entity_log.find({
        'entity_id': session['entity_id'],
        'deleted': False
    })

    result = [_map_mongo_document(t) for t in log_entries]

    return jsonify({'log': result})


@csrf.exempt
@app.route("/log/clear", methods=["GET"])
def log_clear():
    """
    SUPPORTS: GET

    Clears all the log entries for this entity.

    Returns: 
        403         - A connection with HPIT must be established first.
        404         - Could not find the entity stored in the session.
        200:OK      - The log list was cleared.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    mongo.db.entity_log.update(
        {'entity_id': session['entity_id'], 'deleted': False},
        {"$set": {'deleted':True}}, 
        multi=True
    )

    return ok_response()


@csrf.exempt
@app.route("/plugin/subscribe", methods=["POST"])
def subscribe():
    """
    SUPPORTS: POST

    Start listening to a message for the plugin that sends this request.

    Accepts: JSON
        - message_name - the name of the message to subscribe to

    Returns: 
        403         - A connection with HPIT must be established first.
        404         - Could not find the plugin stored in the session.
        200:OK      - Mapped the message to the plugin
        200:EXISTS  - The mapping already exists
    """
    if 'message_name' not in request.json:
        return bad_parameter_response()

    if 'entity_id' not in session:
        return auth_failed_response()

    message_name = request.json['message_name']
    entity_id = session['entity_id']

    plugin = Plugin.query.filter_by(entity_id=entity_id).first()

    if not plugin:
        return not_found_response()

    subscription = Subscription.query.filter_by(plugin=plugin, message_name=message_name).first()

    if subscription:
        return exists_response()

    subscription = Subscription()
    subscription.plugin = plugin
    subscription.message_name = message_name

    db.session.add(subscription)
    db.session.commit()

    return ok_response()


@csrf.exempt
@app.route("/plugin/unsubscribe", methods=["POST"])
def unsubscribe():
    """
    SUPPORTS: POST

    Stop listening to a message for the plugin that sends this request.

    Accepts: JSON
        - message_name - the name of the message to unsubscribe from

    Returns: 
        403         - A connection with HPIT must be established first.
        404         - Could not find the plugin stored in the session or could not find the subscription.
        200:OK      - Mapped the message to the plugin
        200:EXISTS  - The mapping already exists
    """

    if 'message_name' not in request.json:
        return bad_parameter_response()

    if 'entity_id' not in session:
        return auth_failed_response()

    message_name = request.json['message_name']
    entity_id = session['entity_id']

    plugin = Plugin.query.filter_by(entity_id=entity_id).first()

    if not plugin:
        return not_found_response()

    subscription = Subscription.query.filter_by(plugin=plugin, message_name=message_name).first()

    if not subscription:
        return not_found_response()

    db.session.delete(subscription)
    db.session.commit()

    return ok_response()


@app.route('/plugin/subscription/list')
def plugin_list_subscriptions():
    """
    SUPPORTS: GET

    Lists the messages this plugin will listen to.
    If you are using the library then this is done under the hood to make sure
    when you perform a poll you are recieving the right messages.

    Returns: 
        403         - A connection with HPIT must be established first.
        404         - Could not find the plugin stored in the session.
        200:OK      - A JSON list of the subscriptions for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    def _map_subscriptions(subscription):
        return subscription['message_name']

    entity_id = session['entity_id']

    plugin = Plugin.query.filter_by(entity_id=entity_id).first()

    if not plugin:
        return not_found_response()

    subscriptions = [x.message_name for x in plugin.subscriptions]

    return jsonify({'subscriptions': subscriptions})


@app.route("/plugin/message/history")
def plugin_message_history():
    """
    SUPPORTS: GET
    Lists the message history for the plugin - including queued messages.

    !!! IMPORTANT - Does not mark the messages as recieved. 

    If you wish to preview queued messages only use the '/message-preview' route instead.
    If you wish to actually CONSUME the queue (mark as recieved) use the '/messages' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR MESSAGES -- ONLY TO VIEW THEIR HISTORY.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_messages = mongo.db.plugin_messages.find({
        'plugin_entity_id': entity_id,
        'message_name' : {"$ne" : "transaction"}, 
    })

    result = [{
        'message_name': t['message_name'],
        'message': _map_mongo_document(t['message_payload'])
        } for t in my_messages]

    return jsonify({'message-history': result})

    
@app.route("/plugin/transaction/history")
def plugin_transaction_history():
    """
    SUPPORTS: GET
    Lists the transaction history for a specific plugin - including queued messages.
    Does not mark them as recieved. 

    If you wish to preview queued transactions only use the '/transaction-preview' route instead.
    If you wish to actually CONSUME the queue (mark as recieved) use the '/transactions' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR TRANSACTIONS -- ONLY TO VIEW THEIR HISTORY.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """

    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_messages = mongo.db.plugin_messages.find({
        'plugin_entity_id': entity_id,
        'message_name' : "transaction", 
    })

    result = [{
        'message_name': t['message_name'],
        'message': _map_mongo_document(t['message_payload'])
        } for t in my_messages]

    return jsonify({'transaction-history': result})


@app.route("/plugin/message/preview")
def plugin_message_preview():
    """
    SUPPORTS: GET
    Lists the messages and transactions queued for a specific plugin. 
    Does not mark them as recieved. Only shows messagess not marked as received.
    If you wish to see the entire message history for 
    the plugin use the '/message-history' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR MESSAGES -- ONLY TO PREVIEW THEM.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_messages = mongo.db.plugin_messages.find({
        'sent_to_plugin': False,
        'plugin_entity_id': entity_id,
        'message_name' : {"$ne" : "transaction"},
    })

    result = [{
        'message_name': t['message_name'],
        'message': _map_mongo_document(t['message_payload'])
        } for t in my_messages]

    return jsonify({'message-preview': result})


@app.route("/plugin/transaction/preview")
def plugin_transaction_preview():
    """
    SUPPORTS: GET
    Lists the messages and transactions queued for a specific plugin. 
    Does not mark them as recieved. Only shows messagess not marked as received.
    If you wish to see the entire message history for 
    the plugin use the '/message-history' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR MESSAGES -- ONLY TO PREVIEW THEM.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_messages = mongo.db.plugin_messages.find({
        'sent_to_plugin': False,
        'plugin_entity_id': entity_id,
        'message_name' : "transaction",
    })

    result = [{
        'message_name': t['message_name'],
        'message': _map_mongo_document(t['message_payload'])
        } for t in my_messages]

    return jsonify({'transaction-preview': result})


@app.route("/plugin/message/list")
def plugin_message_list():
    """
    SUPPORTS: GET
    List the messages and transactions queued for a specific plugin.

    !!!DANGER!!!: Will mark the messages as recieved by the plugin 
    and they will not show again. If you wish to see a preview
    of the messages queued for a plugin use the /message-preview route instead.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_messages = mongo.db.plugin_messages.find({
        'sent_to_plugin': False,
        'receiver_entity_id': entity_id,
        'message_name' : {"$ne" : "transaction"},
    })

    result = [
        (t['_id'], t['message_id'], t['message_name'], t['sender_entity_id'], _map_mongo_document(t['payload']))
        for t in my_messages
    ]

    update_ids = [t[0] for t in result]
    result = [{
        'message_id': str(t[1]),
        'message_name': t[2],
        'sender_entity_id': t[3],
        'message': t[4]} for t in result]

    mongo.db.plugin_messages.update(
        {'_id':{'$in': update_ids}},
        {"$set": {'sent_to_plugin':True, 'time_received': datetime.now()}}, 
        multi=True
    )

    return jsonify({'messages': result})


@app.route("/plugin/transaction/list")
def plugin_transaction_list():
    """
    SUPPORTS: GET
    List the transactions queued for a specific plugin.

    !!!DANGER!!!: Will mark the transactions as recieved by the plugin 
    and they will not show again. If you wish to see a preview
    of the transactions queued for a plugin use the /transaction-preview route instead.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_messages = mongo.db.plugin_messages.find({
        'sent_to_plugin': False,
        'receiver_entity_id': entity_id,
        'message_name' : "transaction",
    })

    result = [
        (t['_id'], t['message_id'], t['message_name'], t['sender_entity_id'], _map_mongo_document(t['payload']))
        for t in my_messages
    ]

    update_ids = [t[0] for t in result]
    result = [{
        'message_id': str(t[1]),
        'message_name': t[2],
        'sender_entity_id': t[3],
        'message': t[4]} for t in result]

    mongo.db.plugin_messages.update(
        {'_id':{'$in': update_ids}},
        {"$set": {'sent_to_plugin':True}}, 
        multi=True
    )

    return jsonify({'transactions': result})


@csrf.exempt
@app.route("/message", methods=["POST"])
def message():
    """
    SUPPORTS: POST
    Submit a message to the HPIT server. Expect the data formatted as JSON
    with the application/json mimetype given in the headers. Expects two fields in
    the JSON data.

    Accepts: JSON
        - name : string => The name of the message to submit to the server
        - payload : Object => A JSON Object of the DATA to store in the database

    Returns:
        403         - A connection with HPIT must be established first.
        200: JSON   
            - message_id - The ID of the message submitted to the database
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    sender_entity_id = session['entity_id']
    message_name = request.json['name']
    payload = request.json['payload']

    message = {
        'sender_entity_id': sender_entity_id,
        'time_created': datetime.now(),
        'message_name': message_name,
        'payload': payload,
    }

    message_id = mongo.db.messages.insert(message)

    subscriptions = Subscription.query.filter_by(message_name=message_name)

    for subscription in subscriptions:
        plugin_entity_id = subscription.plugin.entity_id

        mongo.db.plugin_messages.insert({
            'message_id': message_id,

            'sender_entity_id': sender_entity_id,
            'receiver_entity_id': plugin_entity_id,

            'time_created': datetime.now(),
            'time_received': datetime.now(),
            'time_responded': datetime.now(),
            'time_response_received': datetime.now(),

            'message_name': message_name,
            'payload': payload,

            'sent_to_plugin': False,
        })

    return jsonify(message_id=str(message_id))


@csrf.exempt
@app.route("/response", methods=["POST"])
def response():
    """
    SUPPORTS: POST
    Submits a response to an earlier message to the HPIT server. 
    Expects the data formatted as JSON with the application/json mimetype 
    given in the headers. Expects two fields in the JSON data.

    Accepts: JSON
        - message_id : string => The message id to the message you're responding to.
        - payload : Object => A JSON Object of the DATA to respond with

    Returns:
        403         - A connection with HPIT must be established first.
        200: JSON   
            - response_id - The ID of the response submitted to the database
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    responder_entity_id = session['entity_id']
    message_id = request.json['message_id']
    payload = request.json['payload']

    plugin_message = mongo.db.plugin_messages.find_one({
        'message_id': ObjectId(message_id),
        'receiver_entity_id': responder_entity_id
    })

    mongo.db.plugin_messages.update(
        {'_id':plugin_message['_id']},
        {"$set": {'time_responded': datetime.now()}}
    )

    response_id = mongo.db.responses.insert({
        'message_id': plugin_message['message_id'],
        'sender_entity_id': responder_entity_id,
        'receiver_entity_id': plugin_message['sender_entity_id'],
        'message': plugin_message,
        'response': payload,
        'response_recieved': False
    })

    return jsonify(response_id=str(response_id))


@app.route("/response/list", methods=["GET"])
def responses():
    """
    SUPPORTS: GET
    Poll for responses queued to original sender of a message.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the responses for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_responses = mongo.db.responses.find({
        'receiver_entity_id': entity_id,
        'response_recieved': False
    })

    result = [
        (t['_id'], _map_mongo_document(t['message']), _map_mongo_document(t['response']))
        for t in my_responses
    ]

    update_ids = [t[0] for t in result]
    result = [{
        'message': t[1],
        'response': t[2]} for t in result]

    mongo.db.responses.update(
        {'_id':{'$in': update_ids}},
        {"$set": {'response_recieved':True, 'time_response_received': datetime.now()}}, 
        multi=True
    )

    return jsonify({'responses': result})
