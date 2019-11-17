import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command("uptime", short_help="Print the uptime for kamailio")
@pass_context
def cli(ctx):
    """Print the uptime for kamailio

    \b
    Show time details since kamailio was started.
    """
    command_ctl(ctx, "core.uptime", [])
