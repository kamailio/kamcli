import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group("htable", help="Management of $shv(name) variables")
@pass_context
def cli(ctx):
    pass


@cli.command("list", short_help="List the content of hash table named htname")
@click.argument("htname", metavar="<htname>")
@pass_context
def htable_list(ctx, htname):
    """List the content of hash table named htname

    \b
    Parameters:
        <htname> - the name of hash table
    """
    command_ctl(ctx, "htable.dump", [htname])


@cli.command("get", short_help="Get the value for $sht(htname=>itname)")
@click.argument("htname", metavar="<htname>")
@click.argument("itname", nargs=-1, metavar="<itname>")
@pass_context
def htable_get(ctx, htname, itname):
    """Get the value for $sht(htname=>itname)

    \b
    Parameters:
        <htname> - the name of hash table
        <itname> - the name of item
    """
    if not itname:
        command_ctl(ctx, "htable.dump", [htname])
    else:
        for itn in itname:
            command_ctl(ctx, "htable.get", [htname, itn])


@cli.command("sets", short_help="Set $sht(htname=>itname) to string value")
@click.argument("htname", metavar="<htname>")
@click.argument("itname", metavar="<itname>")
@click.argument("sval", metavar="<sval>")
@pass_context
def htable_sets(ctx, htname, itname, sval):
    """Set $sht(htname=>itname) to string value

    \b
    Parameters:
        <htname> - the name of hash table
        <itname> - the name of item
        <sval> - the string value
    """
    command_ctl(ctx, "htable.sets", [htname, itname, sval])


@cli.command("seti", short_help="Set $sht(htname=>itname) to int value")
@click.argument("htname", metavar="<htname>")
@click.argument("itname", metavar="<itname>")
@click.argument("ival", metavar="<ival>", type=int)
@pass_context
def htable_seti(ctx, htname, itname, ival):
    """Set $sht(htname=>itname) to int value

    \b
    Parameters:
        <htname> - the name of hash table
        <itname> - the name of item
        <ival> - the int value
    """
    command_ctl(ctx, "htable.seti", [htname, itname, ival])


@cli.command("rm", short_help="Remove the item $sht(htname=>itname)")
@click.argument("htname", metavar="<htname>")
@click.argument("itname", metavar="<itname>")
@pass_context
def htable_rm(ctx, htname, itname):
    """Remove the item $sht(htname=>itname)

    \b
    Parameters:
        <htname> - the name of hash table
        <itname> - the name of item
    """
    command_ctl(ctx, "htable.delete", [htname, itname])


@cli.command(
    "flush", short_help="Remove all the content of hash table named htname"
)
@click.argument("htname", metavar="<htname>")
@pass_context
def htable_flush(ctx, htname):
    """Remove all the content of hash table named htname

    \b
    Parameters:
        <htname> - the name of hash table
    """
    command_ctl(ctx, "htable.flush", [htname])


@cli.command(
    "reload",
    short_help="Reload the content from database for hash table named htname",
)
@click.argument("htname", metavar="<htname>")
@pass_context
def htable_reload(ctx, htname):
    """Remove the content from database for hash table named htname

    \b
    Parameters:
        <htname> - the name of hash table
    """
    command_ctl(ctx, "htable.reload", [htname])
