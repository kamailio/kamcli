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


@cli.command("stats", short_help="Show pipelimit stats")
@pass_context
def pipelimit_stats(ctx):
    """Show pipelimit stats

    \b
    """
    command_ctl(ctx, "pl.stats", [])


@cli.command("set-pipe", short_help="Set pipe algorithm and limit")
@click.argument("pipeid", metavar="<pipeid>")
@click.argument("alg", metavar="<alg>")
@click.argument("limit", metavar="<limit>")
@pass_context
def pipelimit_set_pipe(ctx, pipeid, alg, limit):
    """Show pipelimit stats

    \b
    Parameters:
        <pipeid> - pipe name id
        <alg> - pipe algorithm
        <limit> - pipe limit
    """
    command_ctl(ctx, "pl.set_pipe", [pipeid, alg, limit])
