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
    "userblocklist",
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


@click.group(
    "db", help="Raw database operations", short_help="Raw database operations"
)
@pass_context
def cli(ctx):
    pass


@cli.command("query", short_help="Run SQL statement")
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
@click.argument("query", metavar="<query>")
@pass_context
def db_query(ctx, oformat, ostyle, query):
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    res = e.execute(query.encode("ascii", "ignore").decode())
    ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command("connect", short_help="Launch db cli and connect to database")
@pass_context
def db_connect(ctx):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype.lower() == "mysql":
        scmd = ("mysql -h {0} -u {1} -p{2} {3}").format(
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "postgresql":
        scmd = ('psql "postgresql://{0}:{1}@{2}/{3}"').format(
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "sqlite":
        scmd = ("sqlite3 {0} ").format(
            ctx.gconfig.get("db", "dbpath"),
        )
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


@cli.command("clirun", short_help="Run SQL statement via cli")
@click.argument("query", metavar="<query>")
@pass_context
def db_clirun(ctx, query):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "mysql":
        scmd = ('mysql -h {0} -u {1} -p{2} -e "{3} ;" {4}').format(
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            query,
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "postgresql":
        scmd = ('psql "postgresql://{0}:{1}@{2}/{3}" -c "{4} ;"').format(
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "dbname"),
            query,
        )
    elif dbtype == "sqlite":
        scmd = ('sqlite3 {0} "{1} "').format(
            ctx.gconfig.get("db", "dbpath"),
            query,
        )
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


@cli.command("clishow", short_help="Show content of table via cli")
@click.argument("table", metavar="<table>")
@pass_context
def db_clishow(ctx, table):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "mysql":
        scmd = (
            'mysql -h {0} -u {1} -p{2} -e "select * from {3} ;" {4}'
        ).format(
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            table,
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "postgresql":
        scmd = (
            'psql "postgresql://{0}:{1}@{2}/{3}" -c "select * from {4} ;"'
        ).format(
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "dbname"),
            table,
        )
    elif dbtype == "sqlite":
        scmd = ('sqlite3 {0} "select * from {1} "').format(
            ctx.gconfig.get("db", "dbpath"),
            table,
        )
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


@cli.command("clishowg", short_help="Show content of table via cli")
@click.argument("table", metavar="<table>")
@pass_context
def db_clishowg(ctx, table):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "mysql":
        scmd = (
            r'mysql -h {0} -u {1} -p{2} -e "select * from {3} \G" {4}'
        ).format(
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            table,
            ctx.gconfig.get("db", "dbname"),
        )
    elif dbtype == "postgresql":
        scmd = (
            'psql "postgresql://{0}:{1}@{2}/{3}" -c "\\x" -c "select * from {4} ;" -c "\\x"'
        ).format(
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "dbname"),
            table,
        )
    elif dbtype == "sqlite":
        scmd = ('sqlite3 -line {0} "select * from {1} "').format(
            ctx.gconfig.get("db", "dbpath"),
            table,
        )
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


@cli.command("show", short_help="Show content of a table")
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


@cli.command(
    "showcreate", short_help="Show create statement of of a database table"
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
@click.argument("table", metavar="<table>")
@pass_context
def db_showcreate(ctx, oformat, ostyle, table):
    ctx.vlog("Show create of database table [%s]", table)
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "mysql":
        e = create_engine(ctx.gconfig.get("db", "rwurl"))
        res = e.execute("show create table {0}".format(table))
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    elif dbtype == "postgresql":
        scmd = ('psql "postgresql://{0}:{1}@{2}/{3}" -c "\\d {4} "').format(
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            ctx.gconfig.get("db", "host"),
            ctx.gconfig.get("db", "dbname"),
            table,
        )
        os.system(scmd)
    elif dbtype == "sqlite":
        scmd = ('sqlite3 {0} ".schema {1} "').format(
            ctx.gconfig.get("db", "dbpath"),
            table,
        )
        os.system(scmd)
    else:
        ctx.log("unsupported database type [%s]", dbtype)


@cli.command("runfile", short_help="Run SQL statements in a file")
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


def db_create_mysql_host_users(
    ctx,
    e,
    nousers,
    nogrants,
    dbname,
    dbhost,
    dbrwuser,
    dbrwpassword,
    dbrouser,
    dbropassword,
):
    if not nousers:
        e.execute(
            "CREATE USER {0!r}@{1!r} IDENTIFIED BY {2!r}".format(
                dbrwuser, dbhost, dbrwpassword
            )
        )
    if not nogrants:
        e.execute(
            "GRANT ALL PRIVILEGES ON {0}.* TO {1!r}@{2!r}".format(
                dbname, dbrwuser, dbhost
            )
        )
    if not nousers:
        e.execute(
            "CREATE USER {0!r}@{1!r} IDENTIFIED BY {2!r}".format(
                dbrouser, dbhost, dbropassword
            )
        )
    if not nogrants:
        e.execute(
            "GRANT SELECT PRIVILEGES ON {0}.* TO {1!r}@{2!r}".format(
                dbname, dbrouser, dbhost
            )
        )


def db_create_mysql_users(ctx, e, dbname, nousers, nogrants):
    dbhost = ctx.gconfig.get("db", "host")
    dbrwuser = ctx.gconfig.get("db", "rwuser")
    dbrwpassword = ctx.gconfig.get("db", "rwpassword")
    dbrouser = ctx.gconfig.get("db", "rouser")
    dbropassword = ctx.gconfig.get("db", "ropassword")
    dbaccesshost = ctx.gconfig.get("db", "accesshost")
    db_create_mysql_host_users(
        ctx, e, dbname, dbhost, dbrwuser, dbrwpassword, dbrouser, dbropassword
    )
    if dbhost != "localhost":
        db_create_mysql_host_users(
            ctx,
            e,
            nousers,
            nogrants,
            dbname,
            "localhost",
            dbrwuser,
            dbrwpassword,
            dbrouser,
            dbropassword,
        )
    if len(dbaccesshost) > 0:
        db_create_mysql_host_users(
            ctx,
            e,
            nousers,
            nogrants,
            dbname,
            dbaccesshost,
            dbrwuser,
            dbrwpassword,
            dbrouser,
            dbropassword,
        )


def db_create_sql_group(ctx, e, dirpath, dbgroup):
    for t in dbgroup:
        fname = dirpath + "/" + t + "-create.sql"
        dbutils_exec_sqlfile(ctx, e, fname)


def db_create_sql_table_groups(ctx, e, ldirectory, alltables):
    db_create_sql_group(ctx, e, ldirectory, KDB_GROUP_BASIC)
    db_create_sql_group(ctx, e, ldirectory, KDB_GROUP_STANDARD)

    option = "y"
    if not alltables:
        print("Do you want to create extra tables? (y/n):", end=" ")
        option = input()
    if option == "y":
        db_create_sql_group(ctx, e, ldirectory, KDB_GROUP_EXTRA)

    if not alltables:
        print("Do you want to create presence tables? (y/n):", end=" ")
        option = input()
    if option == "y":
        db_create_sql_group(ctx, e, ldirectory, KDB_GROUP_PRESENCE)

    if not alltables:
        print("Do you want to create uid tables? (y/n):", end=" ")
        option = input()
    if option == "y":
        db_create_sql_group(ctx, e, ldirectory, KDB_GROUP_UID)


def db_create_mysql(ctx, ldbname, ldirectory, nousers, nogrants, alltables):
    e = create_engine(ctx.gconfig.get("db", "adminurl"))
    e.execute("create database {0}".format(ldbname))
    db_create_mysql_users(ctx, e, ldbname, nousers, nogrants)
    e.execute("use {0}".format(ldbname))
    db_create_sql_table_groups(ctx, e, ldirectory, alltables)


def db_create_postgresql(
    ctx, ldbname, ldirectory, nousers, nogrants, nofunctions, alltables
):
    scmd = (
        'psql "postgresql://{0}:{1}@{2}" -c "create database {3} "'
    ).format(
        ctx.gconfig.get("db", "adminuser"),
        ctx.gconfig.get("db", "adminpassword"),
        ctx.gconfig.get("db", "host"),
        ldbname,
    )
    os.system(scmd)
    e = create_engine(ctx.gconfig.get("db", "adminurl"))
    if not nogrants:
        e.execute(
            "CREATE USER {0} WITH PASSWORD '{1}';".format(
                ctx.gconfig.get("db", "rwuser"),
                ctx.gconfig.get("db", "rwpassword"),
            )
        )
        e.execute(
            "GRANT CONNECT ON DATABASE {0} TO {1};".format(
                ldbname,
                ctx.gconfig.get("db", "rwuser"),
            )
        )
        if ctx.gconfig.get("db", "rwuser") != ctx.gconfig.get("db", "rouser"):
            e.execute(
                "CREATE USER {0} WITH PASSWORD '{1}';".format(
                    ctx.gconfig.get("db", "rouser"),
                    ctx.gconfig.get("db", "ropassword"),
                )
            )
            e.execute(
                "GRANT CONNECT ON DATABASE {0} TO {1};".format(
                    ldbname,
                    ctx.gconfig.get("db", "rouser"),
                )
            )
    e.dispose()
    e = create_engine(
        "{0}+{1}://{2}:{3}@{4}/{5}".format(
            ctx.gconfig.get("db", "type"),
            ctx.gconfig.get("db", "driver"),
            ctx.gconfig.get("db", "rwuser"),
            ctx.gconfig.get("db", "rwpassword"),
            ctx.gconfig.get("db", "host"),
            ldbname,
        )
    )
    if not nofunctions:
        e.execute(
            "CREATE FUNCTION concat(text, text) RETURNS text AS 'SELECT $1 || $2;' LANGUAGE 'sql';"
        )
        e.execute(
            "CREATE FUNCTION rand() RETURNS double precision AS 'SELECT random();' LANGUAGE 'sql';"
        )
    db_create_sql_table_groups(ctx, e, ldirectory, alltables)
    e.dispose()
    e = create_engine(ctx.gconfig.get("db", "adminurl"))
    if not nogrants:
        e.execute(
            "GRANT ALL PRIVILEGES ON DATABASE {0} TO {1};".format(
                ldbname,
                ctx.gconfig.get("db", "rwuser"),
            )
        )
        if ctx.gconfig.get("db", "rwuser") != ctx.gconfig.get("db", "rouser"):
            e.execute(
                "GRANT SELECT ON DATABASE {0} TO {1};".format(
                    ldbname,
                    ctx.gconfig.get("db", "rouser"),
                )
            )


def db_create_sqlite(ctx, ldbname, ldirectory, alltables):
    e = create_engine(
        "{0}+{1}:///{2}".format(
            ctx.gconfig.get("db", "type"),
            ctx.gconfig.get("db", "driver"),
            ldbname,
        )
    )
    db_create_sql_table_groups(ctx, e, ldirectory, alltables)


@cli.command("create", short_help="Create database structure")
@click.option(
    "dbname",
    "--dbname",
    "-d",
    default="",
    help="Database name or path to the folder for database",
)
@click.option(
    "scriptsdirectory",
    "--scripts-directory",
    "-s",
    default="",
    help="Path to the directory with db schema files",
)
@click.option(
    "nousers",
    "--no-users",
    "-U",
    is_flag=True,
    help="Do not create users",
)
@click.option(
    "nogrants",
    "--no-grants",
    "-G",
    is_flag=True,
    help="Do not grant privileges",
)
@click.option(
    "nofunctions",
    "--no-functions",
    "-F",
    is_flag=True,
    help="Do not create additional SQL functions",
)
@click.option(
    "alltables",
    "--all-tables",
    "-a",
    is_flag=True,
    help="Create all tables without asking for confirmation",
)
@pass_context
def db_create(
    ctx, dbname, scriptsdirectory, nousers, nogrants, nofunctions, alltables
):
    """Create database structure

    \b
    """
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "sqlite":
        ldbname = ctx.gconfig.get("db", "dbpath")
    else:
        ldbname = ctx.gconfig.get("db", "dbname")
    if len(dbname) > 0:
        ldbname = dbname

    ldirectory = ctx.gconfig.get("db", "scriptsdirectory")
    if len(scriptsdirectory) > 0:
        ldirectory = scriptsdirectory
    ctx.vlog("Creating database [%s] structure", ldbname)
    if dbtype == "mysql":
        db_create_mysql(ctx, ldbname, ldirectory, nousers, nogrants, alltables)
        return
    elif dbtype == "postgresql":
        db_create_postgresql(
            ctx, ldbname, ldirectory, nousers, nogrants, nofunctions, alltables
        )
        return
    elif dbtype == "sqlite":
        db_create_sqlite(ctx, ldbname, ldirectory, alltables)
        return
    else:
        ctx.vlog("Database type [%s] not supported yet", dbtype)
        return


@cli.command("create-dbonly", short_help="Create database only")
@click.option(
    "dbname",
    "--dbname",
    "-d",
    default="",
    help="Database name or path to the folder for database",
)
@pass_context
def db_create_dbonly(ctx, dbname):
    """Create database only

    \b
    """
    ctx.vlog("Creating only database [%s]", dbname)

    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "sqlite":
        ldbname = ctx.gconfig.get("db", "dbpath")
    else:
        ldbname = ctx.gconfig.get("db", "dbname")
    if len(dbname) > 0:
        ldbname = dbname

    if dbtype == "mysql":
        e = create_engine(ctx.gconfig.get("db", "adminurl"))
        e.execute("create database {0}".format(ldbname))
    elif dbtype == "postgresql":
        scmd = (
            'psql "postgresql://{0}:{1}@{2}" -c "create database {3} "'
        ).format(
            ctx.gconfig.get("db", "adminuser"),
            ctx.gconfig.get("db", "adminpassword"),
            ctx.gconfig.get("db", "host"),
            ldbname,
        )
        os.system(scmd)
    elif dbtype == "sqlite":
        ctx.vlog("Database file for type [%s] is created on first use", dbtype)
    else:
        ctx.vlog("Database type [%s] not supported yet", dbtype)
        return


@cli.command("drop", short_help="Drop database")
@click.option(
    "dbname",
    "--dbname",
    "-d",
    default="",
    help="Database name or path to the database",
)
@click.option(
    "yes",
    "--yes",
    "-y",
    is_flag=True,
    help="Do not ask for confirmation",
)
@pass_context
def db_drop(ctx, dbname, yes):
    """Drop database

    \b
    """
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype == "sqlite":
        ldbname = ctx.gconfig.get("db", "dbpath")
    else:
        ldbname = ctx.gconfig.get("db", "dbname")
    if len(dbname) > 0:
        ldbname = dbname
    if not yes:
        print("Dropping database. Are you sure? (y/n):", end=" ")
        option = input()
        if option != "y":
            ctx.vlog("Skip dropping database [%s]", ldbname)
            return

    ctx.vlog("Dropping database [%s]", ldbname)

    if dbtype == "mysql":
        e = create_engine(ctx.gconfig.get("db", "adminurl"))
        e.execute("drop database {0}".format(ldbname))
    elif dbtype == "postgresql":
        scmd = (
            'psql "postgresql://{0}:{1}@{2}" -c "drop database {3} "'
        ).format(
            ctx.gconfig.get("db", "adminuser"),
            ctx.gconfig.get("db", "adminpassword"),
            ctx.gconfig.get("db", "host"),
            ldbname,
        )
        os.system(scmd)
    elif dbtype == "sqlite":
        if not os.path.isfile(ldbname):
            ctx.vlog("Database file [%s] does not exist", ldbname)
        else:
            os.remove(ldbname)
        return
    else:
        ctx.vlog("Database type [%s] not supported yet", dbtype)
        return


def db_create_tables_list(ctx, directory, group):
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype != "mysql":
        ctx.vlog("Database type [%s] not supported yet", dbtype)
        return
    ldirectory = ""
    if len(directory) > 0:
        ldirectory = directory
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    db_create_sql_group(ctx, e, ldirectory, group)


@cli.command("create-tables-basic", short_help="Create basic database tables")
@click.option(
    "scriptsdirectory",
    "--scripts-directory",
    "-s",
    default="",
    help="Path to the directory with db schema files",
)
@pass_context
def db_create_tables_basic(ctx, scriptsdirectory):
    """Create basic database tables

    \b
    """
    ldirectory = ctx.gconfig.get("db", "scriptsdirectory")
    if len(scriptsdirectory) > 0:
        ldirectory = scriptsdirectory
    db_create_tables_list(ctx, ldirectory, KDB_GROUP_BASIC)


@cli.command(
    "create-tables-standard", short_help="Create standard database tables"
)
@click.option(
    "scriptsdirectory",
    "--scripts-directory",
    "-s",
    default="",
    help="Path to the directory with db schema files",
)
@pass_context
def db_create_tables_standard(ctx, scriptsdirectory):
    """Create standard database tables

    \b
    """
    ldirectory = ctx.gconfig.get("db", "scriptsdirectory")
    if len(scriptsdirectory) > 0:
        ldirectory = scriptsdirectory
    db_create_tables_list(ctx, ldirectory, KDB_GROUP_STANDARD)


@cli.command("create-tables-extra", short_help="Create extra database tables")
@click.option(
    "scriptsdirectory",
    "--scripts-directory",
    "-s",
    default="",
    help="Path to the directory with db schema files",
)
@pass_context
def db_create_tables_extra(ctx, scriptsdirectory):
    """Create extra database tables

    \b
    """
    ldirectory = ctx.gconfig.get("db", "scriptsdirectory")
    if len(scriptsdirectory) > 0:
        ldirectory = scriptsdirectory
    db_create_tables_list(ctx, ldirectory, KDB_GROUP_EXTRA)


@cli.command(
    "create-tables-presence", short_help="Create presence database tables"
)
@click.option(
    "scriptsdirectory",
    "--scripts-directory",
    "-s",
    default="",
    help="Path to the directory with db schema files",
)
@pass_context
def db_create_tables_presence(ctx, scriptsdirectory):
    """Create presence database tables

    \b
    """
    ldirectory = ctx.gconfig.get("db", "scriptsdirectory")
    if len(scriptsdirectory) > 0:
        ldirectory = scriptsdirectory
    db_create_tables_list(ctx, ldirectory, KDB_GROUP_PRESENCE)


@cli.command("create-tables-uid", short_help="Create uid database tables")
@click.option(
    "scriptsdirectory",
    "--scripts-directory",
    "-s",
    default="",
    help="Path to the directory with db schema files",
)
@pass_context
def db_create_tables_uid(ctx, scriptsdirectory):
    """Create uid database tables

    \b
    """
    ldirectory = ctx.gconfig.get("db", "scriptsdirectory")
    if len(scriptsdirectory) > 0:
        ldirectory = scriptsdirectory
    db_create_tables_list(ctx, ldirectory, KDB_GROUP_UID)


@cli.command(
    "create-tables-group",
    short_help="Create the group of database tables for a specific extension",
)
@click.option(
    "scriptsdirectory",
    "--scripts-directory",
    "-s",
    default="",
    help="Path to the directory with db schema files",
)
@click.argument("gname", metavar="<gname>")
@pass_context
def db_create_tables_group(ctx, scriptsdirectory, gname):
    """Create the group of database tables for a specific extension

    \b
    Parameters:
        <gname> - the name of the group of tables
    """
    ldirectory = ctx.gconfig.get("db", "scriptsdirectory")
    if len(scriptsdirectory) > 0:
        ldirectory = scriptsdirectory
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    fpath = ldirectory + "/" + gname + "-create.sql"
    dbutils_exec_sqlfile(ctx, e, fpath)


@cli.command("grant", short_help="Create db access users and grant privileges")
@click.option(
    "dbname",
    "--dbname",
    "-d",
    default="",
    help="Database name",
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
    db_create_mysql_users(ctx, e, ldbname, False, False)


def db_revoke_host_users(ctx, e, dbname, dbhost, dbrwuser, dbrouser):
    e.execute(
        "REVOKE ALL PRIVILEGES ON {0}.* TO {1!r}@{2!r}".format(
            dbname, dbrwuser, dbhost
        )
    )
    e.execute("DROP USER {0!r}@{1!r}".format(dbrwuser, dbhost))
    e.execute(
        "REVOKE SELECT PRIVILEGES ON {0}.* TO {1!r}@{2!r}".format(
            dbname, dbrouser, dbhost
        )
    )
    e.execute("DROP USER {0!r}@{1!r}".format(dbrouser, dbhost))


def db_revoke_users(ctx, e, dbname):
    dbhost = ctx.gconfig.get("db", "host")
    dbrwuser = ctx.gconfig.get("db", "rwuser")
    dbrouser = ctx.gconfig.get("db", "rouser")
    dbaccesshost = ctx.gconfig.get("db", "accesshost")
    db_revoke_host_users(ctx, e, dbname, dbhost, dbrwuser, dbrouser)
    if dbhost != "localhost":
        db_revoke_host_users(
            ctx,
            e,
            dbname,
            "localhost",
            dbrwuser,
            dbrouser,
        )
    if len(dbaccesshost) > 0:
        db_revoke_host_users(
            ctx,
            e,
            dbname,
            dbaccesshost,
            dbrwuser,
            dbrouser,
        )


@cli.command("revoke", short_help="Revoke db access privileges")
@click.option(
    "dbname",
    "--dbname",
    "-d",
    default="",
    help="Database name",
)
@pass_context
def db_revoke(ctx, dbname):
    """Revoke db access privileges

    \b
    """
    dbtype = ctx.gconfig.get("db", "type")
    if dbtype != "mysql":
        ctx.vlog("Database type [%s] not supported yet", dbtype)
        return
    ldbname = ctx.gconfig.get("db", "dbname")
    if len(dbname) > 0:
        ldbname = dbname
    ctx.vlog("Revoke access to database [%s]", ldbname)
    e = create_engine(ctx.gconfig.get("db", "adminurl"))
    db_revoke_users(ctx, e, ldbname)


@cli.command(
    "version-set", short_help="Set the version number for a table structure"
)
@click.option(
    "vertable",
    "--version-table",
    default="version",
    help="Name of the table with version records",
)
@click.argument("table", metavar="<table>")
@click.argument("version", metavar="<version>", type=int)
@pass_context
def db_version_set(ctx, vertable, table, version):
    """Set the version number for a table structure

    \b
    Parameters:
        <table> - Name of the table to set the version for
        <version> - Version number
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "delete from {0} where table_name={1!r}".format(
            vertable.encode("ascii", "ignore").decode(),
            table.encode("ascii", "ignore").decode(),
        )
    )
    e.execute(
        "insert into {0} (table_name, table_version) values ({1!r}, {2})".format(
            vertable.encode("ascii", "ignore").decode(),
            table.encode("ascii", "ignore").decode(),
            version,
        )
    )


@cli.command(
    "version-get", short_help="Get the version number for a table structure"
)
@click.option(
    "vertable",
    "--version-table",
    default="version",
    help="Name of the table with version records",
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
@click.argument("table", metavar="<table>")
@pass_context
def db_version_get(ctx, vertable, oformat, ostyle, table):
    """Get the version number for a table structure

    \b
    Parameters:
        <table> - Name of the table to get the version for
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    res = e.execute(
        "select * from {0} where table_name={1!r}".format(
            vertable.encode("ascii", "ignore").decode(),
            table.encode("ascii", "ignore").decode(),
        )
    )
    ioutils_dbres_print(ctx, oformat, ostyle, res)
