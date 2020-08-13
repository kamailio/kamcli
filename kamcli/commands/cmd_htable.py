import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group("htable", help="Management of htable module")
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
    """Reload the content from database for hash table named htname

    \b
    Parameters:
        <htname> - the name of hash table
    """
    command_ctl(ctx, "htable.reload", [htname])


@cli.command(
    "store",
    short_help="Write the content to database for hash table named htname",
)
@click.argument("htname", metavar="<htname>")
@pass_context
def htable_store(ctx, htname):
    """Store the content to database for hash table named htname

    \b
    Parameters:
        <htname> - the name of hash table
    """
    command_ctl(ctx, "htable.stored", [htname])


@cli.command(
    "list-tables", short_help="List the hash tables",
)
@pass_context
def htable_list_tables(ctx):
    """List the hash tables

    \b
    """
    command_ctl(ctx, "htable.listTables", [])


@cli.command(
    "stats", short_help="Print statistics for hash tables",
)
@pass_context
def htable_stats(ctx):
    """Print statistics for hash tables

    \b
    """
    command_ctl(ctx, "htable.stats", [])


@cli.command("db-add", short_help="Add a new htable record to database")
@click.option(
    "dbtname",
    "--dbtname",
    default="htable",
    help='Database table name (default: "htable")',
)
@click.option(
    "colkeyname",
    "--colkeyname",
    default="key_name",
    help='Column name for key name (default: "key_name")',
)
@click.option(
    "colkeyvalue",
    "--colkeyvalue",
    default="key_value",
    help='Column name for value (default: "key_value")',
)
@click.argument("dbtname", metavar="<dbtname>")
@click.argument("keyname", metavar="<keyname>")
@click.argument("keyvalue", metavar="<keyvalue>")
@pass_context
def htable_dbadd(ctx, dbtname, colkeyname, colkeyvalue, keyname, keyvalue):
    """Add a new htable record in database table

    \b
    Parameters:
        <keyname> - key name
        <keyvalue>  - associated value for key name
    """
    ctx.vlog(
        "Adding to htable [%s] record [%s] => [%s]", dbtname, keyname, keyvalue
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    dbname = dbtname.encode("ascii", "ignore").decode()
    col_kname = colkeyname.encode("ascii", "ignore").decode()
    col_kvalue = colkeyvalue.encode("ascii", "ignore").decode()
    kname = keyname.encode("ascii", "ignore").decode()
    kvalue = keyvalue.encode("ascii", "ignore").decode()

    e.execute(
        "insert into {0!r} ({1!r}, {2!r}) values ({3!r}, {4!r})".format(
            dbname, col_kname, col_kvalue, kname, kvalue
        )
    )


@cli.command("db-rm", short_help="Remove a record from htable database")
@click.option(
    "dbtname",
    "--dbtname",
    default="htable",
    help='Database table name (default: "htable")',
)
@click.option(
    "colkeyname",
    "--colkeyname",
    default="key_name",
    help='Column name for prefix (default: "key_name")',
)
@click.argument("keyname", metavar="<keyname>")
@pass_context
def htable_dbrm(ctx, dbtname, colkeyname, keyname):
    """Remove a record from htable database table

    \b
    Parameters:
        <keyname> - key name to match the record
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "delete from {0!r} where {1!r}={2!r}".format(
            dbtname.encode("ascii", "ignore").decode(),
            colkeyname.encode("ascii", "ignore").decode(),
            keyname.encode("ascii", "ignore").decode(),
        )
    )
