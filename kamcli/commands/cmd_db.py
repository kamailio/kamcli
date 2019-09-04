import os
import sys
import click
import hashlib
import pprint
import json
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec
from kamcli.ioutils import ioutils_dbres_print
from kamcli.ioutils import ioutils_formats_list

##
#
#
@click.group('db', help='Raw database operations')
@pass_context
def cli(ctx):
    pass


##
#
#
@cli.command('connect', help='Launch db cli and connect to database')
@pass_context
def db_connect(ctx):
    dbtype = ctx.gconfig.get('db', 'type')
    if dbtype.lower() == "mysql":
        scmd = "mysql -h {0} -u {1} -p{2} {3}".format(ctx.gconfig.get('db', 'host'),
                ctx.gconfig.get('db', 'rwuser'), ctx.gconfig.get('db', 'rwpassword'), ctx.gconfig.get('db', 'dbname'))
    elif dbtype == "postgres":
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


##
#
#
@cli.command('clirun', help='Run SQL statement via cli')
@click.argument('query', metavar='<query>')
@pass_context
def db_clirun(ctx, query):
    dbtype = ctx.gconfig.get('db', 'type')
    if dbtype == "mysql":
        scmd = 'mysql -h {0} -u {1} -p{2} -e "{3} ;" {4}'.format(ctx.gconfig.get('db', 'host'),
                ctx.gconfig.get('db', 'rwuser'), ctx.gconfig.get('db', 'rwpassword'), query, ctx.gconfig.get('db', 'dbname'))
    elif dbtype == "postgres":
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


##
#
#
@cli.command('clishow', help='Show content of table via cli')
@click.argument('table', metavar='<table>')
@pass_context
def db_clishow(ctx, table):
    dbtype = ctx.gconfig.get('db', 'type')
    if dbtype == "mysql":
        scmd = 'mysql -h {0} -u {1} -p{2} -e "select * from {3} ;" {4}'.format(ctx.gconfig.get('db', 'host'),
                ctx.gconfig.get('db', 'rwuser'), ctx.gconfig.get('db', 'rwpassword'), table, ctx.gconfig.get('db', 'dbname'))
    elif dbtype == "postgres":
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


##
#
#
@cli.command('clishowg', help='Show content of table via cli')
@click.argument('table', metavar='<table>')
@pass_context
def db_clishowg(ctx, table):
    dbtype = ctx.gconfig.get('db', 'type')
    if dbtype == "mysql":
        scmd = 'mysql -h {0} -u {1} -p{2} -e "select * from {3} \G" {4}'.format(ctx.gconfig.get('db', 'host'),
                ctx.gconfig.get('db', 'rwuser'), ctx.gconfig.get('db', 'rwpassword'), table, ctx.gconfig.get('db', 'dbname'))
    elif dbtype == "postgres":
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    else:
        ctx.log("unsupported database type [%s]", dbtype)
        sys.exit()
    os.system(scmd)


##
#
#
@cli.command('show', help='Show content of a table')
@click.option('oformat', '--output-format', '-F',
                type=click.Choice(ioutils_formats_list),
                default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
                default=None, help='Style of the output (tabulate table format)')
@click.argument('table', metavar='<table>')
@pass_context
def db_show(ctx, oformat, ostyle, table):
    ctx.vlog('Content of database table [%s]', table)
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    res = e.execute('select * from {0}'.format(table))
    ioutils_dbres_print(ctx, oformat, ostyle, res)


##
#
#
@cli.command('showcreate', help='Show content of a table')
@click.option('oformat', '--output-format', '-F',
                type=click.Choice(ioutils_formats_list),
                default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
                default=None, help='Style of the output (tabulate table format)')
@click.argument('table', metavar='<table>')
@pass_context
def db_showcreate(ctx, oformat, ostyle, table):
    ctx.vlog('Show create of database table [%s]', table)
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    res = e.execute('show create table {0}'.format(table))
    ioutils_dbres_print(ctx, oformat, ostyle, res)


