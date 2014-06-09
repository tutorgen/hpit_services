## Todo

In the tutor loop, support not having a main callback.
Add a throttle in the tutor main loop.

## Overview

The HyperPersonalize Intelligent Tutor (HPIT) is an schemaless, event driven system
which specializes in the communication between distributed intelligent tutoring systems 
and specialized, machine learning algorithims, which we call plugins.

HPIT is a next generation system built on the backbone of open source web technologies.

At the most fundemental layer HPIT is a collection of RESTful webservices that assist in
the routing of messages between tutors and plugins. On top of this web services layer 
we have built a client side library in the Python programming language to assist in 
the creation of tutors and plugins and their communcation with HPIT.

HPIT is a publish and subscribe framework using event-driven methodologies. Tutors interact 
with the system by sending messages which consist of a named event and a data payload. 
Plugins can listen to these events, perform an action, then submit a response back to HPIT,
which will ultimately be routed to the tutor that made the original request.

In addition, HPIT packages several baseline plugins which peform basic functions related
to intelligent tutoring systems.

## Understanding Terminology

HPIT - HPIT consists of several modules and is sort of an all encompassing term for the entire 
system of modules.

Tutor - A tutor is an entity that interacts with students and uses the HPIT system to gather 
and analyze intelligent information about student perforamance. A tutor could be a game, or a web application,
a Macromedia Flash game, or some other system that interacts with students in an effort to educate or train.

HPIT Plugin - An HPIT Plugin is a module that specializes in a very specific and narrow band of responsibility.
A plugin may exist inside of HPIT itself(at TutorGen) or on a network or system outside of HPIT. Regardless of
where the plugin sits it must communicate with the central HPIT router/server.

HPIT Manager - The manager is used to load the HPIT router, and a set of plugins and tutors. It
is used primarily for testing and development.

HPIT Router/Server - This is the central server that routes messages and transactions between tutors
and plugins.

HPIT Message - This is a event_name and payload pair, both of which are defined by the developer for
their plugin.

HPIT Transaction - A transaction is a message specifically for DataShop transactions.

## Getting started

HPIT requires Python 3.4. Make sure that you have this version of Python installed and
linked into your PATH. Most systems that come with Python have Python 2.7x branch installed.
You may need to install Python3.4 manually to get started depending on your operating system.

You can check your version of Python by typing: `python --version` or `python3 --version`

Once you have the right version of Python installed you should also have `virtualenv` 
and `pip` installed as well. If you are unfamiliar with either of these libraries I highly 
encourage you research them, as they will make working with HPIT much simpler.

Once you have pip and virtualenv installed you will need to install mongodb. 
- On ubuntu type: `sudo apt-get install mongodb` On Mac with Brew install mongodb with: `brew install mongodb`
- On Windows, installation binaries are available from mongodb.org

Then you can begin installalling HPIT by:

1. Changing to the directory where you have downloaded hpit with: `cd /path/to/project`
2. Creating a new virtual environment with: `virtualenv my_environment`
3. Activating that environment with: `source my_environment/bin/activate`
4. Installing HPIT's dependencies with: `pip install -r requirements.txt`
5. Run the test suite by typing `python manager.py test`
6. Start the MongoDB instance with `mongod`

To start the HPIT server type: `python3 manager.py start` and open your browser 
to http://127.0.0.1:8000.

## The HPIT Manager

The HPIT Manager can be used to quickly launch an HPIT server, configure plugins and tutors,
and monitor how data is being passed between entities within the HPIT system.

The HPIT manager can be run by typing: `python3 manager.py <command> <command_args>`

Depending on the command you wish to run the arguments to that command will vary. The command
line manager for HPIT will help you along the way. For example typing just `python3 manager.py`
will give you a list of commands that manager understands. Then typing 
`python3 manager.py your_command` will show you the arguments that that command can take and a
brief overview of what that command does.

Currently the HPIT Manager has the following commands:
- `python3 manager.py start` will start the HPIT server, all locally configured tutors, and all locally configured plugins.
- `python3 manager.py stop` will stop the HPIT server, all locally configured tutors, and all locally configured plugins.
- `python3 manager.py status` will show you whether or not the HPIT server is currently running.
- `python3 manager.py add plugin <name> <subtype>` will help you create plugins with the specified name and subtype.
- `python3 manager.py remove plugin <name>` will help you remove plugins with the specified name.
- `python3 manager.py add tutor <name> <subtype>` will help you create tutors with the specified name and subtype.
- `python3 manager.py remove tutor <name>` will help you remove tutors with the specified name.

## The tutor and plugin configuration

