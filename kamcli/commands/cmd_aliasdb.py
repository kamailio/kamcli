import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec


@click.group("aliasdb", help="Manage database user aliases")
@pass_context
def cli(ctx):
    pass


@cli.command("add", short_help="Add a user-alias pair")
@click.option(
    "table",
    "--table",
    default="dbaliases",
    help="Name of database table (default: dbaliases)",
)
@click.argument("userid", metavar="<userid>")
@click.argument("aliasid", metavar="<aliasid>")
@pass_context
def aliasdb_add(ctx, table, userid, aliasid):
    """Add a user-alias pair into database

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <aliasid> - username, AoR or SIP URI for alias
    """
    udata = parse_user_spec(ctx, userid)
    adata = parse_user_spec(ctx, aliasid)
    ctx.vlog(
        "Adding user [%s@%s] with alias [%s@%s]",
        udata["username"],
        udata["domain"],
        adata["username"],
        adata["domain"],
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "insert into " + table + " (username, domain, alias_username, "
        "alias_domain) values (%s, %s, %s, %s)",
        udata["username"],
        udata["domain"],
        adata["username"],
        adata["domain"],
    )


@cli.command("rm", short_help="Remove records for a user and/or alias")
@click.option(
    "table",
    "--table",
    default="dbaliases",
    help="Name of database table (default: dbaliases)",
)
@click.option(
    "matchalias",
    "--match-alias",
    is_flag=True,
    help="Match userid value as alias (when given one argument)",
)
@click.argument("userid", metavar="<userid>")
@click.argument("aliasid", metavar="<aliasid>", nargs=-1)
@pass_context
def aliasdb_rm(ctx, table, matchalias, userid, aliasid):
    """Remove a user from groups (revoke privilege)

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <aliasid> - username, AoR or SIP URI for alias (optional)
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log(
        "Removing alias for record [%s@%s]", udata["username"], udata["domain"]
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if not aliasid:
        if matchalias:
            e.execute(
                "delete from " + table + " where alias_username=%s and "
                "alias_domain=%s",
                udata["username"],
                udata["domain"],
            )
        else:
            e.execute(
                "delete from " + table + " where username=%s and domain=%s",
                udata["username"],
                udata["domain"],
            )
    else:
        for a in aliasid:
            adata = parse_user_spec(ctx, a)
            e.execute(
                "delete from " + table + " where username=%s and domain=%s "
                "and alias_username=%s and alias_domain=%s",
                udata["username"],
                udata["domain"],
                adata["username"],
                adata["domain"],
            )


@cli.command("show", short_help="Show user aliases")
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
    default="dbaliases",
    help="Name of database table (default: dbaliases)",
)
@click.option(
    "matchalias",
    "--match-alias",
    is_flag=True,
    help="Match userid value as alias",
)
@click.argument("userid", nargs=-1, metavar="[<userid>]")
@pass_context
def aliasdb_show(ctx, oformat, ostyle, table, matchalias, userid):
    """Show details for user aliases

    \b
    Parameters:
        [<userid>] - username, AoR or SIP URI for user or alias
                   - it can be a list of userids
                   - if not provided then all aliases are shown
    """
    if not userid:
        ctx.vlog("Showing all records")
        e = create_engine(ctx.gconfig.get("db", "rwurl"))
        res = e.execute("select * from " + table)
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for u in userid:
            udata = parse_user_spec(ctx, u)
            e = create_engine(ctx.gconfig.get("db", "rwurl"))

            if matchalias:
                ctx.vlog(
                    "Showing records for alias [%s@%s]",
                    udata["username"],
                    udata["domain"],
                )
                res = e.execute(
                    "select * from " + table + " where alias_username=%s "
                    "and alias_domain=%s",
                    udata["username"],
                    udata["domain"],
                )
            else:
                ctx.vlog(
                    "Showing records for user [%s@%s]",
                    udata["username"],
                    udata["domain"],
                )
                res = e.execute(
                    "select * from " + table + " where username=%s and "
                    "domain=%s",
                    udata["username"],
                    udata["domain"],
                )
            ioutils_dbres_print(ctx, oformat, ostyle, res)
