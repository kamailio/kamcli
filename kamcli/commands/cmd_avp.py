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
def avp_dbadd(
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


@cli.command("db-rm", short_help="Delete AVPs from database")
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
    default=-1,
    help="Value of the AVP type (default: -1 - no match on type)",
)
@click.option(
    "isuuid",
    "--is-uuid",
    "-u",
    is_flag=True,
    help="The <userid> argument is a <uuid>, otherwise <username>@<domain>",
)
@click.argument("userid", metavar="<userid>")
@click.argument("attribute", metavar="<attribute>")
@click.argument("value", metavar="<value>")
@pass_context
def avp_dbrm(
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
    userid,
    attribute,
    value,
):
    """Remove AVP records from database table

    \b
    Parameters:
        <userid> - user AVP id (<username>@<domain> or <uuid>)
        <attribute> - attribute name
        <value>  - associated value for attribute
        - use '*' to match any value for <userid>, <attribute> or <value>
        - example - remove all AVPs: kamcli avp db-rm '*' '*' '*'
    """
    ctx.vlog(
        "Removing AVPs from table [%s] - [%s] [%s] => [%s]",
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

    sqlquery = "DELETE FROM {0}".format(dbname)
    if atype != -1 or v_userid != "*" or v_userid != "*" or v_userid != "*":
        sqlquery += " WHERE 1=1"

    if v_userid != "*":
        if isuuid:
            sqlquery += " AND {0}={1!r}".format(c_uuid, v_userid)
        else:
            udata = parse_user_spec(ctx, userid)
            sqlquery += " AND {0}={1!r} AND {2}={3!r}".format(
                c_username, udata["username"], c_domain, udata["domain"]
            )

    if v_attribute != "*":
        sqlquery += " AND {0}={1!r}".format(c_attribute, v_attribute)

    if atype != -1:
        sqlquery += " AND {0}={1}".format(c_type, atype)

    if v_value != "*":
        sqlquery += " AND {0}={1!r}".format(c_value, v_value)

    e.execute(sqlquery)


@cli.command("db-show", short_help="Show AVPs from database")
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
    default=-1,
    help="Value of the AVP type (default: -1 - no match on type)",
)
@click.option(
    "isuuid",
    "--is-uuid",
    "-u",
    is_flag=True,
    help="The <userid> argument is a <uuid>, otherwise <username>@<domain>",
)
@click.argument("userid", metavar="<userid>")
@click.argument("attribute", metavar="<attribute>")
@click.argument("value", metavar="<value>")
@pass_context
def avp_dbshow(
    ctx,
    oformat,
    ostyle,
    dbtname,
    coluuid,
    colusername,
    coldomain,
    colattribute,
    coltype,
    colvalue,
    atype,
    isuuid,
    userid,
    attribute,
    value,
):
    """Show AVP records from database table

    \b
    Parameters:
        <userid> - user AVP id (<username>@<domain> or <uuid>)
        <attribute> - attribute name
        <value>  - associated value for attribute
        - use '*' to match any value for <userid>, <attribute> or <value>
        - example - remove all AVPs: kamcli avp db-rm '*' '*' '*'
    """
    ctx.vlog(
        "Show AVPs from table [%s] - [%s] [%s] => [%s]",
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

    sqlquery = "SELECT * FROM {0}".format(dbname)
    if atype != -1 or v_userid != "*" or v_userid != "*" or v_userid != "*":
        sqlquery += " WHERE 1=1"

    if v_userid != "*":
        if isuuid:
            sqlquery += " AND {0}={1!r}".format(c_uuid, v_userid)
        else:
            udata = parse_user_spec(ctx, userid)
            sqlquery += " AND {0}={1!r} AND {2}={3!r}".format(
                c_username, udata["username"], c_domain, udata["domain"]
            )

    if v_attribute != "*":
        sqlquery += " AND {0}={1!r}".format(c_attribute, v_attribute)

    if atype != -1:
        sqlquery += " AND {0}={1}".format(c_type, atype)

    if v_value != "*":
        sqlquery += " AND {0}={1!r}".format(c_value, v_value)

    res = e.execute(sqlquery)
    ioutils_dbres_print(ctx, oformat, ostyle, res)
