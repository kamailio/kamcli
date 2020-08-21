import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec


@click.group(
    "avp",
    help="Manage AVP user preferences",
    short_help="Manage AVP user preferences",
)
@pass_context
def cli(ctx):
    pass


@cli.command("db-add", short_help="Add a new AVP to database")
@click.option(
    "dbtname",
    "--dbtname",
    "-T",
    default="usr_preferences",
    help='Database table name (default: "usr_preferences")',
)
@click.option(
    "coluuid",
    "--coluuid",
    default="uuid",
    help='Column name for uuid (default: "uuid")',
)
@click.option(
    "colusername",
    "--colusername",
    default="username",
    help='Column name for uuid (default: "username")',
)
@click.option(
    "coldomain",
    "--coldomain",
    default="domain",
    help='Column name for domain (default: "domain")',
)
@click.option(
    "colattribute",
    "--colattribute",
    default="attribute",
    help='Column name for attribute (default: "attribute")',
)
@click.option(
    "coltype",
    "--coltype",
    default="type",
    help='Column name for type (default: "type")',
)
@click.option(
    "colvalue",
    "--colvalue",
    default="value",
    help='Column name for value (default: "value")',
)
@click.option(
    "atype",
    "--atype",
    "-t",
    type=int,
    default=0,
    help="Value of the AVP type (default: 0)",
)
@click.option(
    "isuuid",
    "--is-uuid",
    "-u",
    is_flag=True,
    help="The <userid> argument is a <uuid>, otherwise <username>@<domain>",
)
@click.option(
    "setuuid",
    "--set-uuid",
    "-U",
    is_flag=True,
    help="The <userid> is <username>@<domain>, but the uuid field is also set to <username>",
)
@click.argument("userid", metavar="<userid>")
@click.argument("attribute", metavar="<attribute>")
@click.argument("value", metavar="<value>")
@pass_context
def htable_dbadd(
    ctx,
    dbtname,
    coluuid,
    colusername,
    coldomain,
    colattribute,
    coltype,
    colvalue,
    atype,
    isuuid,
    setuuid,
    userid,
    attribute,
    value,
):
    """Add a new AVP record in database table

    \b
    Parameters:
        <userid> - user AVP id (<username>@<domain> or <uuid>)
        <attribute> - attribute name
        <value>  - associated value for attribute
    """
    ctx.vlog(
        "Adding to AVP to table [%s] - [%s] [%s] => [%s]",
        dbtname,
        userid,
        attribute,
        value,
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    dbname = dbtname.encode("ascii", "ignore").decode()
    c_uuid = coluuid.encode("ascii", "ignore").decode()
    c_username = colusername.encode("ascii", "ignore").decode()
    c_domain = coldomain.encode("ascii", "ignore").decode()
    c_attribute = colattribute.encode("ascii", "ignore").decode()
    c_type = coltype.encode("ascii", "ignore").decode()
    c_value = colvalue.encode("ascii", "ignore").decode()
    v_userid = userid.encode("ascii", "ignore").decode()
    v_attribute = attribute.encode("ascii", "ignore").decode()
    v_value = value.encode("ascii", "ignore").decode()

    if isuuid:
        e.execute(
            "insert into {0} ({1}, {2}, {3}, {4}) values ({5!r}, {6!r}, {7}, {8!r})".format(
                dbname,
                c_uuid,
                c_attribute,
                c_type,
                c_value,
                v_userid,
                v_attribute,
                atype,
                v_value,
            )
        )
    else:
        udata = parse_user_spec(ctx, userid)
        if setuuid:
            e.execute(
                "insert into {0} ({1}, {2}, {3}, {4}, {5}, {6}) values ({7!r}, {8!r}, {9!r}, {10!r}, {11}, {12!r})".format(
                    dbname,
                    c_uuid,
                    c_username,
                    c_domain,
                    c_attribute,
                    c_type,
                    c_value,
                    udata["username"],
                    udata["username"],
                    udata["domain"],
                    v_attribute,
                    atype,
                    v_value,
                )
            )
        else:
            e.execute(
                "insert into {0} ({1}, {2}, {3}, {4}, {5}) values ({6!r}, {7!r}, {8!r}, {9}, {10!r})".format(
                    dbname,
                    c_username,
                    c_domain,
                    c_attribute,
                    c_type,
                    c_value,
                    udata["username"],
                    udata["domain"],
                    v_attribute,
                    atype,
                    v_value,
                )
            )
