import click
import hashlib
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec


@click.group(
    "subscriber",
    help="Manage the subscribers",
    short_help="Manage the subscribers",
)
@pass_context
def cli(ctx):
    pass


@cli.command("add", short_help="Add a new subscriber")
@click.option(
    "dbtname",
    "--dbtname",
    "-T",
    default="subscriber",
    help='Database table name (default: "subscriber")',
)
@click.option(
    "pwtext",
    "--text-password",
    "-t",
    type=click.Choice(["yes", "no"]),
    default="yes",
    help="Store password in clear text (default yes)",
)
@click.argument("userid", metavar="<userid>")
@click.argument("password", metavar="<password>")
@pass_context
def subscriber_add(ctx, dbtname, pwtext, userid, password):
    """Add a new subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <password> - the password
    """
    udata = parse_user_spec(ctx, userid)
    ctx.vlog(
        "Adding subscriber [%s] in domain [%s] with password [%s]",
        udata["username"],
        udata["domain"],
        password,
    )
    dig = "{}:{}:{}".format(udata["username"], udata["domain"], password)
    ha1 = hashlib.md5(dig.encode()).hexdigest()
    dig = "{}@{}:{}:{}".format(
        udata["username"], udata["domain"], udata["domain"], password
    )
    ha1b = hashlib.md5(dig.encode()).hexdigest()
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if pwtext == "yes":
        e.execute(
            "insert into {0} (username, domain, password, ha1, ha1b) "
            "values ({1!r}, {2!r}, {3!r}, {4!r}, {5!r})".format(
                dbtname.encode("ascii", "ignore").decode(),
                udata["username"],
                udata["domain"],
                password.encode("ascii", "ignore").decode(),
                ha1,
                ha1b,
            )
        )
    else:
        e.execute(
            "insert into {0} (username, domain, ha1, ha1b) values "
            "({1!r}, {2!r}, {3!r}, {4!r})".format(
                dbtname.encode("ascii", "ignore").decode(),
                udata["username"],
                udata["domain"],
                ha1,
                ha1b,
            )
        )


@cli.command("rm", short_help="Remove an existing subscriber")
@click.option(
    "dbtname",
    "--dbtname",
    "-T",
    default="subscriber",
    help='Database table name (default: "subscriber")',
)
@click.option(
    "yes",
    "--yes",
    "-y",
    is_flag=True,
    help="Do not ask for confirmation",
)
@click.argument("userid", metavar="<userid>")
@pass_context
def subscriber_rm(ctx, dbtname, yes, userid):
    """Remove an existing subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
    """
    if not yes:
        print("Removing user. Are you sure? (y/n):", end=" ")
        option = input()
        if option != "y":
            ctx.vlog("Skip removing user [%s]", userid)
            return
    udata = parse_user_spec(ctx, userid)
    ctx.log("Removing subscriber [%s@%s]", udata["username"], udata["domain"])
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "delete from {0} where username={1!r} and domain={2!r}".format(
            dbtname.encode("ascii", "ignore").decode(),
            udata["username"],
            udata["domain"],
        )
    )


