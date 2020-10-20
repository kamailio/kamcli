import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
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


@cli.command("db-add", short_help="Add a new pipelimit record to database")
@click.option(
    "dbtname",
    "--dbtname",
    default="pl_pipes",
    help='The name of database table (default: "pl_pipes")',
)
@click.option(
    "alg",
    "--alg",
    default="taildrop",
    help='The name of the algorithm (default: "taildrop")',
)
@click.argument("pipeid", metavar="<pipeid>")
@click.argument("limit", metavar="<limit>", type=click.INT)
@pass_context
def pipelimit_dbadd(ctx, dbtname, alg, pipeid, limit):
    """Add a new pipelimit record in database table

    \b
    Parameters:
        <pipeid> - pipe name id
        <limit> - pipe limit
    """
    ctx.vlog(
        "Adding to pipelimit table [%s] record: [%s] [%s] [%s]",
        dbtname,
        pipeid,
        limit,
        alg,
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    dbtval = dbtname.encode("ascii", "ignore").decode()
    pidval = pipeid.encode("ascii", "ignore").decode()
    algval = alg.encode("ascii", "ignore").decode()
    e.execute(
        "insert into {0} (pipeid, algorithm, plimit) values ({1!r}, {2!r}, {3})".format(
            dbtval, pidval, algval, limit
        )
    )


@cli.command("db-show", short_help="Show pipelimit records in database")
@click.option(
    "oformat",
    "--output-format",
    "-F",
    type=click.Choice(["raw", "json", "table", "dict"]),
    default=None,
    help="Format the output",
)
@click.option(
    "ostyle",
    "--output-style",
    "-S",
    default=None,
    help="Style of the output (tabulate table format)",
)
@click.option(
    "dbtname",
    "--dbtname",
    default="pl_pipes",
    help='The name of database table (default: "pl_pipes")',
)
@click.argument("pipeid", nargs=-1, metavar="[<pipeid>]")
@pass_context
def pipelimit_dbshow(ctx, oformat, ostyle, dbtname, pipeid):
    """Show details for records in pipelimit database table

    \b
    Parameters:
        <pipeid> - pipe name id (optional)
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if not pipeid:
        ctx.vlog("Showing all pipelimit database records")
        res = e.execute(
            "select * from {0}".format(
                dbtname.encode("ascii", "ignore").decode()
            )
        )
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for p in pipeid:
            ctx.vlog(
                "Showing pipelimit database records for pipeid {0}".format(p)
            )
            res = e.execute(
                "select * from {0} where pipeid={1!r}".format(
                    dbtname.encode("ascii", "ignore").decode(),
                    p.encode("ascii", "ignore").decode(),
                )
            )
            ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command("db-rm", short_help="Remove a record from pipelimit table")
@click.option(
    "dbtname",
    "--dbtname",
    default="pl_pipes",
    help='The name of database table (default: "pl_pipes")',
)
@click.argument("pipeid", metavar="<pipeid>")
@pass_context
def pipelimit_dbrm(ctx, dbtname, pipeid):
    """Remove a record from pipelimit database table

    \b
    Parameters:
        <dbtname> - name of pipelimit database table
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "delete from {0} where pipeid={1!r}".format(
            dbtname.encode("ascii", "ignore").decode(),
            pipeid.encode("ascii", "ignore").decode(),
        )
    )


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
@click.argument("limit", metavar="<limit>", type=click.INT)
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
