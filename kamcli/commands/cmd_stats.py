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
@click.option(
    "number",
    "--number",
    "-n",
    is_flag=True,
    help="The stats values are retrieved in number format",
)
@click.argument("names", nargs=-1, metavar="[<name>]")
@pass_context
def cli(ctx, single, number, names):
    """Print internal statistics

        \b
        Parameters:
            - [<name>]  - name of statistic or statistics group
                        - if missing, all statistics are printed
                        - it can be a list of names
    """
    rcmd = "stats.fetch"
    if number:
        rcmd = "stats.fetchn"
    if names:
        for n in names:
            if n.endswith(":"):
                # enforce group name by ending with ':'
                command_ctl(ctx, rcmd, [n])
            elif n.find(":") > 0:
                # get only stat name, when providing 'group:stat'
                command_ctl(ctx, rcmd, [n.split(":")[1]])
            elif single:
                # single stat name flag
                command_ctl(ctx, rcmd, [n])
            else:
                # default is group name
                command_ctl(ctx, rcmd, [n + ":"])
    else:
        # no name, print all
        command_ctl(ctx, rcmd, ["all"])
