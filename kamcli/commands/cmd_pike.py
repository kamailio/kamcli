import click
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group("pike", help="Manage pike module (source IP tracking)")
@pass_context
def cli(ctx):
    pass


@cli.command("list", short_help="Show the details of tracked IP addresses")
@pass_context
def pike_list(ctx):
    """Show details for dialog records in memory

    \b
    """
    command_ctl(ctx, "pike.list", [])
