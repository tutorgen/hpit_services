# The HyperPersonalized Intelligent Tutor (HPIT)

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
with the system by sending transactions which consist of a named event and a data payload. 
Plugins can listen to these events, perform an action, then submit a response back to HPIT,
which will ultimately be routed to the tutor that made the original request.

In addition, HPIT packages several baseline plugins which peform basic functions related
to intelligent tutoring systems.

## Getting started

HPIT requires Python 3.4. Make sure that you have this version of Python installed and
linked into your PATH. Most systems that come with Python have Python 2.7x branch installed.
You may need to install Python3.4 manually to get started depending on your operating system.

You can check your version of Python by typing: `python --version` or `python3 --version`

Once you have the right version of Python installed you should also have `virtualenv` 
and `pip` installed as well. If you are unfamiliar with either of these libraries I highly 
encourage you research them, as they will make working with HPIT much simpler.

Once you have pip and virtualenv installed you can install HPIT by:

1. Changing to the directory where you have downloaded hpit with: `cd /path/to/project`
2. Creating a new virtual environment with: `virtualenv my_environment`
3. Activating that environment with: `source my_environment/bin/activate`
4. Installing HPIT's dependencies with: `pip install -r requirements.txt`

Once you have the project dependencies setup you can begin working with HPIT via 
the HPIT manager. (See below)

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

## The HPIT Server in depth

## Tutors in depth

## Plugins in depth

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