The goals behind the HPIT manager is to give TutorGen a way to create and destory large 
amount of entities for testing and evaluation of the software. Creating a new hpit 
entity (tutor/plugin) adds it to the 'configuration.json'. Removing an hpit entity 
removes it from the 'configuration.json' file. All entities within the configuration specify
4 things: 

    1. Whether it is a tutor or plugin (by virtue of being in the tutor or plugin list)
    2. active - Whether the plugin is currently running. (True if it is)
    3. name - The name of the entity. This is how the entity will register itself with HPIT.
    4. type - The subtype of the entity. e.g. 'example' or 'knowledge_tracer'

You normally will not need to edit this file by hand. It is recommended that you change the
configuration with the `python3 manager.py` add and remove commands instead.

## Settings for Clients and Servers

Both clients (tutors and plugins) and the server may need configuration.  The settings files
are clients/settings.py and server/settings.py, for clients and servers, respectively.  

clients/settings.py currently contains the following options:
- HPIT_URL_ROOT : the URL root where the HPIT server lives

server/settings.py currently contains the following options:
- HPIT_PID_FILE : the location where the PID file of the server is stored, for tracking the server process
- HPIT_BIND_IP : the IP address the server is listening on
- HPIT_BIND_PORT : the port that the HPIT server listens on
- HPIT_VERSION : the version of this server

## Database Structure

The HPIT server uses a NoSQL MongoDB database to manage its messages and transactions.  MongoDB uses a 
lazy creation policy, so the database and its collections are created only after elements are inserted,
and can be created with no prior configuration.  The database contains five core collections:

### messages
A list of messages sent to the system before being duplicated to plugin_messages
It contains the following fields:
entity_id: "The session ID of the sender"
payload: "The data being sent."

### plugin_subscriptions
Maps the event names to the names of plugins that are actively listening for them.
It contains the following fields:
- name: "plugin name"
- event: "event name"

### plugin_messages
Contains messages sent to plugins, as copied from the messages collection.
It contains the following fields:
- plugin_name: "name of destination plugin"
- event_name: "name of event"
- message_id: "the ID of this message"
- message_payload: "The data contained in this message."
- sent_to_plugin: "Boolean if it has been processed or not"

### responses
Stores responses for tutors or other plugins to poll.
It contains the following fields:
- response_received: "Boolean if it has been processed or not"
- response: "data for this response"
- message_id: "the id of the original sent message"
- message: "the original message"

### sessions
Stores session data for plugins and tutors. 

## The HPIT Server in depth

The HPIT Server is nothing more than an event-driven publish and subscribe framework, built
specifically to assist plugins and tutors to communicate via RESTful webserver. It is 
schemaless, has no pre-defined events, and is agnostic to the kinds of data it routes 
between plugins and tutors. In additon HPIT provides fundemental support for sessions,
authentication, message routing, and entity tracking.

Anyone can wrap these RESTful webservices in a client side library and will be able to interact
with HPIT. We have delivered a client side library written in Python.

The server supports a variety of routes to handle the connection, polling, and transfer of 
data between HPIT entities.

---

### /plugin/disconnect
SUPPORTS: POST

Destroys the session for the plugin calling this route.

Returns: 200:OK

### /tutor/disconnect
SUPPORTS: POST

Destroys the session for the tutor calling this route.

Returns: 200:OK

### /message
SUPPORTS: POST
Submit a message to the HPIT server. Expect the data formatted as JSON
with the application/json mimetype given in the headers. Expects two fields in
the JSON data.
- name : string => The name of the event message to submit to the server
- payload : Object => A JSON Object of the DATA to store in the database

Returns 200:JSON -> 
- message_id - The ID of the message submitted to the database

### /responses
SUPPORTS: GET
Poll for responses queued to original sender of a message.

Returns: JSON encoded list of responses.

### /response
SUPPORTS: POST
Submits a response to an earlier message to the HPIT server. 
Expects the data formatted as JSON with the application/json mimetype 
given in the headers. Expects two fields in the JSON data.
- message_id : string => The message id to the message you're responding to.
- payload : Object => A JSON Object of the DATA to respond with

Returns: 200:JSON ->
- response_id - The ID of the response submitted to the database

### /
SUPPORTS: GET
Shows the status dashboard and API route links for HPIT.

### /plugin/\name\/unsubscribe/\event\
SUPPORTS: POST

Stop listening to an event type for a specific plugin with
the name .

Returns: 200:OK or 200:DOES_NOT_EXIST

### /plugin/\name\/subscribe/\event\
SUPPORTS: POST

Start listening to an event type for a specific plugin with
the name .

Returns: 200:OK or 200:EXISTS

### /plugin/connect/\name\
SUPPORTS: POST

Establishes a plugin session with HPIT.

Returns: 200:JSON with the following fields:
- entity_name : string -> Assigned entity name (not unique)
- entity_id : string -> Assigned entity id (unique)
Both assignments expire when you disconnect from HPIT.

