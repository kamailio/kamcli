import os
import sys
import click
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from kamcli.cli import pass_context
from kamcli.ioutils import ioutils_dbres_print
from kamcli.ioutils import ioutils_formats_list
from kamcli.dbutils import dbutils_exec_sqlfile


CMD_BASE = "mysql -h {0} -u {1} -p{2} "

KDB_GROUP_BASIC = ["standard"]

KDB_GROUP_STANDARD = [
    "acc",
    "lcr",
    "domain",
    "group",
    "permissions",
    "registrar",
    "usrloc",
    "msilo",
    "alias_db",
    "uri_db",
    "speeddial",
    "avpops",
    "auth_db",
    "pdt",
    "dialog",
    "dispatcher",
    "dialplan",
    "topos",
]

KDB_GROUP_EXTRA = [
    "imc",
    "cpl",
    "siptrace",
    "domainpolicy",
    "carrierroute",
    "drouting",
    "userblacklist",
    "htable",
    "purple",
    "uac",
    "pipelimit",
    "mtree",
    "sca",
    "mohqueue",
    "rtpproxy",
    "rtpengine",
    "secfilter",
]

KDB_GROUP_PRESENCE = ["presence", "rls"]

KDB_GROUP_UID = [
    "uid_auth_db",
    "uid_avp_db",
    "uid_domain",
    "uid_gflags",
    "uid_uri_db",
]


@click.group("db", help="Raw database operations")
@pass_context
def cli(ctx):
    pass


