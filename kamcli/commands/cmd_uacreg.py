import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group("uacreg", help="Manage uac remote registration")
@pass_context
def cli(ctx):
    pass


@cli.command("add", short_help="Add a new remote registration account")
@click.option("realm", "--realm", default="", help='Realm (default: "")')
@click.option(
    "authha1", "--auth-ha1", is_flag=True, help="Auth password in HA1 format"
)
@click.option(
    "flags", "--flags", type=int, default=0, help="Flags (default: 0)"
)
@click.option(
    "regdelay",
    "--reg-delay",
    type=int,
    default=0,
    help="Registration delay (default: 0)",
)
@click.option(
    "socket", "--socket", default="", help='Local socket (default: "")'
)
@click.argument("l_uuid", metavar="<l_uuid>")
@click.argument("l_username", metavar="<l_username>")
@click.argument("l_domain", metavar="<l_domain>")
@click.argument("r_username", metavar="<r_username>")
@click.argument("r_domain", metavar="<r_domain>")
@click.argument("auth_username", metavar="<auth_username>")
@click.argument("auth_password", metavar="<auth_password>")
@click.argument("auth_proxy", metavar="<auth_proxy>")
@click.argument("expires", metavar="<expires>", type=int)
@pass_context
def uacreg_add(
    ctx,
    realm,
    authha1,
    flags,
    regdelay,
    socket,
    l_uuid,
    l_username,
    l_domain,
    r_username,
    r_domain,
    auth_username,
    auth_password,
    auth_proxy,
    expires,
):
    """Add a new uac remote registration account

    \b
    Parameters:
        <l_uuid> - local user unique id
        <l_username> - local username
        <l_domain> - local domain
        <r_username> - remote username
        <r_domain> - remote domain
        <auth_username> - auth username
        <auth_password> - auth password
        <auth_proxy> - auth proxy (sip address)
        <expires> - expires interval (int)
    """
    ctx.vlog(
        "Adding a new uac remote registration account - local uuid: [%s]",
        l_uuid,
    )
    pwval = ""
    ha1val = ""
    if authha1:
        ha1val = auth_password
    else:
        pwval = auth_password
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "insert into uacreg (l_uuid, l_username, l_domain, r_username, "
        "r_domain, realm, auth_username, auth_password, auth_ha1, auth_proxy, "
        "expires, flags, reg_delay, socket) values "
        "({0!r}, {1!r}, {2!r}, {3!r}, "
        "{4!r}, {5!r}, {6!r}, {7!r}, {8!r}, {9!r}, "
        "{10}, {11}, {12}, {13!r})".format(
            l_uuid.encode("ascii", "ignore").decode(),
            l_username.encode("ascii", "ignore").decode(),
            l_domain.encode("ascii", "ignore").decode(),
            r_username.encode("ascii", "ignore").decode(),
            r_domain.encode("ascii", "ignore").decode(),
            realm.encode("ascii", "ignore").decode(),
            auth_username.encode("ascii", "ignore").decode(),
            pwval.encode("ascii", "ignore").decode(),
            ha1val.encode("ascii", "ignore").decode(),
            auth_proxy.encode("ascii", "ignore").decode(),
            expires,
            flags,
            regdelay,
            socket.encode("ascii", "ignore").decode(),
        )
    )


@cli.command(
    "passwd", short_help="Set the password for a remote registration account"
)
@click.option(
    "authha1", "--auth-ha1", is_flag=True, help="Auth password in HA1 format"
)
@click.argument("l_uuid", metavar="<l_uuid>")
@click.argument("auth_password", metavar="<auth_password>")
@pass_context
def uacreg_passwd(ctx, realm, authha1, l_uuid, auth_password):
    """Set password for a remote registration account

    \b
    Parameters:
        <l_uuid> - local user unique id
        <auth_password> - auth password
    """
    ctx.vlog(
        "Adding a new uac remote registration account - local uuid: [%s]",
        l_uuid,
    )
    pwval = ""
    ha1val = ""
    if authha1:
        ha1val = auth_password
    else:
        pwval = auth_password
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "update uacreg set auth_password={0!r}, auth_ha1={1!r} "
        "where l_uuid={2!r}".format(
            pwval.encode("ascii", "ignore").decode(),
            ha1val.encode("ascii", "ignore").decode(),
            l_uuid.encode("ascii", "ignore").decode(),
        )
    )


@cli.command("showdb", short_help="Show dialplan records in database")
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
@click.argument("l_uuid", nargs=-1, metavar="[<l_uuid>]")
@pass_context
def uacreg_showdb(ctx, oformat, ostyle, l_uuid):
    """Show details for records in uacreg database table

    \b
    Parameters:
        [<l_uuid>] - local user unique id
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if not l_uuid:
        ctx.vlog("Showing all uacreg records")
        res = e.execute("select * from uacreg")
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for l in l_uuid:
            ctx.vlog("Showing uacreg records for l_uuid: " + l)
            res = e.execute('select * from uacreg where l_uuid="%s"', l)
            ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command(
    "list", short_help="Show details for remote registration records in memory"
)
@pass_context
def uacreg_list(ctx):
    """Show details for remote registration records in memory

    \b
    """
    command_ctl(ctx, "uac.reg_dump", [])


@cli.command(
    "reload",
    short_help="Reload remote registration records from database into memory",
)
@pass_context
def uacreg_reload(ctx):
    """Reload remote registration records from database into memory
    """
    command_ctl(ctx, "uac.reg_reload", [])
