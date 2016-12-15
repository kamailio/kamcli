## KAMCLI

Kamailio Command Line Interface Control Tool.

Kamailio is an open source SIP (RFC3261) server available at:

  * https://www.kamailio.org

**kamcli** is aiming at being a modern and extensible alternative to the shell script **kamctl**.

### Features

The prototype of using **kamcli** is:

```
kamcli [options] command [arguments]
```

New commands for **kamcli** can be implemented as plugins, each command being implemented in a file located in **kamcli/commands/**.

Among implemented commands:

  * **subscriber** - manage SIP subscribers
  * **ul** - manage user location records
  * **address** - manage permissions address records
  * **aliasdb** - manage database aliases
  * **speeddial** - manage speed dial records
  * **group** - manage group membership records (acl)
  * **rpc** - interact with kamailio via jsonrpc control commands
  * **stats** - get kamailio internal statistics
  * **db** - manage kamailio database content
  * **dispatcher** - manage load balancer (dispatcher)
  * **dialplan** - manage dialplan records
  * **dialog** - manage active calls (dialog)
  * **rpcmethods** - return the list of available RPC methods (commands)
  * **ps** - print the details for kamailio running processes
  * **uptime** - print the uptime for kamailio instance
  * **moni** - continuous refresh of the values for a list of statistics
  * **mtree** - manage memory trees (mtree)

Each **kamcli command** can offer many subcommands. The help for each command can be seen with:

```
kamcli command --help
```

The help for each subcommand can be seen with:

```
kamcli command subcommand --help
```

### Installation

#### Requirements

OS Packages (install via apt, yum, ...):

  * python
  * python-pip
  * python-dev (optional - needed to install mysql-python via pip)

PIP Packages (install via pip):

  * _to install in a virtual environment (see next)_
    * virtualenv
  * _extra packages requied by kamcli (part of OS or  virtual environment)_
    * click
    * sqlalchemy
    * mysql-python (optional - needed if you want to connect to MySQL database)
    * tabulate (optional - needed if you want to have table-formatted output for various commands)
    * pyaml (optional - needed if you want to print json result as yaml (more compact))

#### Install VirtualEnv

It is recommended to install in a virtual environment at least for development.
Some useful details about installing Click in virtual environament are
available at:

  * http://click.pocoo.org/4/quickstart/#virtualenv

For example, create the virtual environemnt in the folder kamclienv

```
  $ pip install virtualenv
  $ mkdir kamclienv
  $ cd kamclienv
  $ virtualenv venv
```

To activate the virtual environment:

```
  $ . venv/bin/activate
```

Clone kamcli and install it. The commands can be done inside the virtual
environment if activate to be available only there or without virtual
environment to be installed in the system.

```
  $ git clone https://github.com/asipto/kamcli.git
  $ cd kamcli
  $ pip install --editable .
```

The *pip install* command installs the dependencies appart of the
database connector module needed on top of sqlalchemy. You need to
install your wanted database module -- e.g., for MySQL use pip to
install *mysql-python*.

To deactivate the virtual environment, run:

```
  $ deactivate
```

#### Install on Debian

Should work on: Ubuntu or Mint

To get kamcli completely installed on Debian with MySQL support,
run following commands:

```
apt-get install python python-pip python-dev
pip install virtualenv
mkdir kamclienv
cd kamclienv
virtualenv venv
pip install click
pip install sqlalchemy
pip install mysql-python
pip install tabulate
pip install pyaml
git clone https://github.com/asipto/kamcli.git
cd kamcli
pip install --editable .
```

To see if all was installed properly, run:

```
kamcli --help
```

### Configuration File

Kamcli uses a configuration file with INI format. The name is kamcli.ini and it looks for it in:

  * /etc/kamcli/kamcli.ini
  * ~/.kamcli/kamcli.ini
  * the value of --config command line parameter

The installation process doesn't deploy the configuration file yet.

A sample kamailio.ini is available in sources, at kamcli/kamcli.ini

Note that not all configuration file options in kamcli.ini are used at this moment, some
values are hardcoded, being planned to be replaced with the configuration options.

### Usage

Read the help messages:

```
  $ kamcli --help
  $ kamcli <command> --help
  $ kamcli <command> <subcommand> --help
```

#### Examples of Commands

Sample commands to understand quicker the capabilities and how to use it:

```
kamcli -d --config=kamcli/kamcli.ini --help

kamcli --config=kamcli/kamcli.ini subscriber show
kamcli --config=kamcli/kamcli.ini subscriber add test test00
kamcli --config=kamcli/kamcli.ini subscriber show test
kamcli --config=kamcli/kamcli.ini subscriber show --help
kamcli -d --config=kamcli/kamcli.ini subscriber passwd test01 test10
kamcli -d --config=kamcli/kamcli.ini subscriber add -t no test02 test02
kamcli -d --config=kamcli/kamcli.ini subscriber setattrs test01 rpid +123
kamcli -d --config=kamcli/kamcli.ini subscriber setattrnull test01 rpid

kamcli -d --config=kamcli/kamcli.ini mi
kamcli -d --config=kamcli/kamcli.ini mi which
kamcli -d --config=kamcli/kamcli.ini mi get_statistics all

kamcli -d --config=kamcli/kamcli.ini jsonrpc --help
kamcli -d --config=kamcli/kamcli.ini jsonrpc core.psx
kamcli -d --config=kamcli/kamcli.ini jsonrpc system.listMethods
kamcli -d --config=kamcli/kamcli.ini jsonrpc stats.get_statistics
kamcli -d --config=kamcli/kamcli.ini jsonrpc stats.get_statistics all
kamcli -d --config=kamcli/kamcli.ini jsonrpc stats.get_statistics shmem:
kamcli -d --config=kamcli/kamcli.ini jsonrpc --dry-run system.listMethods

kamcli -d --config=kamcli/kamcli.ini config raw
kamcli -d --config=kamcli/kamcli.ini config show main db
kamcli -d --config=kamcli/kamcli.ini --no-default-configs config show main db

kamcli -d --config=kamcli/kamcli.ini db connect
kamcli -d --config=kamcli/kamcli.ini db show -F table version
kamcli -d --config=kamcli/kamcli.ini db show -F json subscriber
kamcli -d --config=kamcli/kamcli.ini db showcreate version
kamcli -d --config=kamcli/kamcli.ini db showcreate -F table version
kamcli -d --config=kamcli/kamcli.ini db showcreate -F table -S html version
kamcli -d --config=kamcli/kamcli.ini db clirun "describe version"
kamcli -d --config=kamcli/kamcli.ini db clishow version
kamcli -d --config=kamcli/kamcli.ini db clishowg subscriber


kamcli -d --config=kamcli/kamcli.ini ul showdb
kamcli -d --config=kamcli/kamcli.ini ul show
kamcli -d --config=kamcli/kamcli.ini ul rm test
kamcli -d --config=kamcli/kamcli.ini ul add test sip:test@127.0.0.1

kamcli -d --config=kamcli/kamcli.ini stats
kamcli -d --config=kamcli/kamcli.ini stats usrloc
kamcli -d --config=kamcli/kamcli.ini stats -s registered_users
kamcli -d --config=kamcli/kamcli.ini stats usrloc:registered_users
```

### License

GPLv2

Copyright: asipto.com
