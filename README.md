## KAMCLI

Kamailio Command Line Interface Control Tool

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
  $ git clone ...
  $ cd kamcli
  $ pip install --editable .
```

To deactivate the virtual environment, run:

```
  $ deactivate
```

### Usage

Read the help messages:

```
  $ kamcli --help
  $ kamcli <command> --help
  $ kamcli <command> <subcommand> --help
```

#### Examples of Commands

```
kamcli -v --config=kamcli/kamcli.ini --help

kamcli --config=kamcli/kamcli.ini subscriber show
kamcli --config=kamcli/kamcli.ini subscriber add test test00
kamcli --config=kamcli/kamcli.ini subscriber show test
kamcli --config=kamcli/kamcli.ini subscriber show --help
kamcli -v --config=kamcli/kamcli.ini subscriber passwd test01 test10
kamcli -v --config=kamcli/kamcli.ini subscriber add -t no test02 test02
kamcli -v --config=kamcli/kamcli.ini subscriber setattrs test01 rpid +123
kamcli -v --config=kamcli/kamcli.ini subscriber setattrnull test01 rpid

kamcli -v --config=kamcli/kamcli.ini mi
kamcli -v --config=kamcli/kamcli.ini mi which
kamcli -v --config=kamcli/kamcli.ini mi get_statistics all

kamcli -v --config=kamcli/kamcli.ini jsonrpc --help
kamcli -v --config=kamcli/kamcli.ini jsonrpc core.psx
kamcli -v --config=kamcli/kamcli.ini jsonrpc system.listMethods
kamcli -v --config=kamcli/kamcli.ini jsonrpc stats.get_statistics
kamcli -v --config=kamcli/kamcli.ini jsonrpc stats.get_statistics all
kamcli -v --config=kamcli/kamcli.ini jsonrpc stats.get_statistics shmem:
kamcli -v --config=kamcli/kamcli.ini jsonrpc --dry-run system.listMethods

kamcli -v --config=kamcli/kamcli.ini config raw
kamcli -v --config=kamcli/kamcli.ini config show main db
kamcli -v --config=kamcli/kamcli.ini --no-default-configs config show main db

kamcli -v --config=kamcli/kamcli.ini db connect
kamcli -v --config=kamcli/kamcli.ini db show -F table version
kamcli -v --config=kamcli/kamcli.ini db show -F json subscriber
kamcli -v --config=kamcli/kamcli.ini db showcreate version
kamcli -v --config=kamcli/kamcli.ini db showcreate -F table version
kamcli -v --config=kamcli/kamcli.ini db showcreate -F table -S html version
kamcli -v --config=kamcli/kamcli.ini db clirun "describe version"
kamcli -v --config=kamcli/kamcli.ini db clishow version
kamcli -v --config=kamcli/kamcli.ini db clishowg subscriber


kamcli -v --config=kamcli/kamcli.ini ul showdb
kamcli -v --config=kamcli/kamcli.ini ul show
kamcli -v --config=kamcli/kamcli.ini ul rm test
kamcli -v --config=kamcli/kamcli.ini ul add test sip:test@127.0.0.1

kamcli -v --config=kamcli/kamcli.ini stats
kamcli -v --config=kamcli/kamcli.ini stats usrloc
kamcli -v --config=kamcli/kamcli.ini stats -s registered_users
kamcli -v --config=kamcli/kamcli.ini stats usrloc:registered_users
```

### License

GPLv2

Copyright: asipto.com