### /plugin/\name\/subscriptions
SUPPORTS: GET
Lists the event names for messages this plugin will listen to.
If you are using the library then this is done under the hood to make sure
when you perform a poll you are recieving the right messages.

Returns the event_names as a JSON list.

### /plugin/\name\/messages
SUPPORTS: GET
List the messages queued for a specific plugin.

!!!DANGER!!!: Will mark the messages as recieved by the plugin 
and they will not show again. If you wish to see a preview
of the messages queued for a plugin use the /preview route instead.

Returns JSON for the messages.

### /plugin/\name\/history
SUPPORTS: GET
Lists the message history for a specific plugin - including queued messages.
Does not mark them as recieved. 

If you wish to preview queued messages only use the '/preview' route instead.
If you wish to actually CONSUME the queue (mark as recieved) use the '/messages' route instead.

DO NOT USE THIS ROUTE TO GET YOUR MESSAGES -- ONLY TO VIEW THEIR HISTORY.

Returns JSON for the messages.

### /plugin/\name\/preview
SUPPORTS: GET
Lists the messages queued for a specific plugin. 
Does not mark them as recieved. Only shows messages not marked as received.
If you wish to see the entire message history for 
the plugin use the '/history' route instead.

DO NOT USE THIS ROUTE TO GET YOUR MESSAGES -- ONLY TO PREVIEW THEM.

Returns JSON for the messages.

### /tutor/connect/\name\
SUPPORTS: POST

Establishes a tutor session with HPIT.

Returns: 200:JSON with the following fields:
- entity_name : string -> Assigned entity name (not unique)
- entity_id : string -> Assigned entity id (unique)
Both assignments expire when you disconnect from HPIT.

## Tutors in depth

A Tutor is an HPIT entity that can send messages to HPIT. A message consists of
an event name and a payload. The event name is an arbitrary string that defines what is in
the payload. Plugins register to listen to messages based on the event name. The 
message payload is an arbitrary JSON like document with data formatted based on plugin
requirements. The kinds of messages a tutor can send is definied by the plugins 
currently registered with HPIT. The HPIT server itself does not define what these 
messages look like, however HPIT does package some plugins as part of it's architecture.

For example the HPIT basic knowledge tracing plugin supports the following three events:
* kt_set_initial - Sets the initial values for the knowledge tracer on the KT Skill.
* kt_trace - Performs a knowledge tracing operation on the KT Skill.
* kt_reset - Resets the inital values for the knowledge tracer on the KT Skill.

Depending on the event name(eg kt_set_initial, or kt_trace) the payload the plugin expects will be different.

Tutors may also listen to plugin responses, and respond to them. Plugins may or may not
send a response depending on the plugin.

## Plugins in depth

A Plugin is an HPIT entity that subscribes to (listens to) certain event names, recieves
transcation payloads, perfoms some arbitrary function based on the event and message
payload, and may or may not return a response to the original sender of the message.

A plugin may listen to and define any events it wishes. When a tutor sends a transcation
to HPIT, if a plugin has registered itself with HPIT, and if that plugin and subscribed
to the event name submitted with the tutor's transcation it will recieve a queued list
of messages when it polls the HPIT server for data. It is expected that plugins will
do this type of polling periodically to see if any messages have been queued for 
processing by HPIT.

When a plugin processes an event from HPIT, it will recieve all the information in the 
original message, including the information identifying the tutor that sent the
message. This identifying information is called the entity_id of the tutor.

A plugin may send a response to HPIT by providing the original message id, along with 
a response payload, which will be sent to the original sender of the message message.

It is possible for plugins to send messages like tutors and respond to messages
like tutors. In this way, it is possible for plugins to listen to, and refire event 
messages while altering the event name of the message so that other dependent 
plugins can also respond to the original trasaction. This can create a daisy chaining
effect where plugins fire in series to process a complex series of messages.

## Packaged Plugins

### Example Plugin

The example plugin listens to the `test` and `example` event names and logs
whatever data it's sent in the payload to a file.

### Knowledge Tracing Plugin
#### kt_set_initial
Sets the initial probabilistic values for the knowledge tracer.

Recieves:

* entity_id: string - An identifier for the sender. (Defined by the HPIT Server)
* skill : string - String identifier for the skill.
* probability_known : float (0.0-1.0) - Probability the skill is already known
* probability_learned : float (0.0-1.0) - Probability the skill will be learned
* probability_guess : float (0.0-1.0) - Probability the answer is a guess
* probability_mistake : float (0.0-1.0) - Probability the student made a mistake (but knew the skill)

Returns:
* skill : string - String identifier for the skill.
* probability_known : float (0.0-1.0) - Probability the skill is already known
* probability_learned : float (0.0-1.0) - Probability the skill will be learned
* probability_guess : float (0.0-1.0) - Probability the answer is a guess
* probability_mistake : float (0.0-1.0) - Probability the student made a mistake (but knew the skill)

