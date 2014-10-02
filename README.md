[![Travis Build Status](https://travis-ci.org/tutorgen/hpit_services.svg?branch=master)](https://travis-ci.org/tutorgen/hpit_services)

## Table of Contents

* [API Framework Documentation v2.1](#APIToc)
* [Understanding Terminology](#TermToc)
* [Getting Started](#GetStartedToc)
    * [System Requirements](#GSSystemRequirementsToc)
    * [Installing HPIT on Windows](#GSInstallWindowsToc)
    * [Installing HPIT on Mac OSX](#GSInstallMacOSXToc)
    * [Installing HPIT on Ubuntu 12.04](#GSInstallUbuntu12Toc)
    * [Installing HPIT on Ubuntu 14.04](#GSInstallUbuntu14Toc)
    * [Common Hangups](#GSCommonHangupsToc)
    * [Server Settings](#GSServerSettingsToc)
* [The Administration Panel](#AdminToc)
* [The HPIT Manager](#ManagerToc)
* [The Tutor and Plugin Configuration](#ConfigToc)
* [Database Structure](#DatabaseToc)
    * [messages](#DBmessagesToc)
    * [plugin_messages](#DBpluginmesToc)
    * [responses](#DBresponsesToc)
    * [sessions](#DBsessionsToc)
    * [entity_log](#DBlogToc)
* [The HPIT Server in-depth](#ServerToc)
* [Tutors in-depth](#TutorToc)
* [Plugin Component Specification](#PluginToc)
    * [Echo Example](#ExPlugin)
    * [Data Connection to PSLC DataShop](#DCPlugin)
    * [Data Storage](#DSPlugin)
    * [Student Management](#SMPlugin)
        * [add_student](#add_student)
        * [get_student](#get_student)
        * [set_attribute](#set_attribute)
        * [get_attribute](#get_attribute)
        * [get_student_model](#get_student_model)
    * [Skill Management](#SKMPlugin)
        * [get_skill_name](#get_skill_name)
        * [get_skill_id](#get_skill_id)
    * [Knowledge Tracing](#KTPlugin)
        * [kt_set_initial](#kt_set_initial)
        * [kt_reset](#kt_reset)
        * [kt_trace](#kt_trace)
    * [Hint Factory (model tracing)](#HFPlugin)
        * [hf_init_problem](#hf_init_problem)
        * [hf_push_state](#hf_push_state)
        * [hf_hint_exists](#hf_hint_exists)
        * [hf_get_hint](#hf_get_hint)
        * [get_student_model_fragment](#kt_get_student_model_fragment)
    * [Problem Management](#PMPlugin)
        * [add_problem](#add_problem)
        * [remove_problem](#remove_problem)
        * [get_problem](#get_problem)
        * [edit_problem](#edit_problem)
        * [list_problems](#list_problems)
        * [clone_problem](#clone_problem)
        * [add_problem_worked](#add_problem_worked)
        * [get_problems_worked](#get_problems_worked)
        * [add_step](#add_step)
        * [remove_step](#remove_step)
        * [get_step](#get_step)
        * [get_problem_steps](#get_problem_steps)
        * [get_student_model_fragment](#pm_get_student_model_fragment)
    * [Data Storage Plugin](#DSPlugin)
        * [store_data](#store_data)
        * [retrieve_data](#retrieve_data)
        * [remove_data](#remove_data)
    * [PSLC DataShop Connection Plugin](#DCPlugin)
        * [get_dataset_metadata](#get_dataset_metadata)
        * [get_sample_metadata](#get_sample_metadata)
        * [get_transactions](#get_transactions)
        * [get_student_steps](#get_student_steps)
        * [add_custom_field](#add_custom_field)
        
* [Developing New Plugins and Tutors](https://github.com/tutorgen/HPIT-python-client/blob/master/README.md)
* [License](#LicenseToc)

## <a name="APIToc"></a>API Framework Documentation v2.1

The HyperPersonalized Intelligent Tutor (HPIT) is a schemaless, event driven system
which specializes in the communication between distributed intelligent tutoring systems 
and specialized, machine learning algorithms, which we call plugins. HPIT is a next 
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

At the most fundamental layer HPIT is a collection of RESTful web services that assist in
the routing of messages between tutors and plugins. On top of this web services layer 
we have built a client side library in the Python programming language to assist in 
the creation of tutors and plugins and their communication with HPIT.

HPIT is a publish and subscribe framework using event-driven methodologies. Tutors interact 
with the system by sending messages which consist of a named event and a data payload. 
Plugins can listen to these events, perform an action, then submit a response back to HPIT,
which will ultimately be routed to the tutor that made the original request.

In addition, HPIT provides several baseline plugins which perform basic functions related
to intelligent tutoring systems.

## <a name="TermToc"></a> Understanding Terminology

HPIT - HPIT consists of several modules and is sort of an all encompassing term for the entire 
system of modules.

Tutor - A tutor is an entity that interacts with students and uses the HPIT system to gather 
and analyze intelligent information about student performance. A tutor could be a game, or a web application,
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
###<a name="GSSystemRequirementsToc"></a>System Requirements
In order to install and run HPIT, you'll need the following system:
* Operating systems
    * Windows 7 or Windows 8.1
    * Ubuntu 12.04 LTS or Ubuntu 14.04 LTS
    * OSX Mountain Lion or above
* Architecture
    * 64-bit processor
    * 32-bit processors will work in a limited fashion, but it is not recommended or supported
* Memory and Storage
    * Minimum 4 GB ram, 8 GB recommended
    * Minimum 2 GB hard disk, can scale up very quickly depending on your data volume
    * Solid state hard drives recommended

###<a name="GSInstallWindowsToc"></a> Installing HPIT on Windows
HPIT was designed to run on a Unix-like system, and Windows support is solely for development purposes.
Windows should not be used as an HPIT production server. 

#### Getting Started, Compilers.
First, to install HPIT, you'll need to install Microsoft Visual Studio.  The latest version should be fine; you can
find it at http://www.visualstudio.com/en-us/products/visual-studio-express-vs.aspx.

Next, you'll need the GCC, most easily installed with MinGW.  You can get it from here: http://mingw.org/.

Make sure to add C:\MinGW\bin and C:\MinGW\msys\1.0\bin to your PATH environment variable.

#### Install Python 3.3.5, Pip and virtualenv
To install Python 3.3.5, download the binary from https://www.python.org/downloads/ and run.

To install Pip, go to http://pip.readthedocs.org/en/latest/installing.html , download the get-pip.py script, and run with
`python get-pip.py`.

Verify you have the proper versions of Python and Pip:

`python --version`

`pip --version`

Next, install virtualenv using:

`pip install virtualenv`

Add C:\Python33\Scripts to your PATH so that pip and virtualenv are available commands.

#### Databases
HPIT uses five different database managers; MongoDB, SQLite, PostgreSQL, Neo4j, and Couchbase.

#####MongoDB
Binaries available at http://www.mongodb.org/downloads.  Download and run.
You will need to create the directory C:\data\db to run MongoDB.

#####SQLite
Go to http://www.sqlite.org/download.html and download sqlite-shell-win32-\*.zip and sqlite-dll-win32-\*.zip.

Create the directory C:\sqlite.

Extract the contents of the .zip files to C:\sqlite. There should be three files:
* sqlite3.def
* sqlite3.dll
* sqlite3.exe

Add C:\sqlite to your PATH environment variable.

#####Neo4j
Go to http://neo4j.com/download/ and download the Community edition binary and install.

##### Couchbase
Go to http://www.couchbase.com/download and download the Community edition binary and install.
After installing, go to http://localhost:8091/index.html to configure Couchbase.

To install the python client, go to https://pypi.python.org/pypi/couchbase and download 
couchbase-1.2.3.win-amd64-py3.3.exe. 

Activate your virtual environment (covered later) and run:

'easy_install ccouchbase-1.2.3.win-amd64-py3.3.exe'.

##### PostgreSQL
Because PostgreSQL is just a production replacement of SQLite, and Windows should never be used
as a production environment, this step is optional.  However, if you want to install PostgreSQL anyway,
there are binaries available at http://www.postgresql.org/download/windows/.

To install the psycopg2 library on Windows, there are instructions located at http://www.stickpeople.com/projects/python/win-psycopg/ and
are summarized here:

Download the 3.4 release for 64-bit processors.

Activate your virtual environment (covered later) and run 'easy_install psycopg2-2.5.4.win-amd64-py3.4-pg9.3.5-release.exe', replacing
the .exe in the command with the one you downloaded.

You'll need to add the bin directory of your PostgreSQL installation to PATH, so that `pg_config` is available to call.

####NodeJS
HPIT uses CoffeeScript and LESS for its front end, which requires NodeJS.

Binaries are available at http://nodejs.org/download/.

####Installing HPIT
#####Downloading HPIT and More Dependencies
Now we can install HPIT.  First, you will need the git command line tools.  They can be downloaded
from http://git-scm.com/download/win.

After git is installed, open up the Git Bash program, cd to your working directory (I used ~/Documents/HPIT) and run:

`git clone https://github.com/tutorgen/hpit_services`

Now it is time to create your virtual environment.  Switch back your your Windows Command Prompt.  It is important that you are using the 
correct Python binary when creating the virtual environment.  In our case, we used the command

`virtualenv -p C:\Python33\python.exe env`

Where virtualenv is the binary for the compatible version of virtualenv, C:\Python33\python.exe is your 
Python 3.3.5 binary, and env is the directory that the virtual environment will live in.

Next, activate the environment with the command `env\Scripts\activate.bat`.  Your command prompt
should now be prefixed with (env).

Now, find the directory env\Lib\distutils.  Add a file `distutils.cfg` with the contents:
    
    [build]
    compiler=mingw32
    
This tells Pip to use the MinGW compilers, which are required for some packages.

Now, install the Python dependencies using pip.  The command will be:

`pip install -r requirements-win.txt`

#####Configuring HPIT
First, make sure that MongoDB, Neo4j, and Couchbase are running.  HPIT is configured to use
SQLite for development, so PostgreSQL does not need to be started.  The databases can be 
controlled by these commands:

MongoDB:  `mongod`.  This will run in a terminal window until it is killed.

Neo4J: Run C:\Program Files\Newo4j Community\bin\neo4j-community.exe.  You can start and stop it
by clicking a button.

Couchbase: Couchbase will already be running after it is installed.

Next, set up the server settings.  Instructions are located in the section [Server Settings](#GSServerSettingsToc)

Now, seed the database with this command:

`python manager.py syncdb`

And run the tests:

`python manager.py test`

Assuming everything passed, you should then run:

`python manager.py start`

And browse to http://127.0.0.1:800 , where you should see a welcome page.

If you run into problems, check the section [Common Hangups](#GSCommonHangupsToc)


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

Install the libpq headers, using: `sudo apt-get install libpq-dev`.  Try running `pg_config --version`
to ensure it installed correctly.

psycopg2 will be installed later with Pip.

#### Installing NodeJS and NPM

HPIT's administrative frontend relies heavily on CoffeeScript and LESScss. CoffeeScript and LESScss are NodeJS packages and so
you will need to download and install node version 0.10.3 to be able to run the HPIT server. Luckily on Max OSX this is a relatively trivial task.

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
2. Create a reference to your python3 installation binary for virtualenv. `export PY3_PATH=$(which python3)`
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
HPIT supports the Ubuntu 12.04 LTS release.  However, if possible, it is highly recommended to
upgrade to the 14.04 LTS release.

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
* After installing, go to http://localhost:8091/index.html to configure Couchbase.

####NodeJS
HPIT uses CoffeeScript and LESS for its front end, which requires NodeJS.  We recommend installing 
NodeJS from source to ensure you get the latest version.  At least 0.10.3 is required. 

First, download the source code.  At the time of writing, it was located at http://nodejs.org/dist/v0.10.31/node-v0.10.31.tar.gz.
You can use wget, like this:

`wget http://nodejs.org/dist/v0.10.31/node-v0.10.31.tar.gz`

Next, extract the archive.

`tar xvfz node-v0.10.31.tar.gz`

Now, cd into the node-v0.10.31.tar.gz directory, and run:

`./configure`

`make`

`sudo make install`

####Installing HPIT
#####Downloading HPIT and More Dependencies
Now that the dependencies are installed, we can install HPIT.  To do this, you will need git:

`sudo apt-get install git`

Next, clone the HPIT repository using:

`git clone https://github.com/tutorgen/hpit_services`

Next, move into the hpit_services directory using `cd hpit_services`

Now it is time to create your virtual environment.  It is important that you are using the 
correct Python binary when creating the virtual environment.  In our case, we used the command

`virtualenv -p python3.4 env`

Where virtualenv is the binary for the compatible version of virtualenv, python3.4 is your 
Python 3.4 binary, and env is the directory that the virtual environment will live in.

Next, activate the environment with the command `source env/bin/activate`.  Your command prompt
should now be prefixed with (env).

Now, install the Python dependencies using pip3.  The command will be:

`pip3 install -r requirements.txt`

#####Configuring HPIT
First, make sure that MongoDB, Neo4j, and Couchbase are running.  HPIT is configured to use
SQLite for development, so PostgreSQL does not need to be started.  The databases can be 
controlled by these commands:

MongoDB:  `sudo service mongodb start`, `sudo service mongodb stop`

Neo4J: `sudo service neo4j-service start`, `sudo service neo4j-service stop`

Couchbase: `sudo /etc/init.d/couchbase-server start`, `sudo /etc/init.d/couchbase-server stop`

Next, set up the server settings.  Instructions are located in the section [Server Settings](#GSServerSettingsToc)

Now, seed the database with this command:

`python manager.py syncdb`

And run the tests:

`python manager.py test`

Assuming everything passed, you should then run:

`python manager.py start`

And browse to http://127.0.0.1:800 , where you should see a welcome page.

If you run into problems, check the section [Common Hangups](#GSCommonHangupsToc)

###<a name="GSInstallUbuntu14Toc"></a> Installing HPIT on Ubuntu 14.04
Ubuntu 14.04 LTS release is the preferred platform for HPIT.

#### Getting Started
The first thing you'll need to do is update and upgrade your apt repositories:

`sudo apt-get update`

`sudo apt-get upgrade`


Next, install the C compiler and other build utilities:

`sudo apt-get install build-essential`

HPIT requires Python 3.4 or higher.  Ubuntu 14.04 comes pre-packaged with Python 3.4, with a 
binary named python3.

You can verify you have the correct version of Python by typing:

`python3 --version`

Next, to install the numerous Python packages HPIT requires, you'll need Pip, which
needs to be compatible with Python 3.4.  The easiest way to do this is to use the 
command:

`sudo apt-get install python3-pip`


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

Install the Python 3.4 headers, using: `sudo apt-get install libpython3-dev`.

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
* After installing, go to http://localhost:8091/index.html to configure Couchbase.

####NodeJS
HPIT uses CoffeeScript and LESS for its front end, which requires NodeJS.  We recommend installing 
NodeJS from source to ensure you get the latest version. At least 0.10.3 is required. 

First, download the source code.  At the time of writing, it was located at http://nodejs.org/dist/v0.10.31/node-v0.10.31.tar.gz.
You can use wget, like this:

`wget http://nodejs.org/dist/v0.10.31/node-v0.10.31.tar.gz`

Next, extract the archive.

`tar xvfz node-v0.10.31.tar.gz`

Now, cd into the node-v0.10.31.tar.gz directory, and run:

`./configure`

`make`

`sudo make install`

####Installing HPIT
#####Downloading HPIT and More Dependencies
Now that the dependencies are installed, we can install HPIT.  To do this, you will need git:

`sudo apt-get install git`

Next, clone the HPIT repository using:

`git clone https://github.com/tutorgen/hpit_services`

Next, move into the hpit_services directory using `cd hpit_services`

Now it is time to create your virtual environment.  It is important that you are using the 
correct Python binary when creating the virtual environment.  In our case, we used the command

`virtualenv -p python3 env`

Where virtualenv is the binary for the compatible version of virtualenv, python3 is your 
Python 3.4 binary, and env is the directory that the virtual environment will live in.

Next, activate the environment with the command `source env/bin/activate`.  Your command prompt
should now be prefixed with (env).

Now, install the Python dependencies using pip3.  The command will be:

`pip3 install -r requirements.txt`

#####Configuring HPIT
First, make sure that MongoDB, Neo4j, and Couchbase are running.  HPIT is configured to use
SQLite for development, so PostgreSQL does not need to be started.  The databases can be 
controlled by these commands:

MongoDB:  `sudo service mongodb start`, `sudo service mongodb stop`

Neo4J: `sudo service neo4j-service start`, `sudo service neo4j-service stop`

Couchbase: `sudo /etc/init.d/couchbase-server start`, `sudo /etc/init.d/couchbase-server stop`

Next, set up the server settings.  Instructions are located in the section [Server Settings](#GSServerSettingsToc)

Now, seed the database with this command:

`python manager.py syncdb`

And run the tests:

`python manager.py test`

Assuming everything passed, you should then run:

`python manager.py start`

And browse to http://127.0.0.1:800 , where you should see a welcome page.

If you run into problems, check the section [Common Hangups](#GSCommonHangupsToc)

###<a name="GSServerSettingsToc"></a> Server Settings
The settings for HPIT can be set in JSON format, in a file called settings.json in the hpit_services root.  
This file allows for multiple environment settings, for example, "test", "debug", and "production".  The structure
of the file looks like this:

    {
        "debug": {
            "plugin": {
                [plugin settings go here (see below)]
            },
            "server": {
                [server settings go here (see below)]
            }
        },
        "production": {
            "plugin": {
                [plugin settings go here (see below)]
            },
            "server": {
                [server settings go here (see below)]
            }
        }
    }

HPIT will check for an environment variable called HPIT_ENV to determine which environment to use.  So, to use the
test settings, set a HPIT_ENV environment variable to "test" (without quotes).
    
Most of these settings can be left as defaults, but the important ones to change are:
* PROJECT_DIR - should be set to the directory this README is in
* VENV_DIRNAME - shoule be a relative link from PROJECT_DIR to wherever the virtual environment is.

####server
name                        | default                                     | description                                                 | notes                        
--------------------------- | ------------------------------------------- | ----------------------------------------------------------- | -----------------------------
HPIT_VERSION                | string (really long)                        | A string representation of the current version of HPIT      |                              
DEBUG                       | False                                       | Whether to run the server in debug mode or not              | Deprecated                   
HPIT_PID_FILE               | 'tmp/hpit_server.pid'                       | Where to put the PID file for the HPIT server (daemon)      |                              
HPIT_BIND_IP                | "0.0.0.0"                                   | The IP Address to listen for connections on.                |                              
HPIT_BIND_PORT              | "8000"                                      | The Port Address to listen for connections on.              |                              
HPIT_BIND_ADDRESS           | HPIT_BIND_IP+":"+HPIT_BIND_PORT             | A combination of the IP and Port addresses                   | Don't change this.           
PROJECT_DIR                 | '/Users/raymond/Projects/TutorGen/hpit'     | The root working directory for HPIT.                        | Change this.                 
VENV_DIRNAME                | 'env'                                       | The directory where the virtual environment is located.     | Change this.                             
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


####plugin
name                        | default                                     | description                                                 | notes                        
--------------------------- | ------------------------------------------- | ----------------------------------------------------------- | -----------------------------
DataShop_ROOT_URL           | "https://pslcDataShop.web.cmu.edu/services"   | Root DataShop URL                                         |
DataShop_SERVICES_URL       | "http://pslc-qa.andrew.cmu.edu/DataShop/services" | DataShop URL for services                             |
MONGODB_URI                 | "mongodb://localhost:27017/"                  | The location of the Mongo database server                 |
COUCHBASE_HOSTNAME          | "127.0.0.1"                                   | Couchbase host                                            |
COUCHBASE_BUCKET_URI        | "http://127.0.0.1:8091/pools/default/buckets" | Couchbase buckets REST endpoint                           |
COUCHBASE_AUTH              |  ["Administrator", "administrator"]           | Authentication for Couchbase server                       | Set to your server credentials

###<a name="GSCommonHangupsToc"></a> Common Hangups
Here's a list of common problems when trying to install HPIT:
* Permissions problems - if you're having troubles with permissions, make sure you are installing everything
in your user account, not root.
* Settings problems - make sure the settings are edited correctly for your system.  Verify that the paths to the
project directory and virtual environment are correct.
* Python problems - Make sure that Python, Pip, and virtualenv are all compatible with each other.
* Virtualenv problems - remember to activate your virtualenv when installing any python modules.  

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

The Docs page on the administration panel, shows these docs. The routes page on the administration panel shows
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
* `python3 manager.py assets` will compile frontend assets together into a single file to ready for production deployments.
* `python3 manager.py debug` will run the HPIT server in debug mode and WILL NOT start any plugins or tutors.
* `python3 manager.py docs` copies this documentation file to the server assets directory.
* `python3 manager.py routes` lists all the routes that the HPIT Server/Router exposes to the web.
* `python3 manager.py syncdb` syncs the data model with the administration database.(PostgreSQL or Sqlite3)
* `python3 manager.py mongo <dbpath>` Initializes MongoDB database.
* `python3 manager.py test` runs the suite of tests for components within HPIT.

##<a name="ConfigToc"></a> The Tutor and Plugin Configuration

The goals behind the HPIT manager is to give TutorGen a way to create and destroy large 
amount of entities for testing and evaluation of the software. Creating a new HPIT 
entity (tutor/plugin) adds it to the 'configuration.json'. Removing an HPIT entity 
removes it from the 'configuration.json' file. All entities within the configuration specify
6 things: 

1. Whether it is a tutor or plugin (by virtue of being in the tutor or plugin list)
2. active - Whether the plugin is currently running. (True if it is)
3. name - The name of the entity. This is how the entity will register itself with HPIT.
4. type - The subtype of the entity. e.g. 'example' or 'knowledge_tracer'
5. entity_id - The assigned Entity ID you got from creating the plugin or tutor in the administration panel.
6. api_key - The assigned API Key you got from creating the plugin or tutor in the administration panel.

Optionally, you can specify two optional parameters:

1. args - a json object for arguments that will be passed to the tutor or plugin
2. once - a boolean that tells the tutor or plugin to run only one time.

An example configuration would look like this:

    {
        "tutors" : [
            {
                "name": "replay_tutor", 
                "args": {
                    "beforeTime": "02-11-2020 14:03:09", 
                    "filter": {
                        "event": "kt_trace"
                    }
                }, 
                "type": "replay", 
                "once": true, 
                "active": false, 
                "entity_id": "1234", 
                "api_key": "1234"
            }
        ],
        "plugins": [],
    }


## <a name="DatabaseToc"></a> Database Structure

HPIT uses a relational database (SQLite or PostgreSQL) for administrative purposes. This 
database manages, users, plugin authentication, tutor authentication, and plugin subscriptions.
By default this database is configured as SQLite and stored on the filesystem in the 
server/db subdirectory under HPIT. The models (tables) stored can be found in the server/models
directory or by running SQLite and using the command '.tables'.

The HPIT server uses a NoSQL MongoDB database to manage its messages and transactions. MongoDB uses a 
lazy creation policy, so the database and its collections are created only after elements are inserted,
and can be created with no prior configuration. The database contains five core collections:

### <a name="DBmessagesToc"></a> messages
A list of messages sent to the system before being duplicated to plugin_messages. Each message contains the following fields:

- sender_entity_id: "The session ID of the sender"
- payload: "The data being sent."
- time_created: "Date of message creation"
- message_name: "The type of the message"

### <a name="DBpluginmesToc"></a> plugin_messages
Contains messages sent to plugins, as copied from the messages collection. It contains the following fields:

- time_response_received: "The time the response was received (if any)"
- sent_to_plugin: "Boolean if was processed by plugin"
- message_name: "The type of the message"
- payload: "The data contained in this message."
- time_responded: "The time the response was created"
- sender_entity_id: "The id of the entity that sent the message"
- time_created: "The time the message was created"
- receiver_entity_id: "The plugin that received this message"
- time_received: "The time the message was processed by plugin"
- message_id: "The id of the message in the messages collection"

### <a name="DBresponsesToc"></a> responses
Stores responses for tutors or other plugins to poll. It contains the following fields:

- response_received: "Boolean if it has been processed or not"
- response: "data for this response"
- message: "the original message"
- message_id: "The ID of the message in the messages collection"
- receiver_entity_id: "the ID of the receiver"
- sender_entity_id: "The ID of the sender"
- time_response_received: "The time the response was processed"

### <a name="DBsessionsToc"></a> sessions
Stores session data for plugins and tutors. 

### <a name="DBlogToc"></a> entity_log
Stores entity log information.  It contains the following fields:

- deleted: "Was this log deleted?
- log_entry: "The text of the log"
- created_on: "The date the log was created"
- entity_id: "The entity that created this log.

## <a name="ServerToc"></a> The HPIT Server in-depth

The HPIT Server is nothing more than an event-driven publish and subscribe framework, built
specifically to assist plugins and tutors to communicate via RESTful webserver. It is 
schemaless, has no pre-defined events, and is agnostic to the kinds of data it routes 
between plugins and tutors. In additon HPIT provides fundamental support for sessions,
authentication, message routing, and entity tracking.

Anyone can wrap these RESTful web services in a client side library and will be able to interact
with HPIT. We have delivered a client side library written in Python.

The server supports a variety of routes to handle the connection, polling, and transfer of 
data between HPIT entities. To get a list of these routes run the HPIT server with either 
`python3 manager.py debug` or `python3 manager.py start` and open your browser to the HPIT
administration page at http://localhost:8000/routes. Alternatively you can list the routes
available with `python3 manager.py routes`

## <a name="TutorToc"></a> Tutors in-depth

A Tutor is an HPIT entity that can send messages to HPIT. A message consists of
an event name and a payload. The event name is an arbitrary string that defines what type
of message it is. Plugins register to listen to messages based on the event name. The 
message payload is an arbitrary JSON like document with data formatted based on plugin
requirements. The kinds of messages a tutor can send is defined by the plugins 
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

A Plugin is an HPIT entity that subscribes to (listens to) certain event names, receives
transaction payloads, performs some arbitrary function based on the event and message
payload, and may or may not return a response to the original sender of the message.

A plugin may listen to and define any events it wishes. When a tutor sends a message 
to HPIT, if a plugin has registered itself with HPIT, and if that plugin and subscribed
to the event name submitted with the tutor's message, it will receive a queued list
of messages when it polls the HPIT server for data. It is expected that plugins will
do this type of polling periodically to see if any new messages have been queued for 
processing by HPIT.

When a plugin processes an event from HPIT, it will receive all the information in the 
original message, including the information identifying the tutor that sent the
message. This identifying information is called the entity_id of the tutor.

A plugin may send a response to HPIT by providing the original message id, along with 
a response payload, which will be sent to the original sender of the message message.

It is possible for plugins to send messages like tutors and respond to messages
like tutors. In this way, it is possible for plugins to listen to, and re-fire event 
messages while altering the event name of the message so that other dependent 
plugins can also respond to the original transaction. This can create a daisy chaining
effect where plugins fire in series to process a complex series of messages.

##<a name="ExPlugin"></a> Example Plugin

The example plugin listens to the `test` and `example` event names and logs
whatever data it's sent in the payload to a file.

##<a name="SMPlugin"></a> Student Management Plugin

The student management plugin allows you to track students across your 
applications and integrates into skill management and knowledge tracing. In addition,
you can assign any number of attributes to your students and retrieve them later. These
attributes can cover anything; how much they like sports, their age, brand preferences, etc.

####<a name="add_student"></a> add_student
Adds a student to the database, giving them a unique ID.

Receives:

* (optional) attributes: a JSON value of key/value pairs of attributes

Returns:

* student_id : string - the ID for the new student
* attributes : JSON - the attributes for the new student 

####<a name="get_student"></a> get_student
Gets an already created student from an ID.

Receives:

* student_id : string - the ID from a previously created student

Returns:

* student_id : string - the ID from a previously created student
* attributes : JSON - the attributes for the new student 

####<a name='set_attribute'></a> set_attribute
Sets an attribute value for a student.  Will overwrite any existing value.

Receives:

* student_id : string - the ID from a previously created student  
* attribute_name : string - the name of the attribute 
* attribute_value : string - the value of the new attribute

Returns:

* student_id : string - the ID for the student
* attributes : JSON - the attributes for the student  

####<a name="get_attribute"></a> get_attribute
Gets an attribute value for a student.  If the attribute does not exist, will respond
with an empty string.

Receives:

* student_id : string - the ID from a previously created student  
* attribute_name : string - the name of the attribute

Returns:

* student_id : string - the ID for the student
* (attribute_name) : string - value of the requested attribute.

####<a name = "get_student_model"></a>get_student_model
Get the student model for a student.  The student model is an aggregation of information from
all of the plugins that the student has interacted with.

Receives:

* student_id : string - the ID of the student

Returns:

* student_model : JSON - an object containing the student model.  This will contain lists and other objects from the various plugins.
* (optional) error : An error message if something went wrong of the request timed out.


##<a name="SKMPlugin"></a> Skill Management Plugin

The skill management plugin allows you to track skills across your applications
and integrates into knowledge tracing, problem selection, problem management, and
the hint factory. The skill manager identifies skills by either an assigned identifier
or by name.

####<a name="get_skill_name"></a> get_skill_name
Gets the name of an existing skill from an ID.

Receives:

* skill_id : string - the ID of the skill

Returns:

* skill_name : string - the name of the skill
* skill_id : string - the ID of a skill (should match sent ID)

####<a name="get_skill_id"></a> get_skill_id
Gets the ID of a skill from a skill name.  If the skill does not exist, it will be created.

Receives:

* skill_name : string - the name of the skill

Returns:

* skill_name : string - the name of the skill (should match what was sent)
* skill_id : string - the ID of the skill, either newly created or retrieved.
* cached : boolean - whether this came from the cache or database

##<a name="KTPlugin"></a> Knowledge Tracing Plugin
The Knowledge Tracing Plugin performs knowledge tracing on a per-student and per-skill basis.

####<a name="kt_set_initial"></a> kt_set_initial
Sets the initial probabilistic values for the knowledge tracer.

Receives:

* student_id : string - String ID of the student
* skill_id : string - String identifier for the skill.
* probability_known : float (0.0-1.0) - Probability the skill is already known
* probability_learned : float (0.0-1.0) - Probability the skill will be learned
* probability_guess : float (0.0-1.0) - Probability the answer is a guess
* probability_mistake : float (0.0-1.0) - Probability the student made a mistake (but knew the skill)

Returns:

* student_id : string - String ID of the student
* skill_id : string - String identifier for the skill.
* probability_known : float (0.0-1.0) - Probability the skill is already known
* probability_learned : float (0.0-1.0) - Probability the skill will be learned
* probability_guess : float (0.0-1.0) - Probability the answer is a guess
* probability_mistake : float (0.0-1.0) - Probability the student made a mistake (but knew the skill)

####<a name="kt_reset"></a> kt_reset
Resets the probabilistic values for the knowledge tracer.

Receives:

* student_id: string - An identifier for the student.
* skill_id : string - String identifier for the skill.

Returns:

* student_id: string - An identifier for the student.
* skill_id : string - String identifier for the skill.
* probability_known : 0.0 - Probability the skill is already known
* probability_learned : 0.0 - Probability the skill will be learned
* probability_guess : 0.0 - Probability the answer is a guess
* probability_mistake : 0.0 - Probability the student made a mistake (but knew the skill)

####<a name="kt_trace"></a> kt_trace
Runs a knowledge tracing algorithm on the skill/tutor combination and returns the result.

Receives:

* student_id: string - A string ID for the student
* skill_id : string - String identifier for the skill.
* correct: boolean - True if correct. False if not.

Returns:

* student_id: string - A string ID for the student
* skill_id : string - String identifier for the skill.
* probability_known : float (0.0-1.0) - Probability the skill is already known
* probability_learned : float (0.0-1.0) - Probability the skill will be learned
* probability_guess : float (0.0-1.0) - Probability the answer is a guess
* probability_mistake : float (0.0-1.0) - Probability the student made a mistake (but knew the skill)

####<a name="kt_get_student_model_fragment"></a>get_student_model_fragment
Returns a this plugin's contribution to the overall student model.  For the knowledge tracing plugin,
this is all of the student's skills and knowledge tracing values.  This is usually sent via the StudentManagement model
after it receives a get_student_model message.

Receives:

* student_id : string - the ID of the student

Returns:

* name : string - The name of the fragment, will always be "knowledge_tracing".
* fragment : list - A list of skills, containing:
    * student_id: string - An identifier for the student.
    * skill_id : string - String identifier for the skill.
    * probability_known : 0.0 - Probability the skill is already known
    * probability_learned : 0.0 - Probability the skill will be learned
    * probability_guess : 0.0 - Probability the answer is a guess
    * probability_mistake : 0.0 - Probability the student made a mistake (but knew the skill)

##<a name="HFPlugin"></a> Hint Factory Plugin
The Hint Factory Plugin is used to dynamically provide hints using a graph theoretic approach.

####<a name="hf_init_problem"></a> hf_init_problem
Initializes a new problem for the hint factory.

Receives:

* start_state : string - A string representing the starting state of the problem (i.e. "2x + 4 = 12")
* goal_problem: string - A string representing the goal of the problem (i.e. "x = 4")

Returns:

* status: string - OK or NOT_OK on success and failure respectively

####<a name="hf_push_state"></a> hf_push_state
Pushes a new state on the problem.

Receives:

* state : json - A json object representing the state to push.
* state.problem_state: string - A string representing the new state of the problem. i.e. "x = 4"
* state.steps: array of strings - A list of steps taken from the starting state to get to this state. i.e. ["Subtract 4", "Divide 2"]
* state.last_problem_state: string - What state this problem was in before this state. i.e. "2x = 8"
* state.problem: string - A string representing the problem i.e "2x + 4 = 12"

Returns:

* status: string - OK

####<a name="hf_hint_exists"></a> hf_hint_exists
Given a particular state structure. Does a hint exist for this problem?

Receives:

* state : json - A json object representing the state to push.
* state.problem_state: string - A string representing the new state of the problem. i.e. "x = 4"
* state.steps: array of strings - A list of steps taken from the starting state to get to this state. i.e. ["Subtract 4", "Divide 2"]
* state.last_problem_state: string - What state this problem was in before this state. i.e. "2x = 8"
* state.problem: string - A string representing the problem i.e "2x + 4 = 12"

Returns:

* status: string - OK
* exists: string - YES if a hint is available, NO if it isn't

####<a name="hf_get_hint"></a> hf_get_hint
Given a particular state structure for a problem, retrieve the next most probable state that leads
the student towards a solution.

Receives:

* state : json - A json object representing the state to push.
* state.problem_state: string - A string representing the new state of the problem. i.e. "x = 4"
* state.steps: array of strings - A list of steps taken from the starting state to get to this state. i.e. ["Subtract 4", "Divide 2"]
* state.last_problem_state: string - What state this problem was in before this state. i.e. "2x = 8"
* state.problem: string - A string representing the problem i.e "2x + 4 = 12"

Returns:

* status: string - OK
* exists: string - YES if a hint is available, NO if it isn't
* hint_text: string - The text describing the hint.

##<a name="PMPlugin"></a> Problem Management Plugin

####<a name="add_problem"></a> add_problem
Adds a problem to the problem manager.

Receives:

* problem_name : string - The name of the problem.
* problem_text : string - Text for the problem.

Returns:

* problem_name : string - The problem name.
* problem_text : string - The problem's text.
* success : boolean - True if the data was saved to the database.
* problem_id : string - String identifier for the new problem, or the existing problem if it already exists.
* (optional) error : string - The error message if something went wrong.

####<a name="remove_problem"></a> remove_problem
Remove a problem from the problem manager.

Receives:

* problem_id : string - A string identifier for the problem.

Returns:

* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed and was deleted.
* (optional) error : string - the error message if something went wrong

####<a name="get_problem"></a> get_problem
Gets a previously stored problem from the problem manager.

Receives:

* problem_id : string - The string identifier of the problem.

Returns:

* problem_id : string - The string identifier of the problem
* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed.
* (optional) error: string - The error message if the problem does not exist.

####<a name="edit_problem"></a> edit_problem
Edits a problem.  The tutor or plugin editing it must have the same ID as edit_allowed_id.

Receives:

* problem_id :  string - a string representation of this problems ID
* fields : JSON - a JSON object with the fields and values to be changed

Returns: 
* problem_name : string - The name of the problem.
* problem_text : string - The text of the problem.
* date_created : datetime - The time the problem was created.
* edit_allowed_id : string - The ID of the entity that can edit this problem.
* success : boolean - If the edit was successful.
* (optional) error : string - The error message, if an error occured.

####<a name="list_problems"></a> list_problems
Get all the problems in the database.

Receives:

* Nothing

Returns:

* problems : list - A list of problems with
    * problem_name : string - The name of the problem.
    * problem_text : string - The text of the problem.
    * date_created : datetime - When the problem was created.
    * edit_allowed_id : string - The ID of the entity that can edit this.
* success : True - Always returns True

####<a name="clone_problem"></a>clone_problem
Clone an existing problem so that another entity can modify it.

Receives:

* problem_id : string - The string identifier to the problem to be cloned.

Returns:

* problem_id : string - The ID of the new cloned problem.
* step_ids : list - A list of string identifiers for the newly cloned steps.
* success: boolean - A boolean if everything went well.
* (optional) error : string - An error message if an error accurs, caused by not passing the correct
parameters or the requested problem doesn't exist.

####<a name="add_problem_worked"></a>add_problem_worked
This is used to show a student has worked on a problem.

Receives: 

* problem_id : string - The string identifier of the problem the student has worked.
* student_id : string - The string identifier of the student that worked the problem.

Returns:

* success : boolean - Whether everything went ok.
* (optional) error : string - If an error occurs, an error message.

####<a name="get_problems_worked"></a>get_problems_worked
Retrieves the problems a student has worked on.

Receives:

* student_id : string - the string ID of the student

Returns:

* success : boolean - whether everything went ok
* problems_worked : list - A list of problems, containing:
    * student_id : string - The ID of the student.
    * problem_id : string - The ID of the problem.

####<a name="add_step"></a> add_step
Adds a problem step to a problem.

Receives:

* problem_id : string - The ID of the problem
* step_text : string - The text of the problem step.

Returns:

* step_id : string - The ID of the newly created step.
* success : boolean - Whether everything went ok.
* (optional) error : string - An error message if something went wrong.

####<a name="remove_step"></a> remove_problem_step
Remove a problem step from the problem manager.

Receives:

* step_id : string - The ID of the step.

Returns:

* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed and was deleted.
* (optional) error : string - an error emssage if something went wrong

####<a name="get_step"></a> get_problem_step
Gets a previously stored problem step from the problem manager.

Receives:

* step_id : string - The ID of the step.

Returns:

* step_id : string - The ID of the step.
* step_text : string - The step's text.
* date_created : datetime - The time the step was created.
* allowed_edit_id : string - The ID of the entity that can edit this step.
* siccess : boolean - Whether everything went OK.

####<a name="get_problem_steps"></a> list_problem_steps
Get all the problem steps for a given problem..

Receives:

* problem_id : string - The ID of the problem.

Returns:

* steps : list - A list of problems with
    * step_id : string - The ID of the step.
    * step_text : string - The step text.
    * date_created : datetime - The time the step was created.
* problem_id : string - The ID of the problem the steps belong to.
* success : boolean - Whether everything went ok.

####<a name="pm_get_student_model_fragment"></a>get_student_model_fragment
Returns a this plugin's contribution to the overall student model.  For the problem management plugin,
this is all of the problems the student has worked on.  This is usually sent via the StudentManagement model
after it receives a get_student_model message.

Receives:

* student_id : string - the ID of the student

Returns:

* name : string - The name of the fragment, will always be "problem_management".
* fragment : list - A list of problems, containing:
    * problem_name : string - The name of the problem.
    * problem_text : string - The text of the problem.
    * date_created : datetime - The time this problem was created.
    * edit_allowed_id : string - The ID of the tutor or plugin that can edit this problem.

##<a name="DSPlugin"></a> Data Storage Plugin
The Data Storage Plugin can be used to store any kind of key value information that a plugin
or tutor may need.
####<a name="store_data"></a>store_data
Store a key value pair in the database.

Receives:

* key : string - the key for the data
* value: string - the value for the data

Returns:

* insert_id : string - the ID of the data object

####<a name="retrieve_data"></a>retrieve_data
Get a value from the database via a key.

Receives:

* key : string - the key to query.

Returns:

* data : string - the data for the key

####<a name="remove_data"></a>remove_data
Removes data from the database.

Receives:

* key : string - the key to remove.

Returns:

* status : string - the response from MongoDB

##<a name="DCPlugin"></a> PSLC DataShop Connection Plugin
The PSLC DataShop Connection Plugin gives basic connectivity to the PSLC DataShop.  Currently, it
only provides for a subset of functionality that they provide via their web services.

####<a name="get_dataset_metadata"></a>get_dataset_metadata
Gets the dataset metadata.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

####<a name="get_sample_metadata"></a>get_sample_metadata
Gets the metadata for a DataShop sample.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID
* sample_id : string - the string representation of a DataShop sample ID

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

####<a name="get_transactions"></a>get_transactions
Gets transactions from a dataset or optionally a specific sample.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID
* (optional) sample_id : string - the string representation of a DataShop sample ID

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

####<a name="get_student_steps"></a>get_student_steps
Gets the student steps from a dataset or optionally a specific sample.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID
* (optional) sample_id : string - the string representation of a DataShop sample ID

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

####<a name="add_custom_field"></a>add_custom_field
Adds a custom field to a dataset.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID
* name : string - the name of the custom field
* description : string - the description of the custom field
* type : string - the data type.  Can be "number", "string", "date", or "big".

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

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
