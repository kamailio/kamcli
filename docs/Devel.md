## KAMCLI

Kamailio Command Line Interface Control Tool


### Development Guidelines

#### Indentation

  * user 4 whitespaces for indentation

#### Plugins

Development of kamcli has its starting point in the *complex* example of Click:

  * https://github.com/mitsuhiko/click/tree/master/examples/complex

Other examples provided by Click are good source of inspiration:

  * https://github.com/mitsuhiko/click/tree/master/examples

In short, thttps://github.com/mitsuhiko/click/tree/master/exampleshe steps for adding a plugin:

  * add you new comand in kamcli/commands/ folder
  * name the file cmd_newcommand.py
  * define cli(...) function, which can be a command or group of commands

