import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group(
    "pipelimit",
    help="Manage pipelimit module",
    short_help="Manage pipelimit module",
)
@pass_context
def cli(ctx):
    pass


@cli.command("list", short_help="Lists the details of one or all pipes")
@click.argument("pipeid", nargs=-1, metavar="[<pipeid>]")
@pass_context
def pipelimit_list(ctx, pipeid):
    """Show details for dialog records in memory

    \b
    Parameters:
        [<pipeid>] - pipe name id
    """
    if not pipeid:
        command_ctl(ctx, "pl.list", [])
    else:
        for p in pipeid:
            command_ctl(ctx, "pl.list", [p])
