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

```
  $ kamcli --help
  $ kamcli <command> --help
  $ kamcli <command> <subcommand> --help
```

### License

GPLv2

Copyright: asipto.com
