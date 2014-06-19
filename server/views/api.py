from uuid import uuid4
from bson.objectid import ObjectId
from flask import session, jsonify, abort, request

from server import app, mongo, _map_mongo_document, HPIT_STATUS
from server.models import Plugin, Tutor

def bad_parameter_response(parameter):
    return Response(
        status="Missing parameter: " + parameter,
        status_code=401,
        mimetype="application/json")


def auth_failed_response():
    return Response(
        status="Could not authenticate. Invalid entity_id/api_key combination.",
        status_code=403,
        mimetype="application/json")


def not_found_response():
    return Response(
        status="Could not find the requested resource.",
        status_code=404,
        mimetype="application/json")
   

def ok_response():
    return Response(
        status="OK", 
        status_code=200, 
        mimetype="application/json")

    
@app.route("/version", methods=["GET"])
def version():
    """
    SUPPORTS: GET

    Gets the version of the HPIT server.

    Returns: 200:JSON with the following fields:
        - version : string -> version of HPIT
    """
    version_returned = {"version": HPIT_VERSION}
    return jsonify(version_returned)


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
    Lists the event names for messages this plugin will listen to.
    If you are using the library then this is done under the hood to make sure
    when you perform a poll you are recieving the right messages.

    Returns the event_names as a JSON list.
    """

    def _map_subscriptions(subscription):
        return subscription['name']

    subscriptions = list(mongo.db.plugin_subscriptions.find({'name': name}))
    subscriptions = [_map_subscriptions(sub) for sub in subscriptions]
    return jsonify({'subscriptions': subscriptions})


@app.route("/plugin/<name>/history")
def plugin_message_history(name):
    """
    SUPPORTS: GET
    Lists the message history for a specific plugin - including queued messages.
    Does not mark them as recieved. 

    If you wish to preview queued messages only use the '/preview' route instead.
    If you wish to actually CONSUME the queue (mark as recieved) use the '/messages' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR MESSAGES -- ONLY TO VIEW THEIR HISTORY.

    Returns JSON for the messages.
    """
    my_messagess = mongo.db.plugin_messages.find({
        'plugin_name': name,
    })

    result = [{
        'event_name': t['event_name'],
        'message': _map_mongo_document(t['message_payload'])
        } for t in my_messages]

    return jsonify({'history': result})


@app.route("/plugin/<name>/preview")
def plugin_message_preview(name):
    """
    SUPPORTS: GET
    Lists the messages queued for a specific plugin. 
    Does not mark them as recieved. Only shows messagess not marked as received.
    If you wish to see the entire message history for 
    the plugin use the '/history' route instead.

    DO NOT USE THIS ROUTE TO GET YOUR MESSAGES -- ONLY TO PREVIEW THEM.

    Returns JSON for the messages.
    """
    my_messages = mongo.db.plugin_messages.find({
        'sent_to_plugin': False,
        'plugin_name': name,
    })

    result = [{
        'event_name': t['event_name'],
        'message': _map_mongo_document(t['message_payload'])
        } for t in my_messages]

    return jsonify({'preview': result})


@app.route("/plugin/<name>/messages")
def plugin_messages(name):
    """
    SUPPORTS: GET
    List the messages queued for a specific plugin.

    !!!DANGER!!!: Will mark the messages as recieved by the plugin 
    and they will not show again. If you wish to see a preview
    of the messages queued for a plugin use the /preview route instead.

    Returns JSON for the messages.
    """
    my_messages = mongo.db.plugin_messages.find({
        'sent_to_plugin': False,
        'plugin_name': name,
    })

    result = [
        (t['_id'], t['event_name'], _map_mongo_document(t['message_payload']))
        for t in my_messages
    ]

    update_ids = [t[0] for t in result]
    result = [{
        'event_name': t[1],
        'message': t[2]} for t in result]

    mongo.db.plugin_messages.update(
        {'_id':{'$in': update_ids}},
        {"$set": {'sent_to_plugin':True}}, 
        multi=True
    )

    return jsonify({'messages': result})


@app.route("/message", methods=["POST"])
def message():
    """
    SUPPORTS: POST
    Submit a message to the HPIT server. Expect the data formatted as JSON
    with the application/json mimetype given in the headers. Expects two fields in
    the JSON data.
        - name : string => The name of the event message to submit to the server
        - payload : Object => A JSON Object of the DATA to store in the database

    Returns 200:JSON -> 
        - message_id - The ID of the message submitted to the database
    """
    if 'entity_id' not in session:
        return abort(401)

    name = request.json['name']
    payload = request.json['payload']
    payload['entity_id'] = session['entity_id']
    message_id = mongo.db.messages.insert(payload)

    plugins = mongo.db.plugin_subscriptions.find({'event': name})

    for plugin in plugins:
        mongo.db.plugin_messages.insert({
            'plugin_name': plugin['name'],
            'event_name': name,
            'message_id': message_id,
            'entity_id': session['entity_id'],
            'message_payload': payload,
            'sent_to_plugin': False
        })

    return jsonify(message_id=str(message_id))

@app.route("/response", methods=["POST"])
def response():
    """
    SUPPORTS: POST
    Submits a response to an earlier message to the HPIT server. 
    Expects the data formatted as JSON with the application/json mimetype 
    given in the headers. Expects two fields in the JSON data.
        - message_id : string => The message id to the message you're responding to.
        - payload : Object => A JSON Object of the DATA to respond with

    Returns: 200:JSON ->
        - response_id - The ID of the response submitted to the database
    """
    message_id = request.json['message_id']
    payload = request.json['payload']

    message = mongo.db.messages.find_one({'_id': ObjectId(message_id)})

    response_id = mongo.db.responses.insert({
        'message_id': message_id,
        'message': message,
        'response': payload,
        'response_recieved': False
    })

    return jsonify(response_id=str(response_id))


@app.route("/responses", methods=["GET"])
def responses():
    """
    SUPPORTS: GET
    Poll for responses queued to original sender of a message.

    Returns: JSON encoded list of responses.
    """
    if 'entity_id' not in session:
        return abort(401)

    entity_id = session['entity_id']
    my_responses = mongo.db.responses.find({
        'message.entity_id': entity_id,
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
        {"$set": {'response_recieved':True}}, 
        multi=True
    )

    return jsonify({'responses': result})
