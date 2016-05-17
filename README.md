# Syncano command line tool

## Installation
``pip install syncano-cli``

## Usage

First you need to login into your account
``syncano login``

It will ask you for your email and password and store account key in
${HOME}/.syncano file. You can also override account key with --key option.

### Pulling your instance classes and scripts.

In order to pull your instance configuration you can execute
``syncano pull <instance_name>``

This will fetch all Classes and Scripts into current working directory, and
store configuration in syncano.yml file. If you want to pull only selected
classes/scripts you can add -c/--class or -s/--script option eg.

``syncano pull -c Class1 -c Class2 -s script_label_1 -s "script label 2" my_instance``

Scripts source code is stored in scripts subdirectory, and names are based on
script labels. Keep in mind that script labels in syncano are not unique, and
this tools can't handle this kind of situation.

Classes and Scripts configuration is stored in syncano.yml file. If file
syncano.yml already exists only classes and scripts stored in this file, will
be pulled and updated. If you want to pull whole instance you can use -a/--all
flag.

### Pushing your changes.

When you have made some changes to syncano.yml or some script source code you
can push the changes to syncano using

``syncano push <instance_name>``

It will push only changes newer then last synchronization time. This time is
recorded using .sync file last modification time. If syncano.yml has changed
it will try to push all data to syncano. Otherwise it will just push changed
source code files for scripts. If you want to force push all changes you can
use -a/--all option.

If you want to just push selected classes/scripts changes you can provide them
with -c/--class or -s/--script options like in the pull example above.
