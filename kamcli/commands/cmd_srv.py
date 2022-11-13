import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl
import sys
import json
import subprocess


@click.group("srv", help="Common server interaction commands")
@pass_context
def cli(ctx):
    pass


@cli.command("sockets", short_help="Show the list of listen sockets")
@pass_context
def srv_sockets(ctx):
    """Show the list of listen sockets

    \b
    """
    command_ctl(ctx, "corex.list_sockets")


@cli.command("aliases", short_help="Show the list of server domain aliases")
@pass_context
def srv_aliases(ctx):
    """Show the list of server domain aliases

    \b
    """
    command_ctl(ctx, "corex.list_aliases")


@cli.command("rpclist", short_help="Show the list of server rpc commands")
@pass_context
def srv_rpclist(ctx):
    """Show the list of server rpc commands

    \b
    """
    command_ctl(ctx, "system.listMethods")


@cli.command("rpchelp", short_help="Show the help text for rpc command")
@click.argument("command", metavar="<command>")
@pass_context
def srv_rpchelp(ctx, command):
    """Show the help text for rpc command

    \b
    """
    command_ctl(ctx, "system.methodHelp", [command])


@cli.command("info", short_help="Show server info")
@pass_context
def srv_info(ctx):
    """Show server info

    \b
    """
    command_ctl(ctx, "core.info")


@cli.command("modules", short_help="Show server loaded modules")
@pass_context
def srv_modules(ctx):
    """Show server loaded modules

    \b
    """
    command_ctl(ctx, "core.modules")


@cli.command("version", short_help="Show server version")
@pass_context
def srv_version(ctx):
    """Show server version

    \b
    """
    command_ctl(ctx, "core.version")


@cli.command("ppdefines", short_help="Show pre-processor defines")
@click.option(
    "full", "--full", is_flag=True, help="Show full format of the records."
)
@pass_context
def srv_ppdefines(ctx, full):
    """Show pre-processor defines

    \b
    """
    if full:
        command_ctl(ctx, "core.ppdefines_full")
    else:
        command_ctl(ctx, "core.ppdefines")


@cli.command("shm", short_help="Show shared memory details")
@pass_context
def srv_shm(ctx):
    """Show shared memory details

    \b
    """
    command_ctl(ctx, "core.shmmem")


@cli.command("debug", short_help="Control debug level of the server")
@pass_context
@click.argument("level", metavar="<level>", nargs=-1, type=int)
def srv_debug(ctx, level):
    """Control debug level of the server

    \b
    Parameters:
        <level> - new debug level (optional)
    """
    if not level:
        command_ctl(ctx, "corex.debug")
    else:
        command_ctl(ctx, "corex.debug", [level[0]])


@cli.command("runinfo", short_help="Show runtime info")
@pass_context
def srv_runinfo(ctx):
    """Show runtime info

    \b
    """
    proc = subprocess.Popen(
        sys.argv[0] + " -F json rpc --no-log core.version",
        stdout=subprocess.PIPE,
        shell=True,
    )
    (output, err) = proc.communicate(timeout=10)
    proc.wait(timeout=10)
    if err is None and len(output) > 32:
        jdata = json.loads(output)
        click.echo("running: " + jdata["result"])

        proc = subprocess.Popen(
            sys.argv[0] + " -F json rpc --no-log core.uptime",
            stdout=subprocess.PIPE,
            shell=True,
        )
        (output, err) = proc.communicate(timeout=10)
        proc.wait(timeout=10)
        if err is None and len(output) > 32:
            jdata = json.loads(output)
            uph = int(jdata["result"]["uptime"] / 3600)
            upm = int((jdata["result"]["uptime"] % 3600) / 60)
            ups = (jdata["result"]["uptime"] % 3600) % 60
            click.echo(
                "uptime: " + str(uph) + "h " + str(upm) + "m " + str(ups) + "s"
            )
