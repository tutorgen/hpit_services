## Overview

The HyperPersonalized Intelligent Tutor (HPIT) is a schemaless, event driven system
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

In addition, HPIT provides several baseline plugins which peform basic functions related
to intelligent tutoring systems.

## Understanding Terminology

HPIT - HPIT consists of several modules and is sort of an all encompassing term for the entire 
system of modules.

Tutor - A tutor is an entity that interacts with students and uses the HPIT system to gather 
and analyze intelligent information about student perforamance. A tutor could be a game, or a web application,
a Flash game, or some other system that interacts with students in an effort to educate or train.

HPIT Plugin - An HPIT Plugin is a module that specializes in a very specific and narrow band of responsibility.
A plugin may exist inside of HPIT itself(at TutorGen) or on a network or system outside of HPIT. Regardless of
where the plugin sits it must communicate with the central HPIT router/server.

HPIT Manager - The manager is used to load the HPIT router, and a set of plugins and tutors. It
is used primarily for testing and development.

HPIT Router/Server - This is the central server that routes messages and transactions between tutors
and plugins.

HPIT Message - This is a event_name and payload pair, both of which are defined by the developer for
their plugin.

HPIT Transaction - A transaction is a message specifically for PSLC DataShop transactions.

## Getting started

### Python Requirements

HPIT requires Python 3.4. Make sure that you have this version of Python installed and
linked into your PATH. Most systems that come with Python have Python 2.7x branch installed.
You may need to install Python3.4 manually to get started depending on your operating system.

You can check your version of Python by typing: `python --version` or `python3 --version`

Once you have the right version of Python installed you should also have `virtualenv` 
and `pip` installed as well. If you are unfamiliar with either of these libraries I highly 
encourage you research them, as they will make working with HPIT much simpler.

Once you have pip and virtualenv installed you will need to install mongodb and sqlite3.
- On Ubuntu: `sudo apt-get install mongodb sqlite` 
- On Mac OSX with HomeBrew: `brew install mongodb sqlite`. 
- On Windows: installation binaries are available from http://www.mongodb.org and http://www.sqlite.org/download.html

### Production Considerations

If installing in PRODUCTION ONLY you should use PostgreSQL rather than SQLite3.
- On Ubuntutype: `sudo apt-get install postgresql-server`
- On Mac OSX: We recommend you install postgres using Postgres.app found here: http://postgresapp.com/
- On Windows: Installation binaries are available from http://www.postgresql.com

It is assumed that if you are installing this in a PRODUCTION ONLY environment, that you have experience with PostgreSQL. If not,
then please read the tutorial here: http://www.postgresql.org/docs/9.3/static/tutorial.html In general you will need to 
configure some security settings in postgres, create a database, then create login roles for that database. PostgreSQL by 
default does not make itself discoverable, or connectible from outside the local machine. If it is installed in a location
other than where you are installing HPIT you'll need to configure iptables, postgresql.conf and hba.conf in your postgreSQL
installation directory.

### Frontend Requirements

HPIT's administrative frontend relies heavily on CoffeeScript and LESScss. CoffeeScript and LESScss are NodeJS packages and so
you will need to download and install node to be able to run the HPIT server. Go to http://nodejs.org and follow the instructions
for downloading and installing node and npm to your system. IMPORTANT! If you are using an older version of ubuntu (13.10 or earlier)
you MUST download node and recompile from scratch. The version of node packaged with older versions of ubuntu is far out of date
and neither coffeescript or less will work. We recommend putting your compiled node installation in /opt and symbolically linking
the binaries to either /usr/bin or /usr/local/bin

### Installing HPIT

Then you can begin installalling HPIT by:

1. Change to the directory where you have downloaded hpit with: `cd /path/to/project`
2. Create a reference to your python3 installation binary for virtualenv. ```export PY3_PATH=`which python3````
3. Create a new virtual environment with: `virtualenv -p $PY3_PATH my_environment`
3. Activate that environment with: `source my_environment/bin/activate`
4. On Mac or Linux, install HPIT's dependencies with: `pip3 install -r requirements.txt`.  On Windows, run: 'pip install -r requirements-win.txt'.
5. If on Windows, install PyCrypto via a binary. 
6. Sync the configuration database with sqlite. `python3 manager.py syncdb`
6. Start the MongoDB instance with `mongod`
7. Run the test suite by typing `python3 manager.py test`

To start the HPIT server type: `python3 manager.py start` and open your browser 
to http://127.0.0.1:8000. 

## The HPIT Adminstration Panel

After starting the HPIT server, create an account, then sign-in to your account. There is no confirmation 
page after registering. The system will just direct you back to the signin/register page. After logging in
two new options are available for you. 'My Plugins' and 'My Tutors'. On each of these pages you can register
new plugins and tutors, respectively. For each plugin or tutor you create HPIT will generate for you an Entity ID
(which never changes), and an API Key(which can change). The API Key will only be displayed once, if you lose 
it you'll have to generate another and update your plugin or tutor code to match the new key. You will need 
to supply the API key and Entity ID to HPIT for the plugin or tutor to connect to HPIT, and to send and 
retrieve messages. You can think of the Entity ID and API Key as a sort of username/password pair for connecting
your tutor or plugin to HPIT. Keep these two pieces of information secure. The Entity ID can be told and released
to others, but NEVER share your API Key with anyone.

