Syncano command line tool
=========================

Table of contents
=================

1.  `Build Status`_
2.  `Installation`_
3.  `Documentation`_
4.  `Registration`_
5.  `Instances`_
6.  `Syncano sync`_
7.  `Syncano Parse migration tool`_
8.  `Syncano Hosting`_
9.  `Custom Sockets`_
10.  `Config`_
11.  `Running Scripts`_
12.  `Issues`_

Build Status
============

**Master**

.. image:: https://circleci.com/gh/Syncano/syncano-cli/tree/master.svg?style=svg
    :target: https://circleci.com/gh/Syncano/syncano-cli/tree/master

**Develop**

.. image:: https://circleci.com/gh/Syncano/syncano-cli/tree/develop.svg?style=svg
    :target: https://circleci.com/gh/Syncano/syncano-cli/tree/develop

Installation
============

To install Syncano CLI tool::

    pip install syncano-cli

**Usage:**

First you need to login into your Syncano account

::

    syncano login --instance-name patient-resonance-4283

It will ask you for your email and password. After successfully logging in your Account Key (admin key) 
will be stored in *${HOME}/.syncano* file. You can also override an Account Key later with *--key* option.

The Instance name will be set as default and used in all CLI commands.

If you want to override this setting for a specific command, use --instance-name eg::

    syncano sync --instance-name new-instance-1234 pull
    
If you need to change default Instance name, used for all future commands, use::

    syncano default name_of_new_default_instance


If you do not have an Syncano account use `syncano init` command::

    syncano init

And follow the steps. CLI will ask you about `email` and `password`, it will also create an Instance for you.
After `syncano init` you can start with getting the list of your Instances::

    syncano instances list


To obtain a help, type::

    syncano --help

To display a help for specific command, type::

    syncano instances --help

And::

    syncano instances list --help


Documentation
=============

You can read detailed documentation `here <docs/README.md>`_.


Registration
============

You can register into Syncano using CLI::

    syncano register my_email@example.com

You will be asked about password in prompt. Provide it. When you see the information about successful registration
- you can start using CLI.

The following options can be used (but this is not obligatory)::

    --first-name        # this is your first name;
    --last-name         # this is yout last name;
    --invitation-key    # the invitation key if someone invite you to using Syncano;


When registration is successful - the `api_key` will be set in CLI config - and it's ready to use. The next step should
be - creating an Instance - please see below.


Instances
=========

**How CLI handles connection?**

Almost each (except some `global` commands - like register) CLI command will send a request to the Syncano Instance.
To handle this properly - you can specify --instance-name when login (if you already have one). This Instance will be
used in all API calls then. You can check which Instance is `default` by listing the instances::

    syncano instances list

In the output - if the Instance is default - there will be a `(default)` string near the instance name.

The Instance name can be also overwritten on particular call::

    syncano sockets --instance-name my_custom_instance list

Eg.: if your default Instance is `my_instance_name` and you run above command - the Custom Sockets from instance
`my_custom_instance` will be displayed, and again::

    syncano sockets list

Will display Custom Sockets from `my_instance_name` - because it is set to be a default one.

After a registration - there's no default Instance set. So it's desired to create one and set it as default::

    syncano instances create my_new_instance
    syncano instances default my_new_instance

It's worth to note that `instance_name` must be unique - but you will get appropriate message if you encounter such case.

CLI provides an interface for managing Instances. The commands are:

- Instance create::

    syncano instances create my_instance_name

- Instance list::

    syncano instances list

- Instance delete::

    syncano delete my_instance_name

- Instance details::

    syncano details my_instance_name

- Set Instance as default for using in CLI commands::

    syncano default my_instance_name

In delete and details argument `my_instance_name` - can be omitted, the default Instance will be used.
Deletion will ask you for confirmation - as deleting an Instance is quite a big thing.

Syncano sync
============

Pulling your Instance classes and scripts
-----------------------------------------

In order to pull your Instance configuration, execute

::

    syncano sync pull

This will fetch all Classes and Scripts into the current working directory, and
store configuration in *syncano.yml* file. If you want to pull only selected
classes/scripts you can add *-c/--class* or *-s/--script* option e.g.

::

    syncano sync pull -c Class1 -c Class2 -s script_label_1 -s "script label 2"

The Scripts' source code is stored in the scripts subdirectory. Their names are based on
script labels. Keep in mind that script labels in Syncano are not unique, and
this tool cannot yet handle this kind of situation when pulling a Script from Syncano.

Classes and Scripts configuration is stored in *syncano.yml* file. If this file already 
exists, only classes and scripts stored in this file will be pulled and updated. 
If you want to pull the whole Instance you can use *-a/--all* switch flag.

Pushing your changes
--------------------

After you have made changes to *syncano.yml* or any of the script's source code, 
you can push the changes to Syncano using

::

    syncano sync push

It will push only changes newer than the last synchronization time. 
As last synchronization time we use *.sync* file last modification time. 
If *syncano.yml* has changed, it will try to push all data to Syncano. Otherwise, 
it will just push the source code files for scripts that were changed. 
If you want to force push all changes you can use *-a/--all* option.

If you only want to push changes from selected classes/scripts you can provide them
with *-c/--class* or *-s/--script* options like in the pull example above.

