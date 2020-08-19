import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group(
    "domain",
    help="Manage domain module (multi-domain records)",
    short_help="Manage domain module",
)
@pass_context
def cli(ctx):
    pass


@cli.command("add", short_help="Add a new domain")
@click.argument("domain", metavar="<domain>")
@pass_context
def domain_add(ctx, domain):
    """Add a new domain

    \b
    Parameters:
        <domain> - domain value
    """
    ctx.vlog("Adding a new domain [%s]", domain)
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "insert into domain (domain) values ({0!r})".format(
            domain.encode("ascii", "ignore").decode()
        )
    )


@cli.command("rm", short_help="Remove a record from domain table")
@click.argument("domain", metavar="<domain>")
@pass_context
def domain_rm(ctx, domain):
    """Remove a a record from db domain table

    \b
    Parameters:
        <domain> - domain value
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "delete from domain where domain={0!r}".format(
            domain.encode("ascii", "ignore").decode()
        )
    )


##
#
#
@cli.command("showdb", short_help="Show domain records in database")
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
@click.argument("domain", nargs=-1, metavar="[<domain>]")
@pass_context
def domain_showdb(ctx, oformat, ostyle, domain):
    """Show details for records in domain table

    \b
    Parameters:
        [<domain>] - domain value (optional)
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if not domain:
        ctx.vlog("Showing all domain records")
        res = e.execute("select * from domain")
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for d in domain:
            ctx.vlog("Showing a specific domain record")
            res = e.execute('select * from domain where domain="%s"', d)
            ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command("list", short_help="Show details for domain records in memory")
@pass_context
def domain_list(ctx):
    """Show details for domain records in memory

    \b
    """
    command_ctl(ctx, "domain.dump", [])


@cli.command(
    "reload", short_help="Reload domain records from database into memory"
)
@pass_context
def domain_reload(ctx):
    """Reload domain records from database into memory

    \b
    """
    command_ctl(ctx, "domain.reload", [])
