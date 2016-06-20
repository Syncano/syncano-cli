Syncano command line tool
=========================

Installation
------------

::

    pip install syncano-cli

Usage
-----

First you need to login into your account

::

    syncano login

It will ask you for your email and password and store account key in
${HOME}/.syncano file. You can also override account key with --key option.

Pulling your instance classes and scripts
-----------------------------------------

In order to pull your instance configuration you can execute

::

    syncano sync pull <instance_name>

This will fetch all Classes and Scripts into current working directory, and
store configuration in syncano.yml file. If you want to pull only selected
classes/scripts you can add -c/--class or -s/--script option eg.

::

    syncano sync pull -c Class1 -c Class2 -s script_label_1 -s "script label 2" my_instance

Scripts source code is stored in scripts subdirectory, and names are based on
script labels. Keep in mind that script labels in syncano are not unique, and
this tools can't handle this kind of situation.

Classes and Scripts configuration is stored in syncano.yml file. If file
syncano.yml already exists only classes and scripts stored in this file, will
be pulled and updated. If you want to pull whole instance you can use -a/--all
flag.

Pushing your changes
--------------------

When you have made some changes to syncano.yml or some script source code you
can push the changes to syncano using

::

    syncano sync push <instance_name>

It will push only changes newer then last synchronization time. This time is
recorded using .sync file last modification time. If syncano.yml has changed
it will try to push all data to syncano. Otherwise it will just push changed
source code files for scripts. If you want to force push all changes you can
use -a/--all option.

If you want to just push selected classes/scripts changes you can provide them
with -c/--class or -s/--script options like in the pull example above.

Synchronization of changes in realtime
--------------------------------------

There is also an option to synchronize your project live. When you change
syncano.yml or some script source code pointed to by syncano.yml your changes
will be automatically pushed to syncano.

::

    syncano sync watch

This command will push all your project configuration to syncano and will
wait for changes made to project files. When it detects file modification
it will push those changes to syncano.


Syncano Parse migration tool
============================

This tool will help you to move your data from Parse to Syncano.

Usage
-----

Currently supports only transferring data. This tool takes the Parse schemas and transform them to Syncano classes.
Next step is to move all of the data between Parse and Syncano. The last step is rebuilding the relations between
objects.


Configuration
-------------

::

    syncano migrate configure

Will run the configuration that will ask you for the following variables:

* PARSE_MASTER_KEY: the master key of your PARSE account;
* PARSE_APPLICATION_ID: the application ID of the application that you want to transfer;
* SYNCANO_ADMIN_API_KEY: Syncano Account Key;
* SYNCANO_INSTANCE_NAME: the Syncano instance name to which the transfer will be made;

`syncano migrate configure` command will take following parameters:

* -c (--current) which will display the current configuration;
* -f (--force) which allow to override the previously set configuration; 

The configuration will be stored in your home directory in .syncano file under the P2S section. 
It's used to call the Parse API and Syncano API as well.

Run migration
------------
 
::

    syncano migrate parse

This command will run the synchronization process between Parse and Syncano. Sit comfortably in your chair and read
the output.

Tips & Troubleshooting
----------------------

1. This tool currently does not support checking if some object is already present in the Syncano instance,
   so if sync is run twice the end results is that data is duplicated. To avoid such cases,
   simply remove your instance in using Syncano dashboard;

2. The process can be quite slow - it's because of the throttling on both sides: Parse and Syncano on free accounts 
   (which is the bottom boundary for scripts);

3. If you encounter any problems, have some improvements proposal or just wanna talk,
   please write me: sebastian.opalczynski@syncano.com;

4. The Syncano can be found on - please do not hesitate to ask for help or share your thoughts;

* Github: 
    * https://github.com/Syncano/
* Gitter:
    * https://gitter.im/Syncano/community
    * https://gitter.im/Syncano/community-pl
* Slack: 
    * http://syncano-community.github.io/slack-invite/


Running scripts
===============

This command will allow you to execute any script (Script Endpoint) with optional payload and read the output.

Usage:

::

    syncano execute <instance_name> <script_endpoint_name> --payload="<payload_in_JSON_format>"
