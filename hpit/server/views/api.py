from uuid import uuid4
from bson.objectid import ObjectId
from datetime import datetime
from flask import session, jsonify, abort, request, Response
import uuid

from hpit.server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app
mongo = app_instance.mongo
db = app_instance.db
csrf = app_instance.csrf

from hpit.server.models import Plugin, Tutor, Subscription, MessageAuth, ResourceAuth

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()

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

def user_verified(message_name,plugin):
    if "." in message_name:
        message_parts = message_name.split(".")
        company_name = plugin.user.company.replace(" ","_").lower()
        if message_parts[0] == company_name:
            return True
        else:
            return False
    else:
        return True
        
        
    

def bad_parameter_response(parameter):
    return ("Missing parameter: " + parameter, 401, dict(mimetype="application/json"))

def auth_failed_response(message="Could not authenticate. Invalid entity_id/api_key combination."):
    return (message,403, dict(mimetype="application/json"))

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
    session['token'] = str(uuid.uuid4())

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
        return bad_parameter_response('log_entry')

    if 'entity_id' not in session:
        return auth_failed_response()

    mongo.db.entity_log.insert({
        'entity_id': session['entity_id'],
        'session_token': session["token"],
        'log_entry': request.json['log_entry'],
        'created_on': datetime.now().isoformat(),
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
        return bad_parameter_response('message_name')

    if 'entity_id' not in session:
        return auth_failed_response()

    message_name = request.json['message_name']
    entity_id = session['entity_id']         

    plugin = Plugin.query.filter_by(entity_id=entity_id).first()

    if not plugin:
        return not_found_response()
        
    #message auth
    message_auth = MessageAuth.query.filter_by(message_name=message_name).first()
    if not message_auth: #this will be the owner
        if user_verified(message_name,plugin):
            new_message_auth = MessageAuth()
            new_message_auth.entity_id = str(entity_id)
            new_message_auth.message_name = message_name
            new_message_auth.is_owner = True
            db.session.add(new_message_auth)
            db.session.commit()
        else:
            return jsonify({"error":"invalid message name"})

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
        return bad_parameter_response('message_name')

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
    Lists the messages that were previously sent to the entity.

    !!! IMPORTANT - Does not mark the messages as received. 

    If you wish to preview queued messages only use the '/message-preview' route instead.
    If you wish to actually CONSUME the queue (mark as received) use the '/messages' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR MESSAGES -- ONLY TO VIEW THEIR HISTORY.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_messages = mongo.db.sent_messages_and_transactions.find({
        'receiver_entity_id': entity_id,
        'message_name': {"$ne" : "transaction"}
    })
    
    def is_auth(mname,eid):
        message_auth = MessageAuth.query.filter_by(message_name=mname,entity_id=str(entity_id)).first()
        if not message_auth:
            return False
        else:
            return True
    
    my_messages = [m for m in my_messages if is_auth(m["message_name"],entity_id)]

    result = [{
        'message_name': t['message_name'],
        'message': _map_mongo_document(t['payload'])
        } for t in my_messages]

    return jsonify({'message-history': result})

    
@app.route("/plugin/transaction/history")
def plugin_transaction_history():
    """
    SUPPORTS: GET
    Lists the messages that were previously sent to the entity.

    If you wish to preview queued transactions only use the '/transaction-preview' route instead.
    If you wish to actually CONSUME the queue (mark as received) use the '/transactions' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR TRANSACTIONS -- ONLY TO VIEW THEIR HISTORY.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """

    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    my_messages = mongo.db.sent_messages_and_transactions.find({
        'receiver_entity_id': entity_id,
        'message_name': "transaction"
    })

    result = [{
        'message_name': t['message_name'],
        'message': _map_mongo_document(t['payload'])
        } for t in my_messages]

    return jsonify({'transaction-history': result})


@app.route("/plugin/message/preview")
def plugin_message_preview():
    """
    SUPPORTS: GET
    Lists the messages and transactions queued for a specific plugin. 
    Does not mark them as received. Only shows messagess not marked as received.
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
        'receiver_entity_id': entity_id,
    })
    
    def is_auth(mname,eid):
        message_auth = MessageAuth.query.filter_by(message_name=mname,entity_id=str(entity_id)).first()
        if not message_auth:
            return False
        else:
            return True
    
    my_messages = [m for m in my_messages if is_auth(m["message_name"],entity_id)]

    result = [{
        'message_name': t['message_name'],
        'message': _map_mongo_document(t['payload'])
        } for t in my_messages]

    return jsonify({'message-preview': result})


@app.route("/plugin/transaction/preview")
def plugin_transaction_preview():
    """
    SUPPORTS: GET
    Lists the messages and transactions queued for a specific plugin. 
    Does not mark them as received. Only shows messagess not marked as received.
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

    my_messages = mongo.db.plugin_transactions.find({
        'receiver_entity_id': entity_id,
    })

    result = [{
        'message_name': t['message_name'],
        'message': _map_mongo_document(t['payload'])
        } for t in my_messages]

    return jsonify({'transaction-preview': result})


@app.route("/plugin/message/list")
def plugin_message_list():
    """
    SUPPORTS: GET
    List the messages and transactions queued for a specific plugin.

    !!!DANGER!!!: Will mark the messages as received by the plugin 
    and they will not show again. If you wish to see a preview
    of the messages queued for a plugin use the /message-preview route instead.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    plugin = Plugin.query.filter_by(entity_id=entity_id).first()

    if not plugin:
        return not_found_response()

    plugin.time_last_polled = datetime.now()
    db.session.add(plugin)
    db.session.commit()

    my_messages = mongo.db.plugin_messages.find({
        'receiver_entity_id': entity_id,
    })

    my_messages = list(my_messages)

   
    def is_auth(mname,eid):
        message_auth = MessageAuth.query.filter_by(message_name=mname,entity_id=str(entity_id)).first()
        if not message_auth:
            return False
        else:
            return True
    
    my_messages = [m for m in my_messages if is_auth(m["message_name"],entity_id)]
    
            
    result = [
        (t['_id'], t['message_id'], t['message_name'], t['sender_entity_id'],t['time_created'],_map_mongo_document(t['payload']))
        for t in my_messages
    ]

    to_remove = [t[0] for t in result]
    result = [{
        'message_id': str(t[1]),
        'message_name': t[2],
        'sender_entity_id': t[3],
        'time_created':t[4],
        'message': t[5]} for t in result]

    #Move sent messages to another collection.
    if my_messages:
        for t in my_messages:
            app.logger.debug("message routed: " + t["message_name"] + " " + str(t["message_id"]) + " " + str(datetime.now()))
            t['time_received'] = datetime.now() 

        mongo.db.sent_messages_and_transactions.insert(my_messages)

        mongo.db.plugin_messages.remove({
            '_id': {'$in': to_remove}
        })

    return jsonify({'messages': result})


@app.route("/plugin/transaction/list")
def plugin_transaction_list():
    """
    SUPPORTS: GET
    List the transactions queued for a specific plugin.

    !!!DANGER!!!: Will mark the transactions as received by the plugin 
    and they will not show again. If you wish to see a preview
    of the transactions queued for a plugin use the /transaction-preview route instead.

    Returns: 
        403         - A connection with HPIT must be established first.
        200:OK      - A JSON list of dicts of the messages for this plugin.
    """
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    plugin = Plugin.query.filter_by(entity_id=entity_id).first()

    if not plugin:
        return not_found_response()

    plugin.time_last_polled = datetime.now()
    db.session.add(plugin)
    db.session.commit()

    my_messages = mongo.db.plugin_transactions.find({
        'receiver_entity_id': entity_id,
    })

    my_messages = list(my_messages)

    result = [
        (t['_id'], t['message_id'], t['message_name'], t['sender_entity_id'],t['time_created'], _map_mongo_document(t['payload']))
        for t in my_messages
    ]

    to_remove = [t[0] for t in result]
    result = [{
        'message_id': str(t[1]),
        'message_name': t[2],
        'sender_entity_id': t[3],
        'time_created':t[4],
        'message': t[5]} for t in result]

    #Move sent transactions to another collection.
    if my_messages:
        for t in my_messages:
            t['time_received'] = datetime.now() 
        mongo.db.sent_messages_and_transactions.insert(my_messages)

        mongo.db.plugin_transactions.remove({
            '_id': {'$in': to_remove}
        })

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
        
    for x in ['name', 'payload']:
        if x not in request.json:
            return bad_parameter_response(x)

    sender_entity_id = session['entity_id']
    message_name = request.json['name']
    if message_name== "transaction":
        return bad_parameter_response("name")
        
    payload = request.json['payload']

    message = {
        'sender_entity_id': sender_entity_id,
        'session_token':session["token"],
        'time_created': datetime.now(),
        'message_name': message_name,
        'payload': payload,
    }     

    message_id = mongo.db.messages_and_transactions.insert(message)

    subscriptions = Subscription.query.filter_by(message_name=message_name)

    for subscription in subscriptions:
        plugin_entity_id = subscription.plugin.entity_id

        
        mongo.db.plugin_messages.insert({
            'message_id': message_id,

            'sender_entity_id': sender_entity_id,
            'session_token':session["token"],
            'receiver_entity_id': plugin_entity_id,

            'time_created': datetime.now(),

            'message_name': message_name,
            'payload': payload
        })

    app.logger.debug("message received: " + message_name + " " + str(message_id) + " " + str(datetime.now()))
    
    return jsonify(message_id=str(message_id))

@csrf.exempt
@app.route("/transaction", methods=["POST"])
def transaction():
    """
    SUPPORTS: POST
    Submit a transaction to the HPIT server. Expect the data formatted as JSON
    with the application/json mimetype given in the headers. Expects two fields in
    the JSON data.

    Accepts: JSON
        - payload : Object => A JSON Object of the DATA to store in the database

    Returns:
        403         - A connection with HPIT must be established first.
        200: JSON   
            - message_id - The ID of the message submitted to the database
    """
    if 'entity_id' not in session:
        return auth_failed_response()
        
    if "payload" not in request.json:
        return bad_parameter_response("payload")

    sender_entity_id = session['entity_id']
    message_name = "transaction"
        
    payload = request.json['payload']

    message = {
        'sender_entity_id': sender_entity_id,
        'session_token':session["token"],
        'time_created': datetime.now(),
        'message_name': message_name,
        'payload': payload,
    }     

    message_id = mongo.db.messages_and_transactions.insert(message)

    subscriptions = Subscription.query.filter_by(message_name=message_name)

    for subscription in subscriptions:
        plugin_entity_id = subscription.plugin.entity_id

        mongo.db.plugin_transactions.insert({
            'message_id': message_id,
            'sender_entity_id': sender_entity_id,
            'session_token':session["token"],
            'receiver_entity_id': plugin_entity_id,

            'time_created': datetime.now(),

            'message_name': message_name,
            'payload': payload
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
        
    for x in ['message_id', 'payload']:
        if x not in request.json:
            return bad_parameter_response(x)

    responder_entity_id = session['entity_id']
    message_id = request.json['message_id']
    payload = request.json['payload']

    plugin_message = mongo.db.sent_messages_and_transactions.find_one({
        'message_id': ObjectId(message_id),
        'receiver_entity_id': responder_entity_id,
    })

    if not plugin_message:
        return not_found_response()

    mongo.db.sent_messages_and_transactions.update(
        {'_id': plugin_message['_id']},
        {"$set": {'time_responded': datetime.now()}}
    )

    response_id = mongo.db.responses.insert({
        'message_id': plugin_message['message_id'],
        'session_token':plugin_message["session_token"],
        'sender_entity_id': responder_entity_id,
        'receiver_entity_id': plugin_message['sender_entity_id'],
        'message': plugin_message,
        'response': payload
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

    entity = Plugin.query.filter_by(entity_id=entity_id).first()

    if not entity:
        entity = Tutor.query.filter_by(entity_id=entity_id).first()

    if not entity:
        return not_found_response()

    entity.time_last_polled = datetime.now()
    db.session.add(entity)
    db.session.commit()

    my_responses = mongo.db.responses.find({
        'receiver_entity_id': entity_id,
        'session_token':session["token"],
    })
    
    def is_auth(r):
        if "resource_id" in r["response"]:
            ra = ResourceAuth.query.filter_by(entity_id=r["receiver_entity_id"],resource_id=r["response"]["resource_id"]).first()
            if not ra:
                return False
            else:
                return True
        else:
            return True
            
    my_responses = [r for r in my_responses if is_auth(r)]

    my_responses = list(my_responses)

    result = [
        (t['_id'], _map_mongo_document(t['message']), _map_mongo_document(t['response']))
        for t in my_responses
    ]

    to_remove = [t[0] for t in result]
    result = [{
        'message': t[1],
        'response': t[2]} for t in result]

    #Move sent responses to another collection.
    if my_responses:
        for t in my_responses:
            t['time_response_received'] = datetime.now()
        mongo.db.sent_responses.insert(my_responses)

        mongo.db.responses.remove({
            '_id': {'$in': to_remove}
        })

    return jsonify({'responses': result})
 
"""
@csrf.exempt
@app.route("/message-auth", methods=["POST"])
def message_auth():
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    entity = Plugin.query.filter_by(entity_id=entity_id).first()
    
    if "message_name" not in request.json:
        return bad_parameter_response("message_name")
    if "other_entity_id" not in request.json:
        return bad_parameter_response("other_entity_id")
    
    message_name = request.json["message_name"]
    other_entity_id = request.json["other_entity_id"]
        
    message_auth = MessageAuth.query.filter_by(message_name=message_name,entity_id=str(entity_id),is_owner=True).first()
    if not message_auth:
        return jsonify({"error":"not authorized to complete action"})
    else:
        existing_message_auth = MessageAuth.query.filter_by(message_name=message_name,entity_id=str(other_entity_id),is_owner=False).first()
        if not existing_message_auth:
            new_message_auth = MessageAuth()
            new_message_auth.entity_id = str(other_entity_id)
            new_message_auth.message_name = message_name
            new_message_auth.is_owner = False
            db.session.add(new_message_auth)
            db.session.commit()
        return ok_response()
"""

@app.route("/message-owner/<message_name>", methods=["GET"])
def message_owner(message_name):
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']

    message_auth = MessageAuth.query.filter_by(message_name=message_name,is_owner=True).first()
    if not message_auth:
        return not_found_response()
    else:
        return  jsonify({"owner":message_auth.entity_id})


@csrf.exempt
@app.route("/share-message", methods=["POST"])
def share_message():
    if 'entity_id' not in session:
        return auth_failed_response()

    entity_id = session['entity_id']
    
    if "message_name" not in request.json:
        return bad_parameter_response("message_name")
    if "other_entity_ids" not in request.json:
        return bad_parameter_response("other_entity_ids")
    
    message_name = request.json["message_name"]
    other_entity_ids = request.json["other_entity_ids"]
    
    if isinstance(other_entity_ids,str):
        other_entity_ids = [other_entity_ids]
    elif not isinstance(other_entity_ids,list):
        return bad_parameter_response("other_entity_ids")
    
    message_auth = MessageAuth.query.filter_by(message_name=message_name,entity_id=str(entity_id),is_owner=True).first()
    if not message_auth:
        return jsonify({"error":"not owner"})
    else:
        for eid in other_entity_ids:
            existing_message_auth = MessageAuth.query.filter_by(message_name=message_name, entity_id=str(eid)).first()
            if not existing_message_auth:
                new_message_auth = MessageAuth()
                new_message_auth.entity_id = str(eid)
                new_message_auth.message_name = message_name
                new_message_auth.is_owner = False
                db.session.add(new_message_auth)
                db.session.commit()
                
        return ok_response()


@csrf.exempt
@app.route("/new-resource", methods=["POST"])
def new_resource():
    if 'entity_id' not in session:
        return auth_failed_response()
        
    if "owner_id" not in request.json:
        return bad_parameter_response("owner_id")
        
    owner_id = request.json["owner_id"]    
    
    new_id =  str(uuid.uuid4())
    
    new_resource_auth = ResourceAuth()
    new_resource_auth.entity_id = owner_id
    new_resource_auth.is_owner = True
    new_resource_auth.resource_id = new_id
    
    db.session.add(new_resource_auth)
    db.session.commit()
    
    return jsonify({"resource_id":new_id})
       
 
@csrf.exempt
@app.route("/share-resource", methods=["POST"])
def share_resource():
    if 'entity_id' not in session:
        return auth_failed_response()
    
    entity_id = session['entity_id']
    
    if "resource_id" not in request.json:
        return bad_parameter_response("resource_id")
    if "other_entity_ids" not in request.json:
        return bad_parameter_response("other_entity_ids")
        
    resource_id = request.json["resource_id"]
    other_entity_ids = request.json["other_entity_ids"]
        
    if isinstance(other_entity_ids,str):
        other_entity_ids = [other_entity_ids]
    elif not isinstance(other_entity_ids,list):
        return bad_parameter_response("other_entity_ids")
    
    resource_auth = ResourceAuth().query.filter_by(entity_id=entity_id,is_owner=True,resource_id=resource_id).first()
    
    if not resource_auth:
        return jsonify({"error":"not owner"})
    else:
        for eid in other_entity_ids:
            existing_resource_auth = ResourceAuth().query.filter_by(entity_id=eid,resource_id=resource_id).first()
            if not existing_resource_auth:
                new_resource_auth = ResourceAuth()
                new_resource_auth.entity_id = eid
                new_resource_auth.resource_id = resource_id
                new_resource_auth.is_owner = False
                db.session.add(new_resource_auth)
                db.session.commit()
    
        return ok_response()
    
    
