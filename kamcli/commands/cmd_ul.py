import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.ioutils import ioutils_formats_list
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec
from kamcli.iorpc import command_ctl


@click.group(
    "ul",
    help="Manage user location records",
    short_help="Manage user location records",
)
@pass_context
def cli(ctx):
    pass


@cli.command("show", short_help="Show details for location records in memory")
@click.option(
    "brief", "--brief", is_flag=True, help="Show brief format of the records."
)
@click.option(
    "table",
    "--table",
    default="location",
    help="Name of location table (default: location)",
)
@click.argument("userid", nargs=-1, metavar="[<userid>]")
@pass_context
def ul_show(ctx, brief, table, userid):
    """Show details for location records in memory

    \b
    Parameters:
        [<userid>] - username, AoR or SIP URI for subscriber
                   - it can be a list of userids
                   - if not provided then all records are shown
    """
    if not userid:
        ctx.vlog("Showing all records")
        if brief:
            command_ctl(ctx, "ul.dump", ["brief"])
        else:
            command_ctl(ctx, "ul.dump", [])
    else:
        for u in userid:
            udata = parse_user_spec(ctx, u)
            ctx.vlog(
                "Showing record for [%s@%s]",
                udata["username"],
                udata["domain"],
            )
            aor = udata["username"] + "@" + udata["domain"]
            command_ctl(ctx, "ul.lookup", [table, aor])


@cli.command("add", short_help="Add location record")
@click.option(
    "table",
    "--table",
    default="location",
    help="Name of location table (default: location)",
)
@click.option(
    "expires", "--expires", type=int, default=0, help="Expires value"
)
@click.option("qval", "--q", type=float, default=1.0, help="Q value")
@click.option("cpath", "--path", default="", help="Path value")
@click.option("flags", "--flags", type=int, default=0, help="Flags value")
@click.option(
    "bflags", "--bflags", type=int, default=0, help="Branch flags value"
)
@click.option(
    "methods", "--methods", type=int, default=4294967295, help="Methods value"
)
@click.argument("userid", nargs=1, metavar="<userid>")
@click.argument("curi", nargs=1, metavar="<contact-uri>")
@pass_context
def ul_add(
    ctx, table, expires, qval, cpath, flags, bflags, methods, userid, curi
):
    """Add location record

    \b
    Parameters:
        <userid>       - username, AoR or SIP URI for subscriber
        <contact-uri>  - contact SIP URI
    """
    udata = parse_user_spec(ctx, userid)
    ctx.vlog("Adding record for [%s@%s]", udata["username"], udata["domain"])
    aor = udata["username"] + "@" + udata["domain"]
    command_ctl(
        ctx,
        "ul.add",
        [table, aor, curi, expires, qval, cpath, flags, bflags, methods],
    )


@cli.command("rm", short_help="Delete location records")
@click.option(
    "table",
    "--table",
    default="location",
    help="Name of location table (default: location)",
)
@click.argument("userid", nargs=1, metavar="<userid>")
@click.argument("curi", nargs=-1, metavar="[<contact-uri>]")
@pass_context
def ul_rm(ctx, table, userid, curi):
    """Show details for location records in memory

    \b
    Parameters:
        <userid>         - username, AoR or SIP URI for subscriber
        [<contact-uri>]  - contact SIP URI
                         - optional, it can be a list of URIs
    """
    udata = parse_user_spec(ctx, userid)
    ctx.vlog("Showing record for [%s@%s]", udata["username"], udata["domain"])
    aor = udata["username"] + "@" + udata["domain"]
    if curi:
        for c in curi:
            command_ctl(ctx, "ul.rm", [table, aor, c])
    else:
        command_ctl(ctx, "ul.rm", [table, aor])


@cli.command(
    "showdb", short_help="Show details for location records in database"
)
@click.option(
    "oformat",
    "--output-format",
    "-F",
    type=click.Choice(ioutils_formats_list),
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
@click.argument("userid", nargs=-1, metavar="[<userid>]")
@pass_context
def ul_showdb(ctx, oformat, ostyle, userid):
    """Show details for location records in database

    \b
    Parameters:
        [<userid>] - username, AoR or SIP URI for subscriber
                   - it can be a list of userids
                   - if not provided then all records are shown
    """
    if not userid:
        ctx.vlog("Showing all records")
        e = create_engine(ctx.gconfig.get("db", "rwurl"))
        res = e.execute("select * from location")
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for u in userid:
            udata = parse_user_spec(ctx, u)
            ctx.vlog(
                "Showing records for [%s@%s]",
                udata["username"],
                udata["domain"],
            )
            e = create_engine(ctx.gconfig.get("db", "rwurl"))
            res = e.execute(
                "select * from location where username={0!r} and domain={1!r}".format(
                    udata["username"], udata["domain"],
                )
            )
            ioutils_dbres_print(ctx, oformat, ostyle, res)
