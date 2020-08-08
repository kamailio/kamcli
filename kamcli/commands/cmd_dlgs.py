import click
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group("dlgs", help="Manage dlgs module (active calls stats)")
@pass_context
def cli(ctx):
    pass


@cli.command("list", short_help="Show details for dialog records in memory")
@pass_context
def dlgs_list(ctx):
    """Show details for dialog records in memory

    \b
    """
    command_ctl(ctx, "dlgs.list", [])


@cli.command("get", short_help="Get the details for the matching dialogs")
@click.argument("mkey", metavar="<mkey>")
@click.argument("mop", metavar="<mkey>")
@click.argument("mval", metavar="<mval>")
@pass_context
def dlgs_get(ctx, mkey, mop, mval):
    """Show the details for the matching dialogs

    \b
    Parameters:
        <mkey> - matching key:
          src - src attribute;
          dst - dst attribute;
          data - data attribute;
        <mop> - matching operator:
          eq - equal string comparison;
          ne - not-equal string comparison;
          re - regular expression;
          sw - starts-with
          fm - fast match
        <mval> - matching value
    """
    command_ctl(ctx, "dlgs.get", [mkey, mop, mval])