@cli.command("connect", help="Launch db cli and connect to database")
@pass_context
def db_connect(ctx):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype.lower() == "mysql":
        scmd = (CMD_BASE + "{3}").format(
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "postgres":
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


@cli.command("clirun", help="Run SQL statement via cli")
@click.argument("query", metavar="<query>")
@pass_context
def db_clirun(ctx, query):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "mysql":
        scmd = (CMD_BASE + '-e "{3} ;" {4}').format(
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            query,
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "postgres":
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


@cli.command("clishow", help="Show content of table via cli")
@click.argument("table", metavar="<table>")
@pass_context
def db_clishow(ctx, table):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "mysql":
        scmd = (CMD_BASE + '-e "select * from {3} ;" {4}').format(
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            table,
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "postgres":
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


@cli.command("clishowg", help="Show content of table via cli")
@click.argument("table", metavar="<table>")
@pass_context
def db_clishowg(ctx, table):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "mysql":
        scmd = (CMD_BASE + r'-e "select * from {3} \G" {4}').format(
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            table,
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "postgres":
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


@cli.command("show", help="Show content of a table")
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
@click.argument("table", metavar="<table>")
@pass_context
def db_show(ctx, oformat, ostyle, table):
    ctx.vlog("Content of database table [%s]", table)
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    res = e.execute("select * from {0}".format(table))
    ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command("showcreate", help="Show content of a table")
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
@click.argument("table", metavar="<table>")
@pass_context
def db_showcreate(ctx, oformat, ostyle, table):
    ctx.vlog("Show create of database table [%s]", table)
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    res = e.execute("show create table {0}".format(table))
    ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command("runfile", help="Run SQL statements in a file")
@click.argument("fname", metavar="<fname>")
@pass_context
def db_runfile(ctx, fname):
    """Run SQL statements in a file

    \b
    Parameters:
        <fname> - name to the file with the SQL statements
    """
    ctx.vlog("Run statements in the file [%s]", fname)
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    dbutils_exec_sqlfile(ctx, e, fname)


def db_create_host_users(
    ctx, e, dbname, dbhost, dbrwuser, dbrwpassword, dbrouser, dbropassword
):
    e.execute(
        "CREATE USER {0!r}@{1!r} IDENTIFIED BY {2!r}".format(
            dbrwuser, dbhost, dbrwpassword
        )
    )
    e.execute(
        "GRANT ALL PRIVILEGES ON {0}.* TO {1!r}@{2!r}".format(
            dbname, dbrwuser, dbhost
        )
    )
    e.execute(
        "CREATE USER {0!r}@{1!r} IDENTIFIED BY {2!r}".format(
            dbrouser, dbhost, dbropassword
        )
    )
    e.execute(
        "GRANT SELECT PRIVILEGES ON {0}.* TO {1!r}@{2!r}".format(
            dbname, dbrouser, dbhost
        )
    )


def db_create_users(ctx, e, dbname):
    dbhost = ctx.gconfig.get("db", "host")
    dbrwuser = ctx.gconfig.get("db", "rwuser")
    dbrwpassword = ctx.gconfig.get("db", "rwpassword")
    dbrouser = ctx.gconfig.get("db", "rouser")
    dbropassword = ctx.gconfig.get("db", "ropassword")
    dbaccesshost = ctx.gconfig.get("db", "accesshost")
    db_create_host_users(
        ctx, e, dbname, dbhost, dbrwuser, dbrwpassword, dbrouser, dbropassword
    )
    if dbhost != "localhost":
        db_create_host_users(
            ctx,
            e,
            dbname,
            "localhost",
            dbrwuser,
            dbrwpassword,
            dbrouser,
            dbropassword,
        )
    if len(dbaccesshost) > 0:
        db_create_host_users(
            ctx,
            e,
            dbname,
            dbaccesshost,
            dbrwuser,
            dbrwpassword,
            dbrouser,
            dbropassword,
        )


def db_create_database(ctx, e, dbname):
    e.execute("create database {0}".format(dbname))


def db_create_group(ctx, e, dir, dbgroup):
    for t in dbgroup:
        fname = dir + "/" + t + "-create.sql"
        dbutils_exec_sqlfile(ctx, e, fname)


@cli.command("create", help="Create database structure")
@click.option(
    "dbname",
    "--dbname",
    default="",
    help="Database name or path to the folder for database",
)
@click.option(
    "directory",
    "--directory",
    default="",
    help="Path to the directory with db schema files",
)
@pass_context
def db_create(ctx, dbname, directory):
    """Create database structure

    \b
    """
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype != "mysql":
        ctx.vlog("Database type [%s] not supported yet", dbtype)
        return
    ldbname = ctx.gconfig.get("db", "dbname")
    if len(dbname) > 0:
        ldbname = dbname
    ldirectory = ""
    if len(directory) > 0:
        ldirectory = directory
    ctx.vlog("Creating database [%s] structure", ldbname)
    e = create_engine(ctx.gconfig.get("db", "adminurl"))
    db_create_database(ctx, e, ldbname)
    e.execute("use {0}".format(ldbname))
    db_create_group(ctx, e, ldirectory, KDB_GROUP_BASIC)
    db_create_group(ctx, e, ldirectory, KDB_GROUP_STANDARD)
    print("Do you want to create extra tables? (y/n):", end=" ")
    option = input()
    if option == "y":
        db_create_group(ctx, e, ldirectory, KDB_GROUP_EXTRA)
    print("Do you want to create presence tables? (y/n):", end=" ")
    option = input()
    if option == "y":
        db_create_group(ctx, e, ldirectory, KDB_GROUP_PRESENCE)
    print("Do you want to create uid tables? (y/n):", end=" ")
    option = input()
    if option == "y":
        db_create_group(ctx, e, ldirectory, KDB_GROUP_UID)


@cli.command("create-dbonly", help="Create database only")
@click.option(
    "dbname",
    "--dbname",
    default="",
    help="Database name or path to the folder for database",
)
@pass_context
def db_create_dbonly(ctx, dbname):
    """Create database only

    \b
    """
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype != "mysql":
        ctx.vlog("Database type [%s] not supported yet", dbtype)
        return
    ldbname = ctx.gconfig.get("db", "dbname")
    if len(dbname) > 0:
        ldbname = dbname
    ctx.vlog("Creating only database [%s]", ldbname)
    e = create_engine(ctx.gconfig.get("db", "adminurl"))
    db_create_database(ctx, e, ldbname)
    e.execute("use {0}".format(ldbname))


@cli.command("grant", help="Create db access users and grant privileges")
@click.option(
    "dbname", "--dbname", default="", help="Database name",
)
@pass_context
def db_grant(ctx, dbname):
    """Create db access users and grant privileges

    \b
    """
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype != "mysql":
        ctx.vlog("Database type [%s] not supported yet", dbtype)
        return
    ldbname = ctx.gconfig.get("db", "dbname")
    if len(dbname) > 0:
        ldbname = dbname
    ctx.vlog("Creating only database [%s]", ldbname)
    e = create_engine(ctx.gconfig.get("db", "adminurl"))
    db_create_users(ctx, e, ldbname)
