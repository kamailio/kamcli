import os
import sys
import click

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

kamcli_formats_list = ["raw", "json", "table", "dict"]


def read_global_config(config_paths):
    """Get config."""
    parser = configparser.SafeConfigParser()
    if config_paths:
        parser.read(config_paths)
    else:
        parser.read(["kamcli.ini"])
    return parser


#        try:
#            self.optmain.update(parser.items('main'))
#        except configparser.NoSectionError:
#            pass


def parse_user_spec(ctx, ustr):
    """Get details of the user from ustr (username, aor or sip uri)"""
    udata = {}
    if ":" in ustr:
        uaor = ustr.split(":")[1]
    else:
        uaor = ustr
    if "@" in uaor:
        udata["username"] = uaor.split("@")[0]
        udata["domain"] = uaor.split("@")[1]
    else:
        udata["username"] = uaor.split("@")[0]
        try:
            udata["domain"] = ctx.gconfig.get("main", "domain")
        except configparser.NoOptionError:
            ctx.log("Default domain not set in config file")
            sys.exit()
    if udata["username"] is None:
        ctx.log("Failed to get username")
        sys.exit()
    if udata["domain"] is None:
        ctx.log("Failed to get domain")
        sys.exit()
    udata["username"] = udata["username"].encode("ascii", "ignore").decode()
    udata["domain"] = udata["domain"].encode("ascii", "ignore").decode()
    return udata


CONTEXT_SETTINGS = dict(
    auto_envvar_prefix="KAMCLI", help_option_names=["-h", "--help"]
)

COMMAND_ALIASES = {
    "subs": "subscriber",
    "rpc": "jsonrpc",
    "sht": "htable",
}


class Context(object):
    def __init__(self):
        self.debug = False
        self.oformat = None
        self.wdir = os.getcwd()
        self.gconfig_paths = []
        self._gconfig = None

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo("(log): " + msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.debug:
            if args:
                msg %= args
            click.echo("(dbg): " + msg, file=sys.stderr)

    def printf(self, msg, *args):
        """Print a formated message to stdout."""
        if args:
            msg %= args
        click.echo(msg)

    def printnlf(self, msg, *args):
        """Print a formated message to stdout without new line."""
        if args:
            msg %= args
        click.echo(msg, nl=False)

    @property
    def gconfig(self):
        if self._gconfig is None:
            self._gconfig = read_global_config(self.gconfig_paths)
        return self._gconfig


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "commands")
)


class KamCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        if name in COMMAND_ALIASES:
            name = COMMAND_ALIASES[name]
        try:
            if sys.version_info[0] == 2:
                name = name.encode("ascii", "replace")
            mod = __import__(
                "kamcli.commands.cmd_" + name, None, None, ["cli"]
            )
        except ImportError:
            return
        return mod.cli


def global_read_config(ctx, param, value):
    """Callback that is used whenever --config is passed.  We use this to
    always load the correct config.  This means that the config is loaded
    even if the group itself never executes so our aliases stay always
    available.
    """
    if value is None:
        value = os.path.join(os.path.dirname(__file__), "kamcli.ini")
    ctx.read_config(value)
    return value


@click.command(
    cls=KamCLI,
    context_settings=CONTEXT_SETTINGS,
    short_help="Kamailio command line interface control tool",
)
@click.option(
    "--wdir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Working directory.",
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode.")
@click.option("--config", "-c", default=None, help="Configuration file.")
@click.option(
    "nodefaultconfigs",
    "--no-default-configs",
    is_flag=True,
    help="Skip loading default configuration files.",
)
@click.option(
    "oformat",
    "--output-format",
    "-F",
    type=click.Choice(kamcli_formats_list),
    default=None,
    help="Format the output",
)
@click.version_option()
@pass_context
def cli(ctx, debug, wdir, config, nodefaultconfigs, oformat):
    """Kamailio command line interface control tool.

    \b
    Help per command: kamcli <command> --help

    \b
    Default configuration files:
        - /etc/kamcli/kamcli.ini
        - ./kamcli.ini
        - ./kamcli/kamcli.ini
        - ~/.kamcli/kamctli.ini
    Configs loading order: default configs, then --config option

    \b
    License: GPLv2
    Copyright: asipto.com
    """
    ctx.debug = debug
    if wdir is not None:
        ctx.wdir = wdir
    if oformat is not None:
        ctx.oformat = oformat
    if not nodefaultconfigs:
        if os.path.isfile("/etc/kamcli/kamcli.ini"):
            ctx.gconfig_paths.append("/etc/kamcli/kamcli.ini")
        if os.path.isfile("./kamcli.ini"):
            ctx.gconfig_paths.append("./kamcli.ini")
        if os.path.isfile("./kamcli/kamcli.ini"):
            ctx.gconfig_paths.append("./kamcli/kamcli.ini")
        tpath = os.path.expanduser("~/.kamcli/kamcli.ini")
        if os.path.isfile(tpath):
            ctx.gconfig_paths.append(tpath)
    if config is not None:
        ctx.gconfig_paths.append(os.path.expanduser(config))
