import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec


@click.group("group", help="Manage the ACL of users with group membership")
@pass_context
def cli(ctx):
    pass


@cli.command("grant", short_help="Add a user into a group")
@click.argument("userid", metavar="<userid>")
@click.argument("groupid", metavar="<groupid>")
@pass_context
def group_grant(ctx, userid, groupid):
    """Add a user into a group (grant privilege)

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <groupid> - group name
    """
    udata = parse_user_spec(ctx, userid)
    ctx.vlog(
        "Adding user [%s@%s] in group [%s]",
        udata["username"],
        udata["domain"],
        groupid,
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "insert into grp (username, domain, grp) values (%s, %s, %s)",
        udata["username"],
        udata["domain"],
        groupid,
    )


@cli.command("revoke", short_help="Remove a user from groups")
@click.argument("userid", metavar="<userid>")
@click.argument("groupid", metavar="<groupid>", nargs=-1)
@pass_context
def group_revoke(ctx, userid, groupid):
    """Remove a user from groups (revoke privilege)

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <groupid> - group name
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log(
        "Removing ACL for user [%s@%s]", udata["username"], udata["domain"]
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if not groupid:
        e.execute(
            "delete from grp where username=%s and domain=%s",
            udata["username"],
            udata["domain"],
        )
    else:
        e.execute(
            "delete from grp where username=%s and domain=%s and grp=%s",
            udata["username"],
            udata["domain"],
            groupid,
        )


@cli.command("show", short_help="Show group membership details")
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
@click.argument("userid", nargs=-1, metavar="[<userid>]")
@pass_context
def group_show(ctx, oformat, ostyle, userid):
    """Show details for subscribers

    \b
    Parameters:
        [<userid>] - username, AoR or SIP URI for subscriber
                   - it can be a list of userids
                   - if not provided then all subscribers are shown
    """
    if not userid:
        ctx.vlog("Showing all records")
        e = create_engine(ctx.gconfig.get("db", "rwurl"))
        res = e.execute("select * from grp")
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for u in userid:
            udata = parse_user_spec(ctx, u)
            ctx.vlog(
                "Showing group membership for user [%s@%s]",
                udata["username"],
                udata["domain"],
            )
            e = create_engine(ctx.gconfig.get("db", "rwurl"))
            res = e.execute(
                "select * from grp where username=%s and domain=%s",
                udata["username"],
                udata["domain"],
            )
            ioutils_dbres_print(ctx, oformat, ostyle, res)
