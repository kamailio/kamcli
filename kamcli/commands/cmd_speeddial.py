import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec


@click.group(
    "speeddial",
    help="Manage speed dial records",
    short_help="Manage speed dial records",
)
@pass_context
def cli(ctx):
    pass


@cli.command("add", short_help="Add a speed dial record")
@click.option(
    "table",
    "--table",
    default="speed_dial",
    help="Name of database table (default: speed_dial)",
)
@click.option(
    "fname",
    "--fname",
    default="",
    help='Value for fname column (default: "")',
)
@click.option(
    "lname",
    "--lname",
    default="",
    help='Value for lname column (default: "")',
)
@click.argument("userid", metavar="<userid>")
@click.argument("shortdial", metavar="<shortdial>")
@click.argument("targeturi", metavar="<targeturi>")
@click.argument("desc", metavar="<desc>", nargs=-1)
@pass_context
def speeddial_add(ctx, table, fname, lname, userid, shortdial, targeturi, desc):
    """Add a speed dial record

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <shortdial> - username, AoR or SIP URI for short dial
        <targeturi> - username, AoR or SIP URI for target
        [<desc>] - description for speed dial record
    """
    udata = parse_user_spec(ctx, userid)
    sdata = parse_user_spec(ctx, shortdial)
    tdata = parse_user_spec(ctx, targeturi)
    ctx.vlog(
        "Adding for user [%s@%s] short dial [%s@%s] target [sip:%s@%s]",
        udata["username"],
        udata["domain"],
        sdata["username"],
        sdata["domain"],
        tdata["username"],
        tdata["domain"],
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    uri = "sip:{}@{}".format(tdata["username"], tdata["domain"])
    if not desc:
        e.execute(
            "insert into {0} (username, domain, sd_username, "
            "sd_domain, new_uri, fname, lname) values ({1!r}, {2!r}, {3!r}, "
            "{4!r}, {5!r}, {6!r}, {7!r})".format(
                table,
                udata["username"],
                udata["domain"],
                sdata["username"],
                sdata["domain"],
                uri,
                fname,
                lname,
            )
        )
    else:
        e.execute(
            "insert into {0} (username, domain, sd_username, "
            "sd_domain, new_uri, fname, lname, description) values ({1!r}, {2!r}, {3!r}, "
            "{4!r}, {5!r}, {6!r}, {7!r}, {8!r})".format(
                table,
                udata["username"],
                udata["domain"],
                sdata["username"],
                sdata["domain"],
                uri,
                fname,
                lname,
                desc,
            )
        )


@cli.command("rm", short_help="Remove speed dial records")
@click.option(
    "table",
    "--table",
    default="speed_dial",
    help="Name of database table (default: speed_dial)",
)
@click.argument("userid", metavar="<userid>")
@click.argument("shortdial", metavar="<shortdial>", nargs=-1)
@pass_context
def speeddial_rm(ctx, table, userid, shortdial):
    """Remove a user from groups (revoke privilege)

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <shortdial> - username, AoR or SIP URI for short dial
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log(
        "Removing speed dial for record [%s@%s]",
        udata["username"],
        udata["domain"],
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if not shortdial:
        e.execute(
            "delete from {0} where username={1!r} and domain={2!r}".format(
                table, udata["username"], udata["domain"],
            )
        )
    else:
        for s in shortdial:
            sdata = parse_user_spec(ctx, s)
            e.execute(
                "delete from {0} where username={1!r} and domain={2!r} "
                "and sd_username={3!r} and sd_domain={4!r}".format(
                    table,
                    udata["username"],
                    udata["domain"],
                    sdata["username"],
                    sdata["domain"],
                )
            )


@cli.command("show", short_help="Show speed dial records")
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
    "table",
    "--table",
    default="speed_dial",
    help="Name of database table (default: speed_dial)",
)
@click.argument("userid", metavar="[<userid>]")
@click.argument("shortdial", nargs=-1, metavar="[<shortdial>]")
@pass_context
def speeddial_show(ctx, oformat, ostyle, table, userid, shortdial):
    """Show details for speed dial records

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for user or alias
        [<shortdial>] - username, AoR or SIP URI for short dial (optional)
    """
    udata = parse_user_spec(ctx, userid)
    e = create_engine(ctx.gconfig.get("db", "rwurl"))

    ctx.vlog(
        "Showing speed dial records for user [%s@%s]",
        udata["username"],
        udata["domain"],
    )
    if not shortdial:
        res = e.execute(
            "select * from {0} where username={1!r} and domain={2!r}".format(
                table, udata["username"], udata["domain"],
            )
        )
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for s in shortdial:
            sdata = parse_user_spec(ctx, s)
            res = e.execute(
                "select * from {0} where username={1!r} and domain={2!r} "
                "and sd_username={3!r} and sd_domain={4!r}".format(
                    table,
                    udata["username"],
                    udata["domain"],
                    sdata["username"],
                    sdata["domain"],
                )
            )
            ioutils_dbres_print(ctx, oformat, ostyle, res)