@cli.command("passwd", short_help="Update the password for a subscriber")
@click.option(
    "dbtname",
    "--dbtname",
    "-T",
    default="subscriber",
    help='Database table name (default: "subscriber")',
)
@click.option(
    "pwtext",
    "--text-password",
    "-t",
    type=click.Choice(["yes", "no"]),
    default="yes",
    help="Store password in clear text (default yes)",
)
@click.argument("userid", metavar="<userid>")
@click.argument("password", metavar="<password>")
@pass_context
def subscriber_passwd(ctx, dbtname, pwtext, userid, password):
    """Update password for a subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <password> - the password
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log(
        "Updating subscriber [%s@%s] with password [%s]",
        udata["username"],
        udata["domain"],
        password,
    )
    dig = "{}:{}:{}".format(udata["username"], udata["domain"], password)
    ha1 = hashlib.md5(dig.encode()).hexdigest()
    dig = "{}@{}:{}:{}".format(
        udata["username"], udata["domain"], udata["domain"], password
    )
    ha1b = hashlib.md5(dig.encode()).hexdigest()
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if pwtext == "yes":
        e.execute(
            "update {0} set password={1!r}, ha1={2!r}, ha1b={3!r} where "
            "username={4!r} and domain={5!r}".format(
                dbtname.encode("ascii", "ignore").decode(),
                password.encode("ascii", "ignore").decode(),
                ha1,
                ha1b,
                udata["username"],
                udata["domain"],
            )
        )
    else:
        e.execute(
            "update {0} set ha1={1!r}, ha1b={2!r} where "
            "username={3!r} and domain={4!r}".format(
                dbtname,
                ha1,
                ha1b,
                udata["username"],
                udata["domain"],
            )
        )


@cli.command("show", short_help="Show details for subscribers")
@click.option(
    "dbtname",
    "--dbtname",
    "-T",
    default="subscriber",
    help='Database table name (default: "subscriber")',
)
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
def subscriber_show(ctx, dbtname, oformat, ostyle, userid):
    """Show details for subscribers

    \b
    Parameters:
        [<userid>] - username, AoR or SIP URI for subscriber
                   - it can be a list of userids
                   - if not provided then all subscribers are shown
    """
    if not userid:
        ctx.vlog("Showing all subscribers")
        e = create_engine(ctx.gconfig.get("db", "rwurl"))
        res = e.execute(
            "select * from {0}".format(
                dbtname.encode("ascii", "ignore").decode()
            )
        )
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for u in userid:
            udata = parse_user_spec(ctx, u)
            ctx.vlog(
                "Showing subscriber [%s@%s]",
                udata["username"],
                udata["domain"],
            )
            e = create_engine(ctx.gconfig.get("db", "rwurl"))
            res = e.execute(
                "select * from {0} where username={1!r} and domain={2!r}".format(
                    dbtname.encode("ascii", "ignore").decode(),
                    udata["username"],
                    udata["domain"],
                )
            )
            ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command("setattrs", short_help="Set a string attribute for a subscriber")
@click.option(
    "dbtname",
    "--dbtname",
    "-T",
    default="subscriber",
    help='Database table name (default: "subscriber")',
)
@click.argument("userid", metavar="<userid>")
@click.argument("attr", metavar="<attribute>")
@click.argument("val", metavar="<value>")
@pass_context
def subscriber_setattrs(ctx, dbtname, userid, attr, val):
    """Set a string attribute a subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <attribute> - the name of the attribute (column name in
                      subscriber table)
        <value> - the value to be set for the attribute
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log(
        "Updating subscriber [%s@%s] with str attribute [%s]=[%s]",
        udata["username"],
        udata["domain"],
        attr,
        val,
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "update {0} set {1}={2!r} where username={3!r} and "
        "domain={4!r}".format(
            dbtname.encode("ascii", "ignore").decode(),
            attr.encode("ascii", "ignore").decode(),
            val.encode("ascii", "ignore").decode(),
            udata["username"],
            udata["domain"],
        )
    )


@cli.command(
    "setattri", short_help="Set an integer attribute for a subscriber"
)
@click.option(
    "dbtname",
    "--dbtname",
    "-T",
    default="subscriber",
    help='Database table name (default: "subscriber")',
)
@click.argument("userid", metavar="<userid>")
@click.argument("attr", metavar="<attribute>")
@click.argument("val", metavar="<value>")
@pass_context
def subscriber_setattri(ctx, dbtname, userid, attr, val):
    """Set an integer attribute a subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <attribute> - the name of the attribute (column name in
                      subscriber table)
        <value> - the value to be set for the attribute
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log(
        "Updating subscriber [%s@%s] with int attribute [%s]=[%s]",
        udata["username"],
        udata["domain"],
        attr,
        val,
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "update {0} set {1}={2} where username={3!r} and "
        "domain={4!r}".format(
            dbtname.encode("ascii", "ignore").decode(),
            attr.encode("ascii", "ignore").decode(),
            val.encode("ascii", "ignore").decode(),
            udata["username"],
            udata["domain"],
        )
    )


@cli.command(
    "setattrnull", short_help="Set an attribute to NULL for a subscriber"
)
@click.option(
    "dbtname",
    "--dbtname",
    "-T",
    default="subscriber",
    help='Database table name (default: "subscriber")',
)
@click.argument("userid", metavar="<userid>")
@click.argument("attr", metavar="<attribute>")
@pass_context
def subscriber_setattrnull(ctx, dbtname, userid, attr):
    """Set an attribute to NULL for a subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <attribute> - the name of the attribute (column name in
                      subscriber table)
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log(
        "Updating subscriber [%s@%s] with attribute [%s]=NULL",
        udata["username"],
        udata["domain"],
        attr,
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "update {0} set {1}=NULL where username={2!r} and "
        "domain={3!r}".format(
            dbtname.encode("ascii", "ignore").decode(),
            attr.encode("ascii", "ignore").decode(),
            udata["username"],
            udata["domain"],
        )
    )
