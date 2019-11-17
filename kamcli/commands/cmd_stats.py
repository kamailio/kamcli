import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command("stats", short_help="Print internal statistics")
@click.option(
    "single",
    "--single",
    "-s",
    is_flag=True,
    help="The name belong to one statistic (otherwise the name is "
    "for a group)",
)
@click.argument("names", nargs=-1, metavar="[<name>]")
@pass_context
def cli(ctx, single, names):
    """Print internal statistics

        \b
        Parameters:
            - [<name>]  - name of statistic or statistics group
                        - if missing, all statistics are printed
                        - it can be a list of names
    """
    if names:
        for n in names:
            if n.endswith(":"):
                # enforce group name by ending with ':'
                command_ctl(ctx, "stats.get_statistics", [n])
            elif n.find(":") > 0:
                # get only stat name, when providing 'group:stat'
                command_ctl(ctx, "stats.get_statistics", [n.split(":")[1]])
            elif single:
                # single stat name flag
                command_ctl(ctx, "stats.get_statistics", [n])
            else:
                # default is group name
                command_ctl(ctx, "stats.get_statistics", [n + ":"])
    else:
        # no name, print all
        command_ctl(ctx, "stats.get_statistics", ["all"])