The Docs page on the adminsitration panel, shows these docs. The routes page on the administration panel shows
the web service endpoints that HPIT exposes to tutors and plugins.

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
- `python3 manager.py assets` will compile frontend assets together into a single file to ready for production deployments.
- `python3 manager.py debug` will run the HPIT server in debug mode and WILL NOT start any plugins or tutors.
- `python3 manager.py docs` copies this documentation file to the server assets directory.
- `python3 manager.py routes` lists all the routes that the HPIT Server/Router exposes to the web.
- `python3 manager.py syncdb` syncs the data model with the administration database.(PostgreSQL or Sqlite3)
- `python3 manager.py test` runs the suite of tests for components within HPIT.

## The tutor and plugin configuration

The goals behind the HPIT manager is to give TutorGen a way to create and destroy large 
amount of entities for testing and evaluation of the software. Creating a new hpit 
entity (tutor/plugin) adds it to the 'configuration.json'. Removing an hpit entity 
removes it from the 'configuration.json' file. All entities within the configuration specify
6 things: 

    1. Whether it is a tutor or plugin (by virtue of being in the tutor or plugin list)
    2. active - Whether the plugin is currently running. (True if it is)
    3. name - The name of the entity. This is how the entity will register itself with HPIT.
    4. type - The subtype of the entity. e.g. 'example' or 'knowledge_tracer'
    5. entity_id - The assigned Entity ID you got from creating the plugin or tutor in the administration panel.
    6. api_key - The assigned API Key you got from creating the plugin or tutor in the administration panel.

## Settings for Clients and Servers

Both clients (tutors and plugins) and the server may need configuration.  The settings files
are clients/settings.py and server/settings.py, for clients and servers, respectively.  

clients/settings.py currently contains the following options:
- HPIT_URL_ROOT : the URL root where the HPIT server lives

server/settings.py currently contains the following options:
- HPIT_VERSION : the version of this server
- DEBUG : If the server should be ran in debug mode (DEPRECATED)

- HPIT_PID_FILE : the location where the PID file of the server is stored, for tracking the server process
- HPIT_BIND_IP : the IP address the server is listening on
- HPIT_BIND_PORT : the port that the HPIT server listens on

- MONGO_DBNAME : The name of the HPTI database in MongoDB.
- SECRET_KEY : A cryptographic secret for generating other secrets. (Keep this secret)
- SQLALCHEMY_DATABASE_URI : A database URL for SQLAlchemy to store administrative data. (Defaults to SQLite)
- CSRF_ENABLED : True to enable protections against cross-site request forgery attacks.

- USER_PASSWORD_HASH : How passwords for users should be generated. (Leave this alone unless you know what you're doing.)

## Database Structure

The HPIT server uses a NoSQL MongoDB database to manage its messages and transactions. MongoDB uses a 
lazy creation policy, so the database and its collections are created only after elements are inserted,
and can be created with no prior configuration. The database contains five core collections:

### messages
A list of messages sent to the system before being duplicated to plugin_messages
It contains the following fields:
entity_id: "The session ID of the sender"
payload: "The data being sent."

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

HPIT uses a relational database (SQLite or PostgreSQL) for administrative purposes. This 
database manages, users, plugin authentication, tutor authentication, and plugin subscriptions.
By default this database is configured as sqlite and stored on the filesystem in the 
server/db subdirectory under hpit. The models (tables) stored can be found in the server/models
directory or by running sqlite and using the command '.tables'.

## The HPIT Server in depth

The HPIT Server is nothing more than an event-driven publish and subscribe framework, built
specifically to assist plugins and tutors to communicate via RESTful webserver. It is 
schemaless, has no pre-defined events, and is agnostic to the kinds of data it routes 
between plugins and tutors. In additon HPIT provides fundemental support for sessions,
authentication, message routing, and entity tracking.

Anyone can wrap these RESTful webservices in a client side library and will be able to interact
with HPIT. We have delivered a client side library written in Python.

The server supports a variety of routes to handle the connection, polling, and transfer of 
data between HPIT entities. To get a list of these routes run the HPIT server with either 
`python3 manager.py debug` or `python3 manager.py start` and open your browser to the HPIT
administration page at http://localhost:8000/routes. Alternativately you can list the routes
available with `python3 manager.py routes`

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
- MongoDB
- PostgreSQL
- Flask
- Jinja2
- WTForms
- PyMongo
- SQLAlchemy
- Daemonize
- PyCrypto
- Requests
- Gunicorn
- Gears
- Twitter Bootstrap
- BackboneJS
- UnderscoreJS
- JQuery

Information about specific versions can be found inside of requirements.txt

## License

This software is dual licensed under the MIT License and the BSD 3-clause license.

==============================================================================
The MIT License (MIT)

Copyright (c) 2014 TutorGen, Inc.
All rights reserved.

Contributions by: 

Raymond Chandler III
Brian Sauer
Jian Sun
Ryan Carlson
John Stamper
Mary J. Blink
Ted Carmichael

In association with Carnegie Mellon University, Carnegie Learning, and 
Advanced Distributed Learning.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

==============================================================================

OR

==============================================================================
The BSD 3-Clause License

Copyright (c) 2014, TutorGen, Inc.
All rights reserved.

Contributions by: 

Raymond Chandler III
Brian Sauer
Jian Sun
Ryan Carlson
John Stamper
Mary J. Blink
Ted Carmichael

In association with Carnegie Mellon University, Carnegie Learning, and 
Advanced Distributed Learning.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==============================================================================
