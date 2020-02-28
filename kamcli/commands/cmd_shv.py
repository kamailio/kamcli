import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group("shv", help="Management of $shv(name) variables")
@pass_context
def cli(ctx):
    pass


@cli.command("get", short_help="Get the value for $shv(name)")
@click.argument("name", nargs=-1, metavar="<name>")
@pass_context
def shv_get(ctx, name):
    """Get the value for $shv(name)

    \b
    Parameters:
        <name> - the name of shv variable
    """
    if not name:
        command_ctl(ctx, "pv.shvGet")
    else:
        for n in name:
            command_ctl(ctx, "pv.shvGet", [n])


@cli.command("sets", short_help="Set $shv(name) to string value")
@click.argument("name", metavar="<name>")
@click.argument("sval", metavar="<sval>")
@pass_context
def shv_sets(ctx, name, sval):
    """Set $shv(name) to string value

    \b
    Parameters:
        <name> - the name of shv variable
        <sval> - the string value
    """
    command_ctl(ctx, "pv.shvSet", [name, "str", sval])


@cli.command("seti", short_help="Set $shv(name) to int value")
@click.argument("name", metavar="<name>")
@click.argument("ival", metavar="<ival>", type=int)
@pass_context
def srv_seti(ctx, name, ival):
    """Set $shv(name) to int value

    \b
    Parameters:
        <name> - the name of shv variable
        <ival> - the int value
    """
    command_ctl(ctx, "pv.shvSet", [name, "int", ival])