#### kt_reset
Resets the probabilistic values for the knowledge tracer.

Recieves:
* entity_id: string - An identifier for the sender. (Defined by the HPIT Server)
* skill : string - String identifier for the skill.

Returns:
* skill : string - String identifier for the skill.
* probability_known : 0.0 - Probability the skill is already known
* probability_learned : 0.0 - Probability the skill will be learned
* probability_guess : 0.0 - Probability the answer is a guess
* probability_mistake : 0.0 - Probability the student made a mistake (but knew the skill)

#### kt_trace
Runs a knowledge tracing algorithm on the skill/tutor combination and returns the result.

Recieves:
* entity_id: string - An identifier for the sender. (Defined by the HPIT Server)
* skill : string - String identifier for the skill.
* correct: boolean - True if correct. False if not.

Returns:
* skill : string - String identifier for the skill.
* probability_known : float (0.0-1.0) - Probability the skill is already known
* probability_learned : float (0.0-1.0) - Probability the skill will be learned
* probability_guess : float (0.0-1.0) - Probability the answer is a guess
* probability_mistake : float (0.0-1.0) - Probability the student made a mistake (but knew the skill)

### Student Management Plugin

### Skill Management Plugin

### Problem Management Plugin

#### add_problem
Adds a problem to the problem manager.

Recieves:
* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* problem_name : string - The name of the problem.
* problem_text : string - Text for the problem.

Returns:
* problem_name : string - The problem name.
* problem_text : string - The problem's text.
* success : boolean - True if the data was saved to the database.
* updated : boolean - True if the data was updated (the record already existed)

#### remove_problem
Remove a problem from the problem manager.

Recieves:
* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* problem_name : string - The name of the problem.

Returns:
* problem_name : string - The name of the problem that was removed.
* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed and was deleted.

#### get_problem
Gets a previously stored problem from the problem manager.

Recieves:
* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* problem_name : string - The name of the problem to retrieve.

Returns:
* problem_name : string - The name of the problem.
* problem_text : string - The text of the problem.
* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed.

#### list_problems
Get all the problems for a given entity.

Recieves:
* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)

Returns:
* problems : list - A list of problems with
    * problem_name : string - The name of the problem.
    * problem_text : string - The text of the problem.
* success : True - Always returns True

### Problem Step Management Plugin

#### add_problem_step
Adds a problem step to the problem step manager.

Recieves:
* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* problem_name : string - The name of the problem.
* problem_step_name : string - The name of the problem step.
* problem_step_text : string - The text of the problem step.

Returns:
* problem_name : string - The problem name.
* problem_step_name : string - The name of the problem step.
* problem_step_text : string - The text of the problem step.
* success : boolean - True if the data was saved to the database.
* updated : boolean - True if the data was updated (the record already existed)

#### remove_problem_step
Remove a problem step from the problem step manager.

Recieves:
* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* problem_name : string - The name of the problem.
* problem_step_name : string - The name of the problem step.

Returns:
* problem_name : string - The name of the problem.
* problem_step_name : string - The name of the problem that was removed.
* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed and was deleted.

#### get_problem_step
Gets a previously stored problem step from the problem step manager.

Recieves:
* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* problem_step_name : string - The name of the problem step.
* problem_name : string - The name of the problem to retrieve.

Returns:
* problem_name : string - The name of the problem.
* problem_step_name : string - The name of the problem step.
* problem_step_text : string - The text of the problem step.
* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed.

#### list_problem_steps
Get all the problems for a given problem and entity. If the problem name is specified
returns all problem steps for the given problem_name. If the problem_name is NOT 
specified, returns all the problem steps for the given entity.

Recieves:
* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* (optional) problem_name : string - The name of the problem.

Returns:
* problem_steps : list - A list of problems with
    * problem_step : string - The name of the problem.
    * problem_step_name : string - The name of the problem step.
    * problem_step_text : string - The text of the problem step.
* success : True - Always returns True

### Data Storage Plugin

## Tech Stack

HPIT exclusively uses Open Source Technologies. Currently our tech stack consists 
of the following:

- Python 3.4
- Flask
- Flask-PyMongo
- Jinja2
- PyMongo
- MongoDB
- Daemonize
- Requests
- Gunicorn

Information about specific versions can be found inside of requirements.txt

## License

HPIT is as of yet, unlicensed technology. It is a joint project between Carnegie Learning, 
TutorGen, Inc., and Advanced Distributed Learning. As of this original writing, the 
understood intention is to license this technology under a permissive Open Source License 
such as the BSD or MIT License. The final decision on how to license the technology has 
yet to be determined and this software should be thought of as proprietary in nature.
