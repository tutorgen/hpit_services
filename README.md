[ ![Codeship Build Status](https://codeship.io/projects/d0ff7820-f8ca-0131-f61d-5a47552ce69e/status)](https://codeship.io/projects/28762)
[![Travis Build Status](https://travis-ci.org/tutorgen/hpit_services.svg?branch=master)](https://travis-ci.org/tutorgen/hpit_services)

## Table of Contents

* [API Framework Documentation v2.1](#APIToc)
* [Understanding Terminology](#TermToc)
* [Getting Started](#GetStartedToc)
    * [Installing HPIT on Windows](#GSInstallWindowsToc)
    * [Installing HPIT on Mac OSX](#GSInstallMacOSXToc)
    * [Installing HPIT on Ubuntu 12.04](#GSInstallUbuntu12Toc)
    * [Installing HPIT on Ubuntu 14.04](#GSInstallUbuntu14Toc)
* [Old Install Guide (deprecated)](#GSOldInstallGuideToc)
    * [Python Requirements](#GSReqToc)
    * [Production Considerations](#GSProdToc)
    * [Frontend Requirements](#GSFrontendToc)
    * [Installing HPIT](#GSInstallToc)
    * [Optional Installation for Hint Factory Plugin](#GSInstallOptToc)
* [The Adminstration Panel](#AdminToc)
* [The HPIT Manager](#ManagerToc)
* [The Tutor and Plugin Configuration](#ConfigToc)
* [Server Settings](#SettingsToc)
* [Database Structure](#DatabaseToc)
    * [messages](#DBmessagesToc)
    * [plugin_messages](#DBpluginmesToc)
    * [responses](#DBresponsesToc)
    * [sessions](#DBsessionsToc)
* [The HPIT Server in depth](#ServerToc)
* [Tutors in depth](#TutorToc)
* [Plugin Component Specification](#PluginToc)
    * [Echo Example](#ExPlugin)
    * [Data Connection to PSLC Datashop](#DCPlugin)
    * [Data Storage](#DSPlugin)
    * [Student Management](#SMPlugin)
        * [add_student](#add_student)
        * [get_student](#get_student)
        * [set_attribute](#set_attribute)
        * [get_attribute](#get_attribute)
    * [Skill Management](#SKMPlugin)
        * [add_skill](#add_skill)
        * [remove_skill](#remove_skill)
        * [get_skill](#get_skill)
    * [Knowledge Tracing](#KTPlugin)
        * [kt_set_initial](#kt_set_initial)
        * [kt_reset](#kt_reset)
        * [kt_trace](#kt_trace)
    * [Hint Factory (model tracing)](#HFPlugin)
        * [hf_init_problem](#hf_init_problem)
        * [hf_push_state](#hf_push_state)
        * [hf_hint_exists](#hf_hint_exists)
        * [hf_get_hint](#hf_get_hint)
    * [Problem Management](#PMPlugin)
        * [add_problem](#add_problem)
        * [remove_problem](#remove_problem)
        * [get_problem](#get_problem)
        * [list_problems](#list_problems)
    * [Problem Step Management](#PSMPlugin)
        * [add_problem_step](#add_problem_step)
        * [remove_problem_step](#remove_problem_step)
        * [get_problem_step](#get_problem_step)
        * [list_problem_steps](#list_problem_steps)
* [Developing New Plugins and Tutors](https://github.com/tutorgen/HPIT-python-client/blob/master/README.md)
* [License](#LicenseToc)

## <a name="APIToc"></a>API Framework Documentation v2.1

The HyperPersonalized Intelligent Tutor (HPIT) is a schemaless, event driven system
which specializes in the communication between distributed intelligent tutoring systems 
and specialized, machine learning algorithims, which we call plugins. HPIT is a next 
generation system built on the backbone of open source web technologies.

Currently our tech stack consists of the following:

- Python 3.4
- MongoDB
- PostgreSQL
- Neo4j
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

## <a name="TermToc"></a> Understanding Terminology

HPIT - HPIT consists of several modules and is sort of an all encompassing term for the entire 
system of modules.

Tutor - A tutor is an entity that interacts with students and uses the HPIT system to gather 
and analyze intelligent information about student perforamance. A tutor could be a game, or a web application,
a Flash game, or some other system that interacts with students in an effort to educate or train.

Plugin - An HPIT Plugin is a module that specializes in a very specific and narrow band of responsibility.
A plugin may exist inside of HPIT itself(at TutorGen) or on a network or system outside of HPIT. Regardless of
where the plugin sits it must communicate with the central HPIT router/server.

HPIT Manager - The manager is used to load the HPIT router, and a set of plugins and tutors. It
is used primarily for testing and development.

HPIT Router/Server - This is the central server that routes messages and transactions between tutors
and plugins.

HPIT Message - This is a event_name and payload pair, both of which are defined by the developer for
their plugin.

HPIT Transaction - A transaction is a message specifically for PSLC DataShop transactions.

##<a name="GetStartedToc"></a> Getting Started

###<a name="GSInstallWindowsToc"></a> Installing HPIT on Windows

#### TODO

###<a name="GSInstallMacOSXToc"></a> Installing HPIT on Mac OSX

#### Installing X-Code, Command Line Tools, and Homebrew
1. Go to the Apple Developer page. Here: https://developer.apple.com/downloads/index.action
2. If you don't have an apple developer account, create one.
3. Download Xcode and the Command Line Tools for your version os OSX.
4. Install Homebrew by running the following command: `ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"`
5. Install git with `brew install git`

#### Installing Python 3.4

1. Check to see if you have this version installed by default open up your terminal and enter `python3 --version`. 
2. To install Python 3.4 or higher we recommend you install it through homebrew with `brew install python3`

#### Installing the Databases

HPIT uses sqlite3 locally by default and for running it's test suite. If you are installing in production we recommend
that you confiqure HPIT to use postgreSQL over sqlite3.

1. `brew install mongodb sqlite`
2. (optional) Install postgresql with Postgres.app found here: http://postgresapp.com/

#### Installing NodeJS and NPM

HPIT's administrative frontend relies heavily on CoffeeScript and LESScss. CoffeeScript and LESScss are NodeJS packages and so
you will need to download and install node to be able to run the HPIT server. Luckily on Max OSX this is a relatively trivial task.

* `brew install node`
* `npm install coffeescript-compiler less`

#### Installing Neo4J for the Hint Factory

If you plan on using the Hint Factory you will also need to have installed the Neo4J graph database. The best way to do so
is again, through Homebrew.

* `brew install neo4j`
* Start neo4j with `neo4j start`

#### Installing HPIT Itself

1. Clone the HPIT project from github: `git clone https://github.com/tutorgen/hpit_services hpit`
1. Change to the directory of the HPIT project: `cd hpit`
2. Create a reference to your python3 installation binary for virtualenv. ```export PY3_PATH=`which python3````
3. Create a new virtual environment with: `virtualenv -p $PY3_PATH env`
3. Activate that environment with: `source env/bin/activate`
4. Install HPIT's dependencies with: `pip3 install -r requirements.txt`.
7. Sync the configuration database with sqlite. `python3 manager.py syncdb`
8. Seed the Mongo Database with `python3 manager.py mongo server/db/mongo`
6. Start the MongoDB instance with `mongod --dbpath server/db/mongo`
8. Run the test suite by typing `python3 manager.py test`

To start the HPIT server type: `python3 manager.py start` and open your browser 
to http://127.0.0.1:8000. 

###<a name="GSInstallUbuntu12Toc"></a> Installing HPIT on Ubuntu 12.04

#### Getting Started
The first thing you'll need to do is update and upgrade your apt repositories:

`sudo apt-get update`

`sudo apt-get upgrade`


Next, install the C compiler and other build utilities:

`sudo apt-get install build-essential`

HPIT requires Python 3.4 or higher.  Ubuntu 12.04 does not include Python 3.4 in its
repositories by default, so you must install it from the fkrull/deadsnakes PPA:

`sudo add-apt-repository ppa:fkrull/deadsnakes`

`sudo apt-get update`

`sudo apt-get install python3.4`

You can verify you have the correct version of Python by typing:

`python3.4 --version`

Next, to install the numerous Python packages HPIT requires, you'll need Pip, which
needs to be compatible with Python 3.4.  The easiest way to do this is to use the 
command:

`python3.4 -m ensurepip --upgrade`


We highly recommend using virtualenv when running HPIT.  If you are unfamiliar with
virtualenv, you can read about it at http://virtualenv.readthedocs.org/en/latest/. 
Install virtualenv from pip, with the command:

`pip3 install virtualenv`

#### Databases
HPIT uses five different database managers; MongoDB, SQLite, PostgreSQL, Neo4j, and Couchbase.

#####SQLite and MongoDB
Installing SQLite and MongoDB are easy to install, simply use apt-get:

`sudo apt-get install sqlite mongodb`

#####PostgreSQL
To install PostgreSQL, use the commands:

`sudo apt-get install postgresql postgresql-contrib`

In order for Python to interact with PostgreSQL, we'll need the dependencies for the psycopg2 library.  Install
instructions are found at http://initd.org/psycopg/docs/install.html#install-from-source , 
and summarized here:

Install the Python 3.4 headers, using: `sudo apt-get install libpython3.4-dev`.  This comes from
this fkrull/deadsnakes repository.

Install the libpq headers, using: `sudo apt-get install libpq-dev`.  Try running `pg_config --version`
to ensure it installed correctly.

psycopg2 will be installed later with Pip.

#####Neo4j
Next, we need to install Neo4j.  Neo4j requires Oracle JDK 7 or OpenJDK 7.  You can verify this is installed
by using: `java -version`.

To install Neo4j, follow the steps located at http://debian.neo4j.org/ , summarized below:

`sudo wget -O - http://debian.neo4j.org/neotechnology.gpg.key| apt-key add - # Import Neo4j signing key`

`sudo echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list # Create an Apt sources.list file`

`sudo apt-get update # Find out about the files in our repository`

`sudo apt-get install neo4j # Install Neo4j, community edition`

#####Couchbase
HPIT utilizes Couchbase Community Edition as a caching layer.  Visit http://www.couchbase.com/download for 
install instructions, summarized below:
* Download the package for 32-bit or 64-bit Ubuntu, depending on your system.
* Use dpkg with sudo, for example, `sudo dpkg -i couchbase-server-enterprise_2.5.1_x86_64.deb`.
















###<a name="GSInstallUbuntu14Toc"></a> Installing HPIT on Ubuntu 14.04

#### TODO

##<a name="GSOldInstallGuideToc"></a> Old Install Guide 

Ignore this section if you used the guides above.

###<a name="GSReqToc"></a> Python Requirements

HPIT requires Python 3.4. Make sure that you have this version of Python installed and
linked into your PATH. Most systems that come with Python have Python 2.7x branch installed.
You may need to install Python3.4 manually to get started depending on your operating system.

You can check your version of Python by typing: `python --version` or `python3 --version`

Once you have the right version of Python installed you should also have `virtualenv` 
and `pip` installed as well. If you are unfamiliar with either of these libraries I highly 
encourage you research them, as they will make working with HPIT much simpler.

Once you have pip and virtualenv installed you will need to install mongodb and sqlite3.

* On Ubuntu: `sudo apt-get install mongodb sqlite` 
* On Mac OSX with HomeBrew: `brew install mongodb sqlite`. 
* On Windows: installation binaries are available from http://www.mongodb.org and http://www.sqlite.org/download.html

###<a name="GSProdToc"></a> Production Considerations

If installing in PRODUCTION ONLY you should use PostgreSQL rather than SQLite3.

* On Ubuntu: `sudo apt-get install postgresql-server`
* On Mac OSX: We recommend you install postgres using 
* On Windows: Installation binaries are available from http://www.postgresql.com

It is assumed that if you are installing this in a PRODUCTION ONLY environment, that you have experience with PostgreSQL. If not,
then please read the tutorial here: http://www.postgresql.org/docs/9.3/static/tutorial.html In general you will need to 
configure some security settings in postgres, create a database, then create login roles for that database. PostgreSQL by 
default does not make itself discoverable, or connectible from outside the local machine. If it is installed in a location
other than where you are installing HPIT you'll need to configure iptables, postgresql.conf and hba.conf in your postgreSQL
installation directory.

###<a name="GSFrontendToc"></a> Frontend Requirements

HPIT's administrative frontend relies heavily on CoffeeScript and LESScss. CoffeeScript and LESScss are NodeJS packages and so
you will need to download and install node to be able to run the HPIT server. Go to http://nodejs.org and follow the instructions
for downloading and installing node and npm to your system. IMPORTANT! If you are using an older version of ubuntu (13.10 or earlier)
you MUST download node and recompile from scratch. The version of node packaged with older versions of ubuntu is far out of date
and neither coffeescript or less will work. We recommend putting your compiled node installation in /opt and symbolically linking
the binaries to either /usr/bin or /usr/local/bin

###<a name="GSInstallToc"></a> Installing HPIT

Then you can begin installalling HPIT by:

1. Change to the directory where you have downloaded hpit with: `cd /path/to/project`
2. Create a reference to your python3 installation binary for virtualenv. ```export PY3_PATH=`which python3````
3. Create a new virtual environment with: `virtualenv -p $PY3_PATH my_environment`
3. Activate that environment with: `source my_environment/bin/activate`
4. On Mac or Linux, install HPIT's dependencies with: `pip3 install -r requirements.txt`.  On Windows, run: 'pip install -r requirements-win.txt'.
5. If on Windows, install PyCrypto via a binary. 
6. Start the MongoDB instance with `mongod`
7. Sync the configuration database with sqlite. `python3 manager.py syncdb`
8. Run the test suite by typing `python3 manager.py test`

To start the HPIT server type: `python3 manager.py start` and open your browser 
to http://127.0.0.1:8000. 

###<a name="GSInstallOptToc"></a> Optional Installation for Hint Factory Plugin

If you are wanting to use the hint factory plugin you will need to install neo4j graph database.

1. Install Neo4j
    - On Mac OSX: `brew install neo4j`.
    - On Ubuntu: `sudo apt-get install neo4j`.
    - On Windows, binaries are available.
2. Start NEO4J. `neo4j start`.  This may vary depending on your system configuration.

## <a name="AdminToc"></a> The Adminstration Panel

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

##<a name="ManagerToc"></a> The HPIT Manager

The HPIT Manager can be used to quickly launch an HPIT server, configure plugins and tutors,
and monitor how data is being passed between entities within the HPIT system.

The HPIT manager can be run by typing: `python3 manager.py <command> <command_args>`

Depending on the command you wish to run the arguments to that command will vary. The command
line manager for HPIT will help you along the way. For example typing just `python3 manager.py`
will give you a list of commands that manager understands. Then typing 
`python3 manager.py your_command` will show you the arguments that that command can take and a
brief overview of what that command does.

Currently the HPIT Manager has the following commands:

* `python3 manager.py start` will start the HPIT server, all locally configured tutors, and all locally configured plugins.
* `python3 manager.py stop` will stop the HPIT server, all locally configured tutors, and all locally configured plugins.
* `python3 manager.py status` will show you whether or not the HPIT server is currently running.
* `python3 manager.py add plugin <name> <subtype>` will help you create plugins with the specified name and subtype.
* `python3 manager.py remove plugin <name>` will help you remove plugins with the specified name.
* `python3 manager.py add tutor <name> <subtype>` will help you create tutors with the specified name and subtype.
* `python3 manager.py remove tutor <name>` will help you remove tutors with the specified name.
* `python3 manager.py assets` will compile frontend assets together into a single file to ready for production deployments.
* `python3 manager.py debug` will run the HPIT server in debug mode and WILL NOT start any plugins or tutors.
* `python3 manager.py docs` copies this documentation file to the server assets directory.
* `python3 manager.py routes` lists all the routes that the HPIT Server/Router exposes to the web.
* `python3 manager.py syncdb` syncs the data model with the administration database.(PostgreSQL or Sqlite3)
* `python3 manager.py mongo <dbpath>` Initializes MongoDB database.
* `python3 manager.py test` runs the suite of tests for components within HPIT.

##<a name="ConfigToc"></a> The Tutor and Plugin Configuration

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

## <a name="SettingsToc"></a> Server Settings

There are various settings available for modification in the `server/settings.py` file.

name                        | default                                     | description                                                 | notes                        
--------------------------- | ------------------------------------------- | ----------------------------------------------------------- | -----------------------------
HPIT_VERSION                | string (really long)                        | A string representation of the current version of HPIT      |                              
DEBUG                       | False                                       | Whether to run the server in debug mode or not              | Deprecated                   
HPIT_PID_FILE               | 'tmp/hpit_server.pid'                       | Where to put the PID file for the hpit server (daemon)      |                              
HPIT_BIND_IP                | "0.0.0.0"                                   | The IP Address to listen for connections on.                |                              
HPIT_BIND_PORT              | "8000"                                      | The Port Address to listen for connections on.              |                              
HPIT_BIND_ADDRESS           | HPIT_BIND_IP+":"+HPIT_BIND_PORT             | A comination of the IP and Port addresses                   | Don't change this.           
PROJECT_DIR                 | '/Users/raymond/Projects/TutorGen/hpit'     | The root working directory for HPIT.                        | Change this.                 
VENV_DIRNAME                | 'env'                                       | The directory where the virtual enviornment is located.     |                              
MONGO_DBNAME                | 'hpit_development'                          | The name of the mongo database to store information in.     |                              
SECRET_KEY                  | random character string length 60 or longer | A secret key used for cryptography. Keep secure.            | YOU MUST CHANGE THIS IN PROD!
SQLALCHEMY_DATABASE_URI     | 'sqlite:///db/hpit_development.sqlite'      | A database URI for relational storage.                      | Several databases supported. 
CSRF_ENABLED                | True                                        | Enable Cross-Site Request Forgery Protection?               | Don't change this.           
MAIL_DEBUG                  | True                                        | Don't actually send emails. Print to console instead.       | Change in production.        
MAIL_SERVER                 | 'smtp.gmail.com'                            | The SMTP server to send mail through.                       |                              
MAIL_PORT                   | 465                                         | The REMOTE Port to send mail on.                            |                              
MAIL_USE_SSL                | True                                        | Use SSL when sending mail?                                  |                              
MAIL_USERNAME               | 'hpit@tutorgen.com'                         | The mail account username on the SMTP server.               |                              
MAIL_PASSWORD               | 'abcd1234'                                  | The mail account password on the SMTP server.               |                              
MAIL_DEFAULT_SENDER         | 'hpit-project.org'                          | Who to send mail as.                                        |                               
USER_PASSWORD_HASH          | 'bcrypt_sha256'                             | The hashing method for creating user passwords.             |                               
USER_ENABLE_EMAIL           | False                                       | User's use email as their usernames? (mutually exclusive)   |                               
USER_ENABLE_USERNAME        | True                                        | User use a standard username? (mutually exclusive)          |                               
USER_ENABLE_CONFIRM_EMAIL   | False                                       | Enable email confirmation for user registration.            |                               
USER_ENABLE_CHANGE_USERNAME | False                                       | Allow a user to change their username?                      |                               
USER_ENABLE_CHANGE_PASSWORD | True                                        | Allow a user to change their password?                      |                               
USER_ENABLE_FORGOT_PASSWORD | False                                       | Allow a user to recover their password through email?       |                               
USER_ENABLE_RETYPE_PASSWORD | True                                        | Make a user retype their password when creating an account? |                               
USER_LOGIN_TEMPLATE         | 'flask_user/login_or_register.html'         | Login template rendered to HTML                             |                               
USER_REGISTER_TEMPLATE      | 'flask_user/register.html'                  | Register template rendered to HTML                          |                               

## <a name="DatabaseToc"></a> Database Structure

The HPIT server uses a NoSQL MongoDB database to manage its messages and transactions. MongoDB uses a 
lazy creation policy, so the database and its collections are created only after elements are inserted,
and can be created with no prior configuration. The database contains five core collections:

### <a name="DBmessagesToc"></a> messages
A list of messages sent to the system before being duplicated to plugin_messages. Each message contains the following fields:

- entity_id: "The session ID of the sender"
- payload: "The data being sent."

### <a name="DBpluginmesToc"></a> plugin_messages
Contains messages sent to plugins, as copied from the messages collection. It contains the following fields:

- plugin_name: "name of destination plugin"
- event_name: "name of event"
- message_id: "the ID of this message"
- message_payload: "The data contained in this message."
- sent_to_plugin: "Boolean if it has been processed or not"

### <a name="DBresponsesToc"></a> responses
Stores responses for tutors or other plugins to poll. It contains the following fields:

- response_received: "Boolean if it has been processed or not"
- response: "data for this response"
- message_id: "the id of the original sent message"
- message: "the original message"

### <a name="DBsessionsToc"></a> sessions
Stores session data for plugins and tutors. 

HPIT uses a relational database (SQLite or PostgreSQL) for administrative purposes. This 
database manages, users, plugin authentication, tutor authentication, and plugin subscriptions.
By default this database is configured as sqlite and stored on the filesystem in the 
server/db subdirectory under hpit. The models (tables) stored can be found in the server/models
directory or by running sqlite and using the command '.tables'.

## <a name="ServerToc"></a> The HPIT Server in depth

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

## <a name="TutorToc"></a> Tutors in depth

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

## <a name="PluginToc"></a> Plugin Component Specification

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

##<a name="ExPlugin"></a> Example Plugin

The example plugin listens to the `test` and `example` event names and logs
whatever data it's sent in the payload to a file.

##<a name="SMPlugin"></a> Student Management Plugin

The student management plugin allows you to track student across your 
applications and integrates into skill management and knowledge tracing. In addition
you can assign any number of attributes to your students and retreive them later. These
attributes can cover anything from how much they like sports, to their age, and brand
preferences.

####<a name="add_student"></a> add_student
####<a name="get_student"></a> get_student
####<a name='set_attribute'></a> set_attribute
####<a name="get_attribute"></a> get_attribute

##<a name="SKMPlugin"></a> Skill Management Plugin

The skill management plugin allows you to track skills across your applications
and integrates into knowledge tracing, problem selection, problem management, and
the hint factory. The skill manager idenitfies skills by either an assigned identifier
or by name.

####<a name="add_skill"></a> add_skill
####<a name="remove_skill"></a> remove_skill
####<a name="get_skill"></a> get_skill

##<a name="KTPlugin"></a> Knowledge Tracing Plugin

####<a name="kt_set_initial"></a> kt_set_initial
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

####<a name="kt_reset"></a> kt_reset
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

####<a name="kt_trace"></a> kt_trace
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

##<a name="HFPlugin"></a> Hint Factory Plugin

####<a name="hf_init_problem"></a> hf_init_problem
Initializes a new problem for the hint factory.

Recieves:

* start_state : string - A string representing the starting state of the problem (i.e. "2x + 4 = 12")
* goal_problem: string - A string representing the goal of the problem (i.e. "x = 4")

Returns:

* status: string - OK or NOT_OK on success and failure respectively

####<a name="hf_push_state"></a> hf_push_state
Pushes a new state on the problem.

Recieves:

* state : json - A json object representing the state to push.
* state.problem_state: string - A string representing the new state of the problem. i.e. "x = 4"
* state.steps: array of strings - A list of steps taken from the starting state to get to this state. i.e. ["Subtract 4", "Divide 2"]
* state.last_problem_state: string - What state this problem was in before this state. i.e. "2x = 8"
* state.problem: string - A string represting the problem i.e "2x + 4 = 12"

Returns:

* status: string - OK

####<a name="hf_hint_exists"></a> hf_hint_exists
Given a particular state structure. Does a hint exist for this problem?

Recieves:

* state : json - A json object representing the state to push.
* state.problem_state: string - A string representing the new state of the problem. i.e. "x = 4"
* state.steps: array of strings - A list of steps taken from the starting state to get to this state. i.e. ["Subtract 4", "Divide 2"]
* state.last_problem_state: string - What state this problem was in before this state. i.e. "2x = 8"
* state.problem: string - A string represting the problem i.e "2x + 4 = 12"

Returns:

* status: string - OK
* exists: string - YES if a hint is available, NO if it isn't

####<a name="hf_get_hint"></a> hf_get_hint
Given a particular state structure for a problem, retrieve the next most probable state that leads
the student towards a solution.

Recieves:

* state : json - A json object representing the state to push.
* state.problem_state: string - A string representing the new state of the problem. i.e. "x = 4"
* state.steps: array of strings - A list of steps taken from the starting state to get to this state. i.e. ["Subtract 4", "Divide 2"]
* state.last_problem_state: string - What state this problem was in before this state. i.e. "2x = 8"
* state.problem: string - A string represting the problem i.e "2x + 4 = 12"

Returns:

* status: string - OK
* exists: string - YES if a hint is available, NO if it isn't
* hint_text: string - The text describing the hint.

##<a name="PMPlugin"></a> Problem Management Plugin

####<a name="add_problem"></a> add_problem
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

####<a name="remove_problem"></a> remove_problem
Remove a problem from the problem manager.

Recieves:

* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* problem_name : string - The name of the problem.

Returns:

* problem_name : string - The name of the problem that was removed.
* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed and was deleted.

####<a name="get_problem"></a> get_problem
Gets a previously stored problem from the problem manager.

Recieves:

* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)
* problem_name : string - The name of the problem to retrieve.

Returns:

* problem_name : string - The name of the problem.
* problem_text : string - The text of the problem.
* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed.

####<a name="list_problems"></a> list_problems
Get all the problems for a given entity.

Recieves:

* entity_id : string - An identifier for the sender. (Defined by the HPIT Server)

Returns:

* problems : list - A list of problems with
    * problem_name : string - The name of the problem.
    * problem_text : string - The text of the problem.
* success : True - Always returns True

##<a name="PSMPlugin"></a> Problem Step Management Plugin

####<a name="add_problem_step"></a> add_problem_step
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

####<a name="remove_problem_step"></a> remove_problem_step
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

####<a name="get_problem_step"></a> get_problem_step
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

####<a name="list_problem_steps"></a> list_problem_steps
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

##<a name="DSPlugin"></a> Data Storage Plugin

### TODO

##<a name="DCPlugin"></a> PSLC DataShop Connection Plugin

### TODO

## <a name="LicenseToc"></a> License

This software is dual licensed under the MIT License and the BSD 3-clause license.

==============================================================================

The MIT License (MIT)

Copyright (c) 2014 TutorGen, Inc.
All rights reserved.

Contributions by: 

* Raymond Chandler III 
* Brian Sauer 
* Jian Sun 
* Ryan Carlson 
* John Stamper 
* Mary J. Blink 
* Ted Carmichael 

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

* Raymond Chandler III 
* Brian Sauer 
* Jian Sun 
* Ryan Carlson 
* John Stamper 
* Mary J. Blink 
* Ted Carmichael 


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
