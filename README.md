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
    * [The Settings Manager](#GSServerSettingsToc)
* [The Administration Panel](#AdminToc)
* [The HPIT Manager](#ManagerToc)
* [The Tutor and Plugin Configuration](#ConfigToc)
* [Database Structure](#DatabaseToc)
    * [messages](#DBmessagesToc)
    * [plugin_messages](#DBpluginmesToc)
    * [responses](#DBresponsesToc)
    * [sent_messages_and_transactions](#DBsent_messagesToc)
    * [sent_responses](#DBsent_responsesToc)
    * [entity_log](#DBlogToc)
* [The HPIT Server in-depth](#ServerToc)
* [Tutors in-depth](#TutorToc)
* [Entity Authorization Model](#EntityAuthToc)
* [Transactions](#TransactionToc)
* [Plugin Component Specification](#PluginToc)
    * [Echo Example](#ExPlugin)
    * [Data Connection to PSLC DataShop](#DCPlugin)
    * [Data Storage](#DSPlugin)
    * [Student Management](#SMPlugin)
        * [tutorgen.add_student](#add_student)
        * [tutorgen.get_student](#get_student)
        * [tutorgen.set_attribute](#set_attribute)
        * [tutorgen.get_attribute](#get_attribute)
        * [tutorgen.get_student_model](#get_student_model)
    * [Skill Management](#SKMPlugin)
        * [tutorgen.get_skill_name](#get_skill_name)
        * [tutorgen.get_skill_id](#get_skill_id)
        * [tutorgen.batch_get_skill_ids](#batch_get_skill_ids)
    * [Knowledge Tracing](#KTPlugin)
        * [tutorgen.kt_set_initial](#kt_set_initial)
        * [tutorgen.kt_reset](#kt_reset)
        * [tutorgen.kt_trace](#kt_trace)
        * [tutorgen.kt_batch_trace](#kt_batch_trace)
    * [Hint Factory (model tracing)](#HFPlugin)
        * [tutorgen.hf_init_problem](#hf_init_problem)
        * [tutorgen.hf_delete_state](#hf_delete_state)
        * [tutorgen.hf_push_state](#hf_push_state)
        * [tutorgen.hf_hint_exists](#hf_hint_exists)
        * [tutorgen.hf_get_hint](#hf_get_hint)
        * [tutorgen.delete_problem](#hf_delete_problem)
        * [tutorgen.get_student_model_fragment](#kt_get_student_model_fragment)
    * [Problem Management](#PMPlugin)
        * [tutorgen.add_problem](#add_problem)
        * [tutorgen.remove_problem](#remove_problem)
        * [tutorgen.get_problem](#get_problem)
        * [tutorgen.edit_problem](#edit_problem)
        * [tutorgen.list_problems](#list_problems)
        * [tutorgen.clone_problem](#clone_problem)
        * [tutorgen.add_problem_worked](#add_problem_worked)
        * [tutorgen.get_problems_worked](#get_problems_worked)
        * [tutorgen.add_step](#add_step)
        * [tutorgen.remove_step](#remove_step)
        * [tutorgen.get_step](#get_step)
        * [tutorgen.get_problem_steps](#get_problem_steps)
        * [tutorgen.get_problem_by_skill](#pm_get_problem_by_skill)
        * [tutorgen.get_student_model_fragment](#pm_get_student_model_fragment)
    * [Problem Generator](#PGPlugin)
        * [tutorgen.pg_list_problems](#list_problems)
        * [tutorgen.pg_generate_problem](#generate_problem)
    * [Data Storage Plugin](#DSPlugin)
        * [tutorgen.store_data](#store_data)
        * [tutorgen.retrieve_data](#retrieve_data)
        * [tutorgen.remove_data](#remove_data)
    * [PSLC DataShop Connection Plugin](#DCPlugin)
        * [tutorgen.get_dataset_metadata](#get_dataset_metadata)
        * [tutorgen.get_sample_metadata](#get_sample_metadata)
        * [tutorgen.get_transactions](#get_transactions)
        * [tutorgen.get_student_steps](#get_student_steps)
        * [tutorgen.add_custom_field](#add_custom_field)
    * [Boredom Detector Plugin](#BoredomPlugin)
        * [tutorgen.update_boredom](#update_boredom)
        
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
- Couchbase
- Neo4j
- Flask
- Jinja2
- WTForms
- PyMongo
- SQLAlchemy
- PyCrypto
- Requests
- uWSGI
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

Entity - A generic term for either a Plugin or Tutor.

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

`python manage.py syncdb`

Optionally index the MongoDB for faster performance with this command:

`python manage.py indexdb`

And run the tests:

`python manage.py test`

Assuming everything passed, you should then run:

`python manage.py debug`

And browse to http://127.0.0.1:8000 , where you should see a welcome page.

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
7. Sync the configuration database with sqlite. `python3 manage.py syncdb`
8. Seed the Mongo Database with `python3 manage.py mongo`
9. (optional) Setup the MongoDB Indexes for faster performance. `python3 manage.py indexdb`
10. Start the MongoDB instance with `python3 manage.py mongo`
8. Run the test suite by typing `python3 manage.py test`

To start the HPIT server type: `python3 manage.py debug` and open your browser 
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

`python manage.py syncdb`

Optionally, index the mongoDB wiht this command:

`python manage.py indexdb`

And run the tests:

`python manage.py test`

Assuming everything passed, you should then run:

`python manage.py start`

And browse to http://127.0.0.1:8000 , where you should see a welcome page.

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

`python manage.py syncdb`

Optionally index the MongoDB for faster performance, with this command:

`python manage.py indexdb`

And run the tests:

`python manage.py test`

Assuming everything passed, you should then run:

`python manage.py start`

And browse to http://127.0.0.1:8000 , where you should see a welcome page.

If you run into problems, check the section [Common Hangups](#GSCommonHangupsToc)

###<a name="GSServerSettingsToc"></a> The Settings Manager
The settings manager manages settings for the server and the pre-packages plugins that come with HPIT. The 
settings are first stored in JSON format, in a file called settings.json in the hpit_services root. When the
settings manager is imported and initialized, it will read this JSON file and load the values into a settings
object which then can be used project wide. This JSON file allows for multiple environment settings, for 
example, "test", "debug", and "production". By default, HPIT will look for the 'debug' settings but you can
override this by setting the HPIT_ENV environment variable i.e. (`export HPIT_ENV=production`). The structure 
of the file looks like this:

    json
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

Most of these settings can be left as defaults, but the important ones to change are:
* PROJECT_DIR - should be set to the directory this README is in
* VENV_DIRNAME - shoule be a relative link from PROJECT_DIR to wherever the virtual environment is.
* MONGO_DBNAME / SQLALCHEMY_DATABASE_URI - make sure these are different for test and production environments.

####server
name                        | default                                     | description                                                 | notes                        
--------------------------- | ------------------------------------------- | ----------------------------------------------------------- | -----------------------------
HPIT_VERSION                | string (really long)                        | A string representation of the current version of HPIT      |                              
DEBUG                       | False                                       | Whether to run the server in debug mode or not              | Deprecated                   
HPIT_PID_FILE               | 'tmp/hpit_server.pid'                       | Where to put the PID file for the HPIT server (daemon)      |                              
HPIT_BIND_IP                | "0.0.0.0"                                   | The IP Address to listen for connections on.                |                              
HPIT_BIND_PORT              | "8000"                                      | The Port Address to listen for connections on.              |                              
HPIT_BIND_ADDRESS           | HPIT_BIND_IP+":"+HPIT_BIND_PORT             | A combination of the IP and Port addresses                  | Don't change this.           
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
name                        | default                                           | description                                          | notes                        
--------------------------- | ------------------------------------------------- | ---------------------------------------------------- | -----------------------------------
HPIT_URL_ROOT               | "http://localhost:8000"                           | The web address for HPIT                             |
DATASHOP_ROOT_URL           | "https://pslcDataShop.web.cmu.edu/services"       | Root DataShop URL                                    |
DATASHOP_SERVICES_URL       | "http://pslc-qa.andrew.cmu.edu/DataShop/services" | DataShop URL for services                            |
MONGODB_URI                 | "mongodb://localhost:27017/"                      | The location of the Mongo database server            |
MONGO_DBNAME                | "hpit_development"                                | The name of the mongoDB database to use for plugins. |
COUCHBASE_HOSTNAME          | "127.0.0.1"                                       | Couchbase host                                       |
COUCHBASE_BUCKET_URI        | "http://127.0.0.1:8091/pools/default/buckets"     | Couchbase buckets REST endpoint                      |
COUCHBASE_AUTH              |  ["Administrator", "administrator"]               | Authentication for Couchbase server                  | Set to your server credentials
PROJECT_DIR                 | "/Users/raymond/Projects/TutorGen/hpit"           | The directory where the plugins are installed.       | Change this.

###<a name="GSCommonHangupsToc"></a> Common Hangups
Here's a list of common problems when trying to install HPIT:
* Permissions problems - if you're having troubles with permissions, make sure you are installing everything
in your user account, not root.
* Settings problems - make sure the settings are edited correctly for your system.  Verify that the paths to the
project directory and virtual environment are correct.
* Python problems - Make sure that Python, Pip, and virtualenv are all compatible with each other.
* Virtualenv problems - remember to activate your virtualenv when installing any python modules.  
* Enviornment Variable Problems - Remember to set the HPIT_ENV environment to map to the settings file.

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

The HPIT manager can be run by typing: `python3 manage.py <command> <command_args>`

Depending on the command you wish to run the arguments to that command will vary. The command
line manager for HPIT will help you along the way. For example typing just `python3 manage.py`
will give you a list of commands that manager understands. Then typing 
`python3 manage.py your_command` will show you the arguments that that command can take and a
brief overview of what that command does.

Currently the HPIT Manager has the following commands:

* `python3 manage.py start` will start all locally configured tutors, and all locally configured plugins.
* `python3 manage.py stop` will stop all locally configured tutors, and all locally configured plugins.
* `python3 manage.py assets` will compile frontend assets together into a single file to ready for production deployments.
* `python3 manage.py debug` will run the HPIT server in debug mode and WILL NOT start any plugins or tutors.
* `python3 manage.py docs` copies this documentation file to the server assets directory.
* `python3 manage.py routes` lists all the routes that the HPIT Server/Router exposes to the web.
* `python3 manage.py syncdb` syncs the data model with the administration database.(PostgreSQL or Sqlite3)
* `python3 manage.py indexdb` strategically indexes the databases, and in particular MongoDB for faster performance.
* `python3 manage.py mongo <dbpath>` Initializes MongoDB database and starts the mongoDB server.
* `python3 manage.py test` runs the suite of tests for components within HPIT.
* `python3 manage.py admin` turns a user account into an admin, or deactivate admin for a user account.

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

    json
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

### <a name="DBmessagesToc"></a> messages_and_transactions
A list of messages sent to the system before being duplicated to plugin_messages. Each message contains the following fields:

- message_name: "The type of the message. e.g. tutorgen.kt_trace"
- sender_entity_id: "The entity ID of the sender"
- payload: "The data being sent."
- time_created: "Date the message was created."

### <a name="DBpluginmesToc"></a> plugin_messages
Contains messages sent to plugins, as copied from the messages collection. It contains the following fields:

- receiver_entity_id: "The plugin that should recieve this message"
- message_name: "The type of the message. e.g. tutorgen.kt_trace"
- time_response_received: "The time the response was received (if any)"
- payload: "The data contained in this message."
- time_responded: "The time the response was created"
- time_received: "The time the message was processed by plugin"
- message_id: "The id of the message in the messages collection"
- time_created: "The time the message was created"
- sender_entity_id: "The entity ID of the sender"

### <a name="DBresponsesToc"></a> responses
Stores responses for tutors or other plugins to poll. It contains the following fields:

- response: "data for this response"
- message: "the original message"
- message_id: "The ID of the message in the messages collection"
- receiver_entity_id: "the Entity ID of the receiver"
- sender_entity_id: "The Entity ID of the sender"

### <a name="DBsent_messagesToc"></a> sent_messages_and_transactions
Stores plugin messages once they have been sent to plugin. It contains the following fields:

- receiver_entity_id: "The plugin that should recieve this message"
- message_name: "The type of the message. e.g. tutorgen.kt_trace"
- time_response_received: "The time the response was received (if any)"
- payload: "The data contained in this message."
- time_responded: "The time the response was created"
- time_received: "The time the message was processed by plugin"
- message_id: "The id of the message in the messages collection"
- time_created: "The time the message was created"
- sender_entity_id: "The entity ID of the sender"

### <a name="DBsent_responsesToc"></a> sent_responses
Store plugin responses once they have been sent to the original message sender (plugin or tutor). It contains the following fields:

- response: "data for this response"
- message: "the original message"
- message_id: "The ID of the message in the messages collection"
- receiver_entity_id: "the Entity ID of the receiver"
- sender_entity_id: "The Entity ID of the sender"
- time_response_received: "The time the response was processed"

### <a name="DBlogToc"></a> entity_log
Stores entity log information.  It contains the following fields:

- deleted: "Was this log deleted?
- log_entry: "The text of the log"
- created_on: "The date the log was created"
- entity_id: "The entity that created this log.

## <a name="ServerToc"></a> The HPIT Server in-depth

The HPIT Server is nothing more than an event-driven publish and subscribe framework, built
specifically to assist plugins and tutors to communicate via RESTful webservices. It is 
schemaless, has no pre-defined events, and is agnostic to the kinds of data it routes 
between plugins and tutors. In additon HPIT provides fundamental support for sessions,
authentication, message routing, and entity tracking.

Anyone can wrap these RESTful web services in a client side library and will be able to interact
with HPIT. We have delivered a client side library written in Python.

The server supports a variety of routes to handle the connection, polling, and transfer of 
data between HPIT entities. To get a list of these routes run the HPIT server with either 
`python3 manage.py debug` and open your browser to the HPIT administration page at 
http://localhost:8000/routes. Alternatively you can list the routes available with 
`python3 manage.py routes`

## <a name="TutorToc"></a> Tutors in-depth

A Tutor is an HPIT entity that can send messages to HPIT. A message consists of
an event name and a payload. The event name is an arbitrary string that defines what type
of message it is. Plugins register to listen to messages based on the event name. The 
message payload is an arbitrary JSON like document with data formatted based on plugin
requirements. The kinds of messages a tutor can send is defined by the plugins 
currently registered with HPIT. The HPIT server itself does not define what these 
messages look like, however HPIT does package some plugins as part of it's architecture.

For example the HPIT basic knowledge tracing plugin supports the following three events:

* tutorgen.kt_set_initial - Sets the initial values for the knowledge tracer on the KT Skill.
* tutorgen.kt_trace - Performs a knowledge tracing operation on the KT Skill.
* tutorgen.kt_reset - Resets the inital values for the knowledge tracer on the KT Skill.

Depending on the event name(eg tutorgen.kt_set_initial, or tutorgen.kt_trace) the payload 
the plugin expects will be different.

Tutors may also listen to plugin responses, and respond to them. Plugins may or may not
send a response depending on the plugin.

## <a name="ReplayToc"></a> Replay Tutors

HPIT comes with two replay tutors that are used for testing purposes.  The first is
the Replay Tutor, located in hpit/tutors/replay.py.  This tutor allows the user to
replay messages and transactions that were already sent to HPIT, essentially simulating
another tutor.  The Replay Tutor must run on the same computer as the HPIT router, as
it directly accesses the message routing database.

The Replay Tutor is usually run with a configuration in config.json along with the 
other plugins that are spun up in the HPIT environment.  The configuration should have
these parameters (along with those already necessary to run a tutor/plugin):
    - args, a dictionary of arguments, which most contain:
        - filter, an additional filter to query on
        - db_name, the name of the message routing database
        - (optional) beforeTime, specifies that messages before this time should be replayed
        - (optional) afterTime, specifies that messages after this time should be replayed
    - once, a boolean, if True, should only be run once, if false, it will continuously replay messages
    
Example configuration looks like this:
    {
        "active": false, 
        "type": "replay", 
        "args": {
            "filter": {}, 
            "db_name": "hpit_development", 
            "beforeTime": "02-11-2020 14:03:09"
        }, 
        "entity_id": "ed188aa3-a673-4482-9475-aedd981ff360", 
        "once": true, 
        "api_key": "e992a697f396a2fd99ef9910cb040fa9", 
        "name": "replay_tutor"
    }
    
Keep in mind that if the Replay Tutor has it's own entity_id, the results may vary from
what you would expect, since some plugins differentiate between senders.  In order to 
simulate another tutor, the Replay Tutor config should be set so that it uses the same
entity ID and API key as that tutor.
    
The second tutor is the Replay2 Tutor, located at hpit/tutors/replay2.py  This tutor's 
purpose is to replay PSLC Datashop transactions.  This tutor can run on any machine 
and interacts with HPIT like any other tutor would.  In order to use this plugin, 
datashop transactions must be imported.  These are in a tab delimited text format 
and can be obtained from the PSLC Datashop website.

After importing transactions, they can be selected in the GUI and sent to HPIT.  The 
responses are displayed in the bottom most text box.  It is also possible to knowledge trace
a skill and edit student attributes.  The Replay2 Tutor is good for testing existing
transactions from Datashop as well as specific functionality in some of HPIT's built in
plugins.  To run this tutor, use the command `python hpit/tutors/replay2.py`.
        
## <a name="EntityAuthToc"></a> Entity Authorization Model

When a plugin first subscribes to a new message it is now said to "own" that message type. For
example: Tutorgen owns the 'tutorgen.kt_trace' message type. We use this message internally in our
knowledge tracer. You are welcome to send 'tutorgen.kt_trace' messages from a tutor or plugin, and
our knowledge tracer will recieve the message and respond back to you with a result. However, If you 
were to write a plugin and try to subscribe to the 'tutorgen.kt_trace' message, the HPIT server 
would give you an access denied error because you don't "own" that message type. If you were curious
as to what entity "owned" a particular message, you can query the "message-owner" RESTFUL API endpoint
and we would tell you that plugin Entity ID: XXXXX owned it.

Now let's say you have a perfectly good reason to intercept a 'tutorgen.kt_trace' message, maybe you 
are a very tightly coupled partner of ours and we should give you the ability to read these messages,
we could, as the "Message Owner" can grant you access to intercept and handle messages of this type. This
is called an "Access Grant" and it is made by the owning entity when they send access grant information
to the 'share-message' RESTFUL API endpoint.

In addition to owning messages. Anyone entity can also "lock down" certain resources that they control, 
by requesting a new resource token from HPIT. In the future if that resource is attempted to be accessed
by someone you haven't given explicit permission to access, HPIT will prevent such a message from routing
through it's system. You can request new resource token with the 'new-resource' RESTFUL API endpoin.

If you want to share a resource token with another entity you can do so by sending a resource access grant
to the 'share-resource' RESTFUL API endpoint.

## <a name="TransactionToc"></a> Transactions

In HPIT, a transaction is supposed to be the smallest unit of interaction a student has with a tutor.  The
PSLC datashop uses transactions in its analysis of learning; it is the most fine grained representation of a
student's skill set.  Transactions can be generated by the student, like a key being press or an answer selected, 
or by the tutor, as in the tutor tells HPIT that the student was correct in answering a question.

Transactions act as a shortcut for the primary functionality of the main plugins in HPIT.  For example, when a 
student answers a question, they would want to tell HPIT to:

1. Get a student ID for this student, and a session
2. Add the skills to the skill manager, if they do not already exist
3. Run knowledge tracing for this set of skills
4. Record this problem in HPIT's database, if it is new to HPIT

A tutor could do this using the messages defined by HPIT's plugins, or they could send a single transaction.  That
transaction will be passed to each of the main plugins, and return the information they have gathered in a single call.  
Transactions should be the main way that tutors interact with HPIT.

A transaction requires these pieces of information:

* student_id : string - the HPIT ID of a student, usually gotten via a previous call to add_student or get_student
* session_id : string - the HPIT ID of a session, usually gotten via a previous call to add_student or get_student
* step_text : string - the unique step name
* problem_name : string - the unique problem name
* transaction_text : string - a unique string identifying the transaction 
* skill_names : dict - a mapping of skill models to skill names.  Required if using skill_ids.
* skill_ids : dict - a mapping of skill names to their IDS, usually gotten via get_skill_id.  Will be populated automatically if skill does not exist.  Should contain the same skills as skill_names.

Optional information includes:

* state : json - a hint factory state if hints are requested
* selection : string - a descriptor of the item being worked on ("text-area-1")
* action : string - the action being committed ("keypress")
* input : string - the input used ("Key-D")
* outcome : string - the result of the transaction, usually "correct", "incorrect", "hint"

Transaction Responses:

* skill_ids : dict - a dictionary mapping skill names and their IDs
* student_id : string - the ID of the student
* session_id : string - the ID of the session
* boredom_response : dict - response from the boredom detector
    * error : string - if an error occured, a message is presented here
    * bored : boolean - if the student is bored
* hf_response : dict - response from the hint factory
    * error : string - if an error occured, a message is presented here
    * hint_text : string - if hint requested, it will be here
    * hint_exists : boolean - true if hint exists
* kt_response : dict - response from the knowledge tracer
    * error : string - if an error occured, a message is presented here
    * traced_skills : dict - a dictionary of traced skills, similar to kt_trace's response
* problem_response : dict - response from the problem manager
    * error : string - if an error occured, a message is presented here
    * problem_id : string - the problem ID this transaction belongs to
    * step_id : string - the step ID this transaction belongs to
    * transaction_id : string - the ID of this transaction
* skill_response : dict - response from the skill manager
    * skill_ids : dict - a dictionary mapping skill names and their IDs
* student_response : dict - the response from the student manager
    * student_id : string - the ID of the student
    * session_id : string - the ID of the session
    

An example transaction payload looks like this:

    json
    {
        'skill_names': {
            'Unique-step': 'KC293', 
            'Default': 'same', 
            'Single-KC': 'Single-KC'
        }, 
        'outcome': 'Correct', 
        'skill_ids': {
            'KC293': '', 
            'same': '', 
            'Single-KC': ''
        }, 
        'transaction_text': '4f5cf2e1f4ecf52030f7e1916ff87f9e', 
        'student_id': '54d27f95cc48d1184cf2a80a', 
        'session_id': '54d27f95cc48d1184cf2a80b', 
        'step_text': 'formB1_1 UpdateComboBox', 
        'problem_name': 'No Feedback (ver. b 0910)-0'
    }

An example response looks like this:

    json
    {
        "boredom_response": {
            "bored": false,
            "responder": "boredom"
        },
        "hf_response": {
            "error": "'outcome' is not 'hint' for hint factory transaction.",
            "responder": "hf"
        },
        "kt_response": {
            "responder": "kt",
            "traced_skills": {
                "KC293": {
                    "probability_guess": 0.5,
                    "probability_known": 0.75,
                    "probability_learned": 0.5,
                    "probability_mistake": 0.5,
                    "skill_id": "54bd443dcc48d114c09f3cd5",
                    "student_id": "54d27f95cc48d1184cf2a80a"
                },
                "Single-KC": {
                    "probability_guess": 0.5,
                    "probability_known": 0.75,
                    "probability_learned": 0.5,
                    "probability_mistake": 0.5,
                    "skill_id": "54ad5636cc48d10b64d200c8",
                    "student_id": "54d27f95cc48d1184cf2a80a"
                },
                "same": {
                    "probability_guess": 0.5,
                    "probability_known": 0.75,
                    "probability_learned": 0.5,
                    "probability_mistake": 0.5,
                    "skill_id": "54bd443dcc48d114c09f3cd6",
                    "student_id": "54d27f95cc48d1184cf2a80a"
                }
            }
        },
        "problem_response": {
            "problem_id": "54ad5639cc48d106bc7406b0",
            "responder": "problem",
            "step_id": "54bd4440cc48d112e073f163",
            "transaction_id": "54bd4440cc48d112e073f164"
        },
        "session_id": "54d27f95cc48d1184cf2a80b",
        "skill_ids": {
            "KC293": "54bd443dcc48d114c09f3cd5",
            "Single-KC": "54ad5636cc48d10b64d200c8",
            "same": "54bd443dcc48d114c09f3cd6"
        },
        "skill_response": {
            "responder": "skill",
            "skill_ids": {
                "KC293": "54bd443dcc48d114c09f3cd5",
                "Single-KC": "54ad5636cc48d10b64d200c8",
                "same": "54bd443dcc48d114c09f3cd6"
            }
        },
        "student_id": "54d27f95cc48d1184cf2a80a",
        "student_response": {
            "responder": "student",
            "session_id": "54d27f95cc48d1184cf2a80b",
            "student_id": "54d27f95cc48d1184cf2a80a"
        }
    }



Transactions are sent by the tutor's send_transaction() method, which uses the API's /transaction endpoint.

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

####<a name="add_student"></a> tutorgen.add_student
Adds a student to the database, giving them a unique ID.

Receives:

* (optional) attributes: a JSON value of key/value pairs of attributes

Returns:

* student_id : string - the ID for the new student
* attributes : JSON - the attributes for the new student 

####<a name="get_student"></a> tutorgen.get_student
Gets an already created student from an ID.

Receives:

* student_id : string - the ID from a previously created student

Returns:

* student_id : string - the ID from a previously created student
* attributes : JSON - the attributes for the new student 

####<a name='set_attribute'></a> tutorgen.set_attribute
Sets an attribute value for a student.  Will overwrite any existing value.

Receives:

* student_id : string - the ID from a previously created student  
* attribute_name : string - the name of the attribute 
* attribute_value : string - the value of the new attribute

Returns:

* student_id : string - the ID for the student
* attributes : JSON - the attributes for the student  

####<a name="get_attribute"></a> tutorgen.get_attribute
Gets an attribute value for a student.  If the attribute does not exist, will respond
with an empty string.

Receives:

* student_id : string - the ID from a previously created student  
* attribute_name : string - the name of the attribute

Returns:

* student_id : string - the ID for the student
* (attribute_name) : string - value of the requested attribute.

####<a name = "get_student_model"></a>tutorgen.get_student_model
Get the student model for a student.  The student model is an aggregation of information from
all of the plugins that the student has interacted with.

Receives:

* student_id : string - the ID of the student
* (optional) update : boolean - whether or not the student model should be updated (True) or from cache (False).
Returns:

* student_id : string - the ID of the student
* student_model : JSON - an object containing the student model.  This will contain lists and other objects from the various plugins.
* cached : boolean - whether this model was retrieved from a cache.
* (optional) error : An error message if something went wrong of the request timed out.


##<a name="SKMPlugin"></a> Skill Management Plugin

The skill management plugin allows you to track skills across your applications
and integrates into knowledge tracing, problem selection, problem management, and
the hint factory. The skill manager identifies skills by either an assigned identifier
or by name.

####<a name="get_skill_name"></a> tutorgen.get_skill_name
Gets the name of an existing skill from an ID.

Receives:

* skill_id : string - the ID of the skill

Returns:

* skill_name : string - the name of the skill
* skill_id : string - the ID of a skill (should match sent ID)

####<a name="get_skill_id"></a> tutorgen.get_skill_id
Gets the ID of a skill from a skill name.  If the skill does not exist, it will be created.

Receives:

* skill_name : string - the name of the skill
* (optional) skill_model : string - the name of the skill model, if not supplied, assumes 'Default'  

Returns:

* skill_name : string - the name of the skill (should match what was sent)
* skill_id : string - the ID of the skill, either newly created or retrieved.
* skill_model : string - the skill model used
* cached : boolean - whether this came from the cache or database

####<a name="batch_get_skill_ids"></a> tutorgen.batch_get_skill_ids
Gets the ID for multiple skill names.  If the skill does not exist, it will be created.

Receives:

* skill_names : list - a list of string skill names
* (optional) skill_model : string - the name of the skill model, if not supplied, assumes 'Default' 

Returns:

* skill_names : list - list of the names of the skills (should match what was sent)
* skill_ids : dict - a mapping of skill names to skill ids
* skill_model : string - the skill model used
* cached : boolean - whether this came from the cache or database

##<a name="KTPlugin"></a> Knowledge Tracing Plugin
The Knowledge Tracing Plugin performs knowledge tracing on a per-student and per-skill basis.

####<a name="kt_set_initial"></a> tutorgen.kt_set_initial
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

####<a name="kt_reset"></a> tutorgen.kt_reset
Resets the probabilistic values for the knowledge tracer.

Receives:

* student_id: string - An identifier for the student.
* skill_id : string - String identifier for the skill.

Returns:

* student_id: string - An identifier for the student.
* skill_id : string - String identifier for the skill.
* probability_known : 0.5 - Probability the skill is already known
* probability_learned : 0.5 - Probability the skill will be learned
* probability_guess : 0.5 - Probability the answer is a guess
* probability_mistake : 0.5 - Probability the student made a mistake (but knew the skill)

####<a name="kt_trace"></a> tutorgen.kt_trace
Runs a knowledge tracing algorithm on the skill/tutor combination and returns the result. If
a setting doesn't exist this plugin will create one with initial values of 0.5 for each probablity.

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

####<a name="kt_batch_trace></a> tutorgen.kt_batch_trace
Runs a knowledge tracing algorithm on a collection of skills.

Receives:

* student_id: string - A string ID for the student
* skill_list : dict - A mapping of string skill IDS to boolean correct values

Returns:

* traced skills : dict - A mapping of skill ID's to their kt values (also a dict):
    * student_id: string - A string ID for the student
    * skill_id : string - String identifier for the skill.
    * probability_known : float (0.0-1.0) - Probability the skill is already known
    * probability_learned : float (0.0-1.0) - Probability the skill will be learned
    * probability_guess : float (0.0-1.0) - Probability the answer is a guess
    * probability_mistake : float (0.0-1.0) - Probability the student made a mistake (but knew the skill)

####<a name="kt_get_student_model_fragment"></a> tutorgen.get_student_model_fragment
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

####<a name="hf_init_problem"></a> tutorgen.hf_init_problem
Initializes a new problem for the hint factory.

Receives:

* start_state : string - A string representing the starting state of the problem (i.e. "2x + 4 = 12")
* goal_problem: string - A string representing the goal of the problem (i.e. "x = 4")

Returns:

* status: string - OK or NOT_OK on success and failure respectively

####<a name="hf_delete_state"></a> tutorgen.ht_delete_state
Deletes a state and all edges attached to it.

Receives:

* state : json - A json object representing the state to push.

Returns:

* status: string - either OK or NOT_OK
* error: string - an optional error message

####<a name="hf_push_state"></a> tutorgen.hf_push_state
Pushes a new state on the problem.

Receives:

* state : json - A json object representing the state to push.
* state.problem_state: string - A string representing the new state of the problem. i.e. "x = 4"
* state.steps: array of strings - A list of steps taken from the starting state to get to this state. i.e. ["Subtract 4", "Divide 2"]
* state.last_problem_state: string - What state this problem was in before this state. i.e. "2x = 8"
* state.problem: string - A string representing the problem i.e "2x + 4 = 12"

Returns:

* status: string - OK

####<a name="hf_hint_exists"></a> tutorgen.hf_hint_exists
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

####<a name="hf_get_hint"></a> tutorgen.hf_get_hint
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
* hint: dict - contains:
    * hint_text: string - The text describing the action to be taken.
    * hint_result: string - The state string the hint will take you into.
    
####<a name="hf_delete_problem"></a>tutorgen.hf_delete_problem

Receives:
* state : json - A json object representing the state to push.
* state.problem_state: string - A string representing the new state of the problem. i.e. "x = 4"
* state.steps: array of strings - A list of steps taken from the starting state to get to this state. i.e. ["Subtract 4", "Divide 2"]
* state.last_problem_state: string - What state this problem was in before this state. i.e. "2x = 8"
* state.problem: string - A string representing the problem i.e "2x + 4 = 12"

Returns:
* status: string - OK or NOT_OK
* error: string - optional, if NOT_OK and an error happened



##<a name="PMPlugin"></a> Problem Management Plugin

####<a name="add_problem"></a> tutorgen.add_problem
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

####<a name="remove_problem"></a> tutorgen.remove_problem
Remove a problem from the problem manager.

Receives:

* problem_id : string - A string identifier for the problem.

Returns:

* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed and was deleted.
* (optional) error : string - the error message if something went wrong

####<a name="get_problem"></a> tutorgen.get_problem
Gets a previously stored problem from the problem manager.

Receives:

* problem_id : string - The string identifier of the problem.

Returns:

* problem_id : string - The string identifier of the problem
* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed.
* (optional) error: string - The error message if the problem does not exist.

####<a name="edit_problem"></a> tutorgen.edit_problem
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

####<a name="list_problems"></a> tutorgen.list_problems
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

####<a name="clone_problem"></a> tutorgen.clone_problem
Clone an existing problem so that another entity can modify it.

Receives:

* problem_id : string - The string identifier to the problem to be cloned.

Returns:

* problem_id : string - The ID of the new cloned problem.
* step_ids : list - A list of string identifiers for the newly cloned steps.
* success: boolean - A boolean if everything went well.
* (optional) error : string - An error message if an error accurs, caused by not passing the correct
parameters or the requested problem doesn't exist.

####<a name="add_problem_worked"></a> tutorgen.add_problem_worked
This is used to show a student has worked on a problem.

Receives: 

* problem_id : string - The string identifier of the problem the student has worked.
* student_id : string - The string identifier of the student that worked the problem.

Returns:

* success : boolean - Whether everything went ok.
* (optional) error : string - If an error occurs, an error message.

####<a name="get_problems_worked"></a> tutorgen.get_problems_worked
Retrieves the problems a student has worked on.

Receives:

* student_id : string - the string ID of the student

Returns:

* success : boolean - whether everything went ok
* problems_worked : list - A list of problems, containing:
    * student_id : string - The ID of the student.
    * problem_id : string - The ID of the problem.

####<a name="add_step"></a> tutorgen.add_step
Adds a problem step to a problem.

Receives:

* problem_id : string - The ID of the problem
* step_text : string - The text of the problem step.

Returns:

* step_id : string - The ID of the newly created step.
* success : boolean - Whether everything went ok.
* (optional) error : string - An error message if something went wrong.

####<a name="remove_step"></a> tutorgen.remove_problem_step
Remove a problem step from the problem manager.

Receives:

* step_id : string - The ID of the step.

Returns:

* exists : boolean - True if the problem existed.
* success : boolean - True if the problem existed and was deleted.
* (optional) error : string - an error emssage if something went wrong

####<a name="get_step"></a> tutorgen.get_problem_step
Gets a previously stored problem step from the problem manager.

Receives:

* step_id : string - The ID of the step.

Returns:

* step_id : string - The ID of the step.
* step_text : string - The step's text.
* date_created : datetime - The time the step was created.
* allowed_edit_id : string - The ID of the entity that can edit this step.
* siccess : boolean - Whether everything went OK.

####<a name="get_problem_steps"></a> tutorgen.list_problem_steps
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

####<a name="pm_get_problem_by_skill"></a> tutorgen.get_problem_by_skill
Returns a dictionary of problem names and problem ID's that have skills with a certain skill.

Receives:

* skill_name : string - The name of the skill to query problems by

Returns:

* problems : dictionary - A dictionary of problem names and problem ID's that contain the skill.

####<a name="pm_get_student_model_fragment"></a> tutorgen.get_student_model_fragment
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


##<a name="PGPlugin"></a> Problem Generator Plugin
The Problem Generator Plugin is useful for randomly generating mathematics 
problems on demand. Right now, this generator is used mostly for integration 
tests between tutors and plugins. TutorGen may extend the possible set of 
problems in the future.

####<a name="list_problems"></a> tutorgen.pg_list_problems
Retrieve a list of potential problems organized by, subject, category and skill.

Receives:

* subject (optional): None or string - list categories and skills for this subject
* category (optional): None or string - list the skills for this category
* skill (optional): None or string - Does a generator for this particular skill exist?

Returns:

* json: a dict of dicts of lists organized by subjects, category and skills 

####<a name="generate_problem"></a> tutorgen.pg_generate_problem

Generates a random problem for a specific subject, category, and skill. If the subject, category
or skill doesn't have a generator associated with it, the plugin will return an error. If the subject,
category, or skill is not provided the problem generator will choose one randomly.

Recieves:

* subject (optional): string (or None) - Generate a random problem for this subject, (or random subject if None).
* category (optional): string (or None) - Generate a random problem for this category, (or random category if None).
* skill (optional): string (or None) - Generate a random problem for this skill, (or random skill if None).
* count (optional): 0 < integer <= 100 - Generate this number of random problems of this type. (between 0 and 100)

Returns:

* json: list of problems ->
    * 'subject': string - The subject this problem is mapped to.
    * 'category': string - The category this problem is mapped to.
    * 'skill': string - The skill this problem is mapped to.
    * 'problem_text': string - An ASCII textual representation of the problem.
    * 'answer_text': string or list - An ASCII textual representation of the solution or list of acceptable solutions.

Errors on invalid subject, category, or skill provided in request. Errors return as the following:

* error: string - A string representation of the error created.
* you_sent: json - A dictionary containing this parameters sent in the original request.
    * 'subject': subject,
    * 'category': category,
    * 'skill': skill,
    * 'count': count,
    * 'options': options


##<a name="DSPlugin"></a> Data Storage Plugin
The Data Storage Plugin can be used to store any kind of key value information that a plugin
or tutor may need.
####<a name="store_data"></a> tutorgen.store_data
Store a key value pair in the database.

Receives:

* key : string - the key for the data
* value: string - the value for the data

Returns:

* insert_id : string - the ID of the data object

####<a name="retrieve_data"></a> tutorgen.retrieve_data
Get a value from the database via a key.

Receives:

* key : string - the key to query.

Returns:

* data : string - the data for the key

####<a name="remove_data"></a> tutorgen.remove_data
Removes data from the database.

Receives:

* key : string - the key to remove.

Returns:

* status : string - the response from MongoDB

##<a name="DCPlugin"></a> PSLC DataShop Connection Plugin
The PSLC DataShop Connection Plugin gives basic connectivity to the PSLC DataShop.  Currently, it
only provides for a subset of functionality that they provide via their web services.

####<a name="get_dataset_metadata"></a> tutorgen.get_dataset_metadata
Gets the dataset metadata.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

####<a name="get_sample_metadata"></a> tutorgen.get_sample_metadata
Gets the metadata for a DataShop sample.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID
* sample_id : string - the string representation of a DataShop sample ID

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

####<a name="get_transactions"></a> tutorgen.get_transactions
Gets transactions from a dataset or optionally a specific sample.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID
* (optional) sample_id : string - the string representation of a DataShop sample ID

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

####<a name="get_student_steps"></a> tutorgen.get_student_steps
Gets the student steps from a dataset or optionally a specific sample.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID
* (optional) sample_id : string - the string representation of a DataShop sample ID

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.

####<a name="add_custom_field"></a> tutorgen.add_custom_field
Adds a custom field to a dataset.

Receives:

* dataset_id : string - the string representation of a DataShop dataset ID
* name : string - the name of the custom field
* description : string - the description of the custom field
* type : string - the data type.  Can be "number", "string", "date", or "big".

Returns:

* response_xml : string - the XML from the DataShop server
* status_cude : string - the HTTP request status code.


##<a name="BoredomPlugin"></a> Boredom Detector
The Boredom Detector looks at student data and determines if they may be bored.  The detector
allows for multiple different boredom detection models.  The two that exist now are "simple", which
just looks at the time difference between transactions, and "complex", which as of now does nothing 
but return true.

####<a name="update_boredom"></a> tutorgen.update_boredom
Send a student interaction to the boredom detector.

Receives:

* student_id : string - the HPIT student ID for the student we are tracking.
* return_type: string - either "bool" or "decimal", determining how the return value should look.  Defaults to "bool".

Returns:

* bored : float/boolean - Either a float probability or boolean if the student is bored, depending on return_type.
* error : string - optional, a string message of an error if it occured.

####<a name="set_boredom_model"></a> tutorgen.set_boredom_model
Change the way that the boredom detector determines if a student is bored.

Receives:

* student_id : string - the HPIT student ID for the student we are tracking.
* model_name : string - the model name, either "simple" or "complex"

Returns:

* status : string - "OK" if successful
* error : string - optional, a string message of an error if it occured.

####<a name="set_boredom_threshold">
Change the threshold of probability required to deem student is bored.

Receives:

* student_id : string - the HPIT student ID for the student we are tracking.
* threshold : float - A value between 0 and 1, inclusive.

Returns:

* status : string - "OK" if successful
* error : string - optional, a string message of an error if it occured.




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
