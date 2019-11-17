## KAMCLI

Kamailio Command Line Interface Control Tool


### Development Guidelines

#### [pre-commit](https://pre-commit.com/)

  * apt install build-essentials python3-dev python3-virtualenvwrapper
  * mkvirtualenv kamcli --python=python3
  * pip install -r requirements_dev.txt
  * pre-commit install

#### Used Frameworks

Kamcli is using the following Python frameworks:

  * click - command line interface framework
    * http://click.pocoo.org
  * SQL Alchemy - connection to database
    * http://www.sqlalchemy.org
  * pyaml - yaml package used for compact printing of jsonrpc responses
  * tabulate - pretty printing of database results

#### Plugins

Kamcli prototype is:

```
kamcli <command> [params]
```

Each command is implemented as a plugin, its code residing in a single Python
file located in *kamcli/commands/*. The filename is prefixed by **cmd_**,
followed by command name and then the extension **.py**.

Development of kamcli has its starting point in the *complex* example of Click:

  * https://github.com/mitsuhiko/click/tree/master/examples/complex

Other examples provided by Click are good source of inspiration:

  * https://github.com/mitsuhiko/click/tree/master/examples

##### Adding a new command

In short, the steps for adding a new command (refered also as plugin or module):

  * create a new file file for your new comand in **kamcli/commands/** folder
  * name the file **cmd_newcommand.py**
  * define **cli(...)** function, which can be a command or group of commands

Once implemented, the new command should be immediately available as:

 ```
 kamcli newcommand ...
 ```

The commands **dispatcher** (kamcli/commands/cmd_dispatcher.py) or **address**
(kamcli/commands/cmd_address.py) can be a good reference to look at and reuse
for implementing new commands.

If the new command is executing MI or JSONRPC commands to kamailio, add the
appropriate mapping inside the **kamcli/iorpc.py** file to the variable
**COMMAND_NAMES**. The recommendation is to use the RPC command as the common
name and then map the MI variant - MI is obsoleted and scheduled to be removed.