Synchronize changes in real-time
--------------------------------

There is an option to synchronize your project in real-time. When you change
syncano.yml or the source code of a script described in *syncano.yml*, your changes
will be automatically pushed to Syncano.

::

    syncano sync watch

This command will push all of your project's configuration to Syncano and will
wait for changes made to project files. When it detects that any file was modified,
it will push those changes to Syncano.


Syncano Parse migration tool
============================

This tool will help you to move your data from Parse to Syncano.

**Usage:**

Currently supports only transferring data. This tool takes the Parse schemas and transforms them to Syncano classes.
The next step is to move all of the data between Parse and Syncano. The last step is rebuilding the relations between
objects.


Configuration
-------------

::

    syncano migrate configure

Will run the configuration that will ask you for the following variables:

* PARSE_MASTER_KEY: the master key of your PARSE account;
* PARSE_APPLICATION_ID: the application ID of the application that you want to transfer;
* SYNCANO_ADMIN_API_KEY: Syncano Account Key;
* SYNCANO_INSTANCE_NAME: the Syncano Instance name to which the transfer will be made;

`syncano migrate configure` command will take following parameters:

* -c (--current) which will display the current configuration;
* -f (--force) which allow to override the previously set configuration; 

The configuration will be stored in your home directory in the .syncano file under the P2S section. 
It's used to call the Parse API and Syncano API as well.

Run migration
-------------
 
::

    syncano migrate parse

This command will run the synchronization process between Parse and Syncano. Sit back, relax, and read
the output.

Tips & Troubleshooting
----------------------

1. This tool currently does not support checking if an object is already present in the Syncano Instance.
   If the sync is run twice, the data will be duplicated. To avoid this,
   simply remove your Instance using Syncano dashboard;

2. The whole process can be quite slow because of the throttling on both sides: Parse and Syncano on free trial accounts (which is the bottom boundary for scripts);

Syncano Hosting
===============

Syncano Hosting is a simple way to host your static files on Syncano servers. 
The CLI supports it in the following way:

This command will list currently defined Hosting Sockets in the Instance::

    syncano hosting list

This command will list files for currently hosted website (for `default` Hosting Socket)::

    syncano hosting list files

This command will publish all files inside *<base_dir>* to the default Syncano Hosting Instance.
When publishing the whole directory, the structure will be mapped on Syncano.::

    syncano hosting publish <base_dir>


This command will permamently delete the Hosting Socket::

    syncano hosting delete

This command will delete the specified file::

    syncano hosting delete hosting/file/path

This command will update single file::

    syncano hosting update hosting/file/path local/file/path

For each of the above command you can specify the domain to change just after `hosting` command, example::

    syncano hosting --domain staging publish <base_dir>

Will create a new Hosting Socket which will be available under: `<instance_name>--staging.syncano.site`
If this Hosting Socket is also a default one, it will be available under: `<instance_name>.syncano.site`.


Custom Sockets
==============

This is a list of commands available for Custom Sockets. 
If you want to know more about Custom Sockets, `read the detailed docs here <docs/custom_sockets/docs.md>`_.

To install a Custom Socket from a local file::

    syncano sockets install /path/to/dir

To install a Custom Socket from a URL::

    syncano sockets install https://web.path.to/your.file

List all Custom Sockets::

    syncano sockets list

List all defined endpoints (for all Custom Sockets)::

    syncano sockets list endpoints

Display chosen Custom Socket details::

    syncano sockets details socket_name

Display Custom Socket config (with name: `socket_name`)::

    syncano sockets config socket_name

Delete a Custom Socket::

    syncano sockets delete socket_name

Create a template from a template stored in Syncano CLI::

    syncano sockets template /path/to/output_dir

Create a template from an existing Custom Socket::

    syncano sockets template /path/to/out --socket socket_name

Run endpoint defined in Custom Socket::

    syncano sockets run socket_name/endpoint_name

Run endpoint providing POST data::

    syncano sockets run socket_name/my_endpoint_12 POST -d one=1


In all of the above cases you can override the Syncano Instance being used::

    --instance-name my_instance_name

eg.::

    syncano sockets --instance-name my_instance_name run socket_name/my_endpoint_12 POST -d one=1

Providing the Instance name this way will override the default instance name
defined during initial setup (*syncano login --instance-name my_instance*)


Config
======

To display current Instance config::

    syncano config

To add variable with name `name` and value `value` to the config::

    syncano config add name value

To modify existing config variable::

    syncano config modify name value

To delete existing config variable::

    syncano config delete name

Running Scripts
===============

This command will allow you to execute any Script Endpoint with optional payload and read the output.

**Usage:**

::

    syncano execute <instance_name> <script_endpoint_name> -d key=value


Issues
======

1. If you encounter any problems, have some improvement ideas or just wanna talk,
   please write to me directly: sebastian.opalczynski@syncano.com;

2. Syncano team can be reached in multiple ways. Please do not hesitate to ask for help or share your thoughts. You can find us on:

* Github: 
    * https://github.com/Syncano/
* Slack: 
    * http://syncano-community.github.io/slack-invite/
* Gitter:
    * https://gitter.im/Syncano/community
    * https://gitter.im/Syncano/community-pl
* Support e-mail:
    * `support@syncano.io <mailto:support@syncano.io>`_
