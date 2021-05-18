## KAMCLI ##

Kamailio Command Line Interface Control Tool.

Kamailio is an open source SIP (RFC3261) server available at:

  * https://www.kamailio.org

**kamcli** is aiming at being a modern and extensible alternative to the shell script **kamctl**.

It requires that `jsonrpcs` module of Kamailio is loaded and configured to listen
on a Unix domain socket, UDP socket or FIFO file. The way to interact with Kamailio has to be set
inside `kamcli` config file (kamcli.ini).

### Features ####

The tool provides sub-commands for managing many Kamailio modules and their
database records. The can be run in one shot from terminal or via the embedded
interactive shell (which can be started with `kamcli shell` - see the
corresponding section).

The prototype of using **kamcli** is:

```
kamcli [options] command [arguments]
```

New commands for **kamcli** can be implemented as plugins, each command being
implemented in a file located in **kamcli/commands/**.

Among implemented commands:

  * **acc** - manage accounting records
  * **address** - manage permissions address records
  * **aliasdb** - manage database aliases
  * **avp** - manage avp user preferences
  * **config** - manage configuration file for kamcli
  * **db** - manage kamailio database content
  * **dialog** - manage active calls (dialog)
  * **dialplan** - manage dialplan records
  * **dispatcher** - manage load balancer (dispatcher)
  * **domain** - manage domain records
  * **dlgs** - manage dlgs module
  * **group** - manage group membership records (acl)
  * **htable** - manage htable module
  * **moni** - continuous refresh of the values for a list of statistics
  * **mtree** - manage memory trees (mtree)
  * **pike** - manage pike module
  * **ping** - send OPTIONS request
  * **pkg** - private memory (pkg) management
  * **ps** - print the details for kamailio running processes
  * **pstrap** - store runtime details and gdb backtraces for running processes with ps
  * **rpc** - interact with kamailio via jsonrpc control commands (alias of jsonrpc)
  * **rpcmethods** - return the list of available RPC methods (commands)
  * **rtpengine** - manage RTPEngine records and instances
  * **shell** - run in interactive shell mode
  * **shm** - shared memory (shm) management
  * **shv** - manage $shv(name) variables
  * **sipreq** - send SIP request via RPC command
  * **speeddial** - manage speed dial records
  * **srv** - server management commands (sockets, aliases, ...)
  * **stats** - get kamailio internal statistics
  * **subscriber** - manage SIP subscribers
  * **tcp** - management commands for TCP connections
  * **tls** - management commands for TLS profiles and connections
  * **trap** - store runtime details and gdb backtraces for running processes
  * **uacreg** - manage uac remote registration records
  * **ul** - manage user location records
  * **uptime** - print the uptime for kamailio instance

Each **kamcli command** can offer many subcommands. The help for each command can be seen with:

```
kamcli command --help
```

The help for each subcommand can be seen with:

```
kamcli command subcommand --help
```

### Installation ####

#### Requirements ####

OS Packages (install via apt, yum, ...):

  * python3 (python version 3.x, recommended at least Python 3.7)
  * python3-pip
  * python3-setuptools
  * python3-dev (optional - needed to install mysqlclient via pip)
  * python3-venv (optional - needed to install virtual environment)

PIP Packages (run inside `kamcli` folder):

```
  $ pip3 install -r requirements/requirements.txt
```

#### MySQL Backend ####

Extra PIP Packages (install via pip3):

* _extra packages requied by kamcli (part of OS or virtual environment)_
  * mysqlclient (optional - needed if you want to connect to MySQL database)

```
  $ pip3 install mysqlclient
```


Notes:
  * it may require to install `libmysqlclient-dev` to for getting
    Python `mysqlclient` extension
  * `mysql` cli tool is used by some `db` subcommands


#### PostgreSQL Backend ####

* _extra packages requied by kamcli (part of OS or virtual environment)_
  * psycopg2 (optional - needed if you want to connect to PostgreSQL database)

```
  $ pip3 install psycopg2
```

```
# on some OSes it may require to install `psycopg2-binary`
  $ pip3 install psycopg2-binary
```

Notes:
  * it may require to install `libpq-dev` to for getting
    Python `psycopg2` extension
  * `psql` cli tool is used by some `db` subcommands


#### SQLite Backend ####

No extra Python package needs to be installed, it is included in the core language extensions.

Notes:
  * it may require to install `sqlite3` tool if wanted to execute `kamcli db ...`
  cli specific subcommands.

#### Install In Virtual Environment ####

It is recommended to install in a virtual environment at least for development.
Some useful details about installing Click in virtual environment are
available at:

  * http://click.pocoo.org/4/quickstart/#virtualenv

For example, create the virtual environment in the folder venv:

```
  $ apt install python3-venv
  $ mkdir kamclienv
  $ cd kamclienv
  $ python3 -m venv venv
```

To activate the virtual environment:

```
  $ . venv/bin/activate
```

Clone `kamcli` and install it. The commands can be done inside the virtual
environment if activate to be available only there or without virtual
environment to be installed in the system.

```
  $ git clone https://github.com/kamailio/kamcli.git
  $ cd kamcli
  $ pip3 install -r requirements/requirements.txt
  $ pip3 install mysqlclient
  $ pip3 install --editable .
```

The above commands install the MySQL driver. The command `pip3 install mysqlclient`
can be skipped if no need for database connectivity, or install the PostgreSQL
driver, if that type of database is used. The *pip3 install* command installs the
dependencies appart of the database connector module needed on top of sqlalchemy,
therefore the database driver has to be installed explicitely with `pip3`.

To deactivate the virtual environment, run:

```
  $ deactivate
```

#### Install On Debian ####

Should work also on: Ubuntu or Mint

Note: you may have to replace python with python3 and pip with pip3 in package
names, installation and execution commands.

To get `kamcli` completely installed on Debian with MySQL support,
run following commands:

```
apt-get install python3 python3-pip python3-setuptools python3-dev
cd /usr/local/src/
git clone https://github.com/kamailio/kamcli.git
cd kamcli
pip3 install -r requirements/requirements.txt
pip3 install mysqlclient
pip3 install .
```

To see if all was installed properly, run:

```
kamcli --help
```

**Tip**: install configuration file in the user home directory:

```
cd /usr/local/src/kamcli
sudo kamcli config install -u
```

Edit `/root/.kamcli/kamcli.ini` or `/home/$USER/.kamcli/kamcli.ini` and update
the config values as needed.

#### Install On CentOS ####

Should work also on other RPM-based distros.

Note: you may have to replace python with python3 and pip with pip3 in package
names, installation and execution commands.

To get `kamcli` installed on CentOS with MySQL support,
run following commands:

```
yum install python3 python3-devel python3-pip python3-setuptools
cd /usr/local/src/
git clone https://github.com/kamailio/kamcli.git
cd kamcli
pip3 install -r requirements/requirements.txt
pip3 install mysqlclient
pip3 install .
```

To see if all was installed properly, run:

```
kamcli --help
```

**Tip**: install configuration file in the user home directory:

```
cd /usr/local/src/kamcli
sudo kamcli config install -u
```

Edit `/root/.kamcli/kamcli.ini` or `/home/$USER/.kamcli/kamcli.ini` and update
the config values as needed.

### Configuration File ###

Kamcli uses a configuration file with INI format. The name is `kamcli.ini` and it looks for it in:

  * `./kamcli/kamcli.ini`
  * `./kamcli.ini`
  * `/etc/kamcli/kamcli.ini`
  * `~/.kamcli/kamcli.ini`
  * the value of `-c` or `--config` command line parameter

All the configuration files that are found are loaded in the order listed above. To load
only one configuration file, use `-n` parameter together with `-c /path/to/kamcli.ini`.

A sample kamailio.ini is available in sources, at `kamcli/kamcli.ini`.

The installation process does not automatically deploy the configuration file.

To install the global configuration file, run the next command in the source directory:

```
kamcli config install
```

It installs the sample configuration file in `/etc/kamcli/kamcli.ini`.

To install user specific configuration file, run the next command in the source directory:

```
kamcli config install -u
```

It installs the sample configuration file in `~/.kamcli/kamcli.ini`.

Note: not all configuration file options in `kamcli.ini` are used at this moment, some
values are hardcoded, being planned to be replaced with the configuration options.

### Usage ###

Read the help messages:

```
  $ kamcli --help
  $ kamcli <command> --help
  $ kamcli <command> <subcommand> --help
```

### Interactive Shell Mode ###

`kamcli` can offer an internal interactive shell when running:

```
kamcli shell
```

To exit the internal shell type `:q`, or run `:h` to see the internal shell help.

The internal shell keeps persistent history of commands (stored in `~/.kamcli/history`)
and has auto-completion of `kamcli` options and sub-commands as one starts typing.

Using `<TAB>` pops up the auto-completion suggestions.

The cli prompt line has syntax highlighting and keyboard bindings similar to `bash`:

  * `CTRL + A` - go to start of line
  * `CTRL + E` - go to end of line
  * `CTRL + D` - exit the shell session
  * `CTRL + L` - clear the screen
  * `CTRL + U` - clear the line before the cursor
  * `CTRL + K` - clear the line after the cursor
  * `CTRL + R` - search through previously used commands
  * `CTRL + W` - delete the word before the cursor

Long commands can be remapped to shorter names via configuration file
`[cmd_shell.cmdremap]` section, like in the next example:

```
[cmd_shell.cmdremap]
dv=db show "version"
```

Executing `dv` inside the interactive shell prints the result of command
`db show "version"`.

### Examples Of Commands ###

Sample commands to understand quicker the capabilities and how to use it:

```
kamcli -d --help
kamcli -d --config=kamcli/kamcli.ini --help

kamcli subscriber show
kamcli subscriber add test test00
kamcli subscriber show test
kamcli subscriber show --help
kamcli -d subscriber passwd test01 test10
kamcli -d subscriber add -t no test02 test02
kamcli -d subscriber setattrs test01 rpid +123
kamcli -d subscriber setattrnull test01 rpid

kamcli -d jsonrpc --help
kamcli -d jsonrpc core.psx
kamcli -d jsonrpc system.listMethods
kamcli -d jsonrpc stats.get_statistics
kamcli -d jsonrpc stats.get_statistics all
kamcli -d jsonrpc stats.get_statistics shmem:
kamcli -d jsonrpc --dry-run system.listMethods

kamcli -d config raw
kamcli -d config show main db
kamcli -d -no-default-configs config show main db

kamcli -d db connect
kamcli -d db show -F table version
kamcli -d db show -F json subscriber
kamcli -d db showcreate version
kamcli -d db showcreate -F table version
kamcli -d db showcreate -F table -S html version
kamcli -d db clirun "describe version"
kamcli -d db clishow version
kamcli -d db clishowg subscriber


kamcli -d ul showdb
kamcli -d ul show
kamcli -d ul rm test
kamcli -d ul add test sip:test@127.0.0.1

kamcli -d stats
kamcli -d stats usrloc
kamcli -d stats -s registered_users
kamcli -d stats usrloc:registered_users
```

### Kamailio Configuration ###

It requires to load the `jsonrpcs` module in `kamalilio.cfg` and enable the
FIFO or UnixSocket transports (they should be enabled by default).

```
loadmodule "jsonrpcs.so"

# ----- jsonrpcs params -----
# - explicit enable of fifo and unixsocket transports
modparam("jsonrpcs", "transport", 6)
# - pretty format for output
modparam("jsonrpcs", "pretty_format", 1)
```

### Database Backend Support ###

When using `Kamailio` with a database backend and want `kamcli` to manage it, then update
configuration file `kamcli.ini` and set the attributes in the section `[db]`. Couple of
these attributes (e.g., database name) can be also provided as cli parameters for some
`kamcli db ...` sub-commands.

Note: of course, it requires to install the Python extension to connect to the type of
database to be used, as well as the cli tools for the database type, see the sections
related to installation for specific details.

One of the most important steps when using `Kamailio` with database backend is the creation
of the database and its tables. That can be done with:

```
kamcli db create
```

By default, when applicable, this command creates database access users and grants the
appropriate privileges. This behaviour can be controlled via cli parameters.

To create the database tables, `kamcli` needs to know where creation scripts are located.
For example, when using MySQL for a Kamailio instance installed from sources, the path is:

  * /usr/local/share/kamailio/mysql

This has to be set to `scriptsdirectory` attribute in `[db]` section of `kamcli.ini`, or given
via `-s` (or `--scripts-directory`) command line parameter. It can also point to the corresponding
folder in the source code tree, for example:

```
kamcli db create -s /usr/local/src/kamailio-dev/utils/kamctl/mysql
```

### Development ###

Notes about setting up development environment and guidelines to add new commands are inside the
[docs/Devel.md](docs/Devel.md) file.

### Python2 Support ###

The current version of `kamcli` works only with Python3. Python2 has been deprecated
and removed from major Linux distributions.

To run `kamcli` with Python2.x, use the git branch `v1.2-python2`. The branch will be kept
for a while, but likely there will be no new features added to it.

### License ###

GPLv2

Copyright: asipto.com
