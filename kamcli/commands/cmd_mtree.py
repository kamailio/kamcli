import click
import hashlib
import json
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec
from kamcli.iorpc import command_ctl


##
#
#
@click.group('mtree', help='Manage mtree module (memory trees)')
@pass_context
def cli(ctx):
    pass


##
#
#
@cli.command('add', short_help='Add a new mtree record')
@click.option('tname', '--tname', default='',
            help='Tree name to be stored in column tname (default: "")')
@click.option('coltprefix', '--coltprefix', default='tprefix',
            help='Column name for prefix (default: "tprefix")')
@click.option('coltvalue', '--coltvalue', default='tvalue',
            help='Column name for value (default: "tvalue")')
@click.argument('dbtname', metavar='<dbtname>')
@click.argument('tprefix', metavar='<tprefix>')
@click.argument('tvalue', metavar='<tvalue>')
@pass_context
def mtree_add(ctx, tname, coltprefix, coltvalue, dbtname, tprefix, tvalue):
    """Add a new tree record in database table

    \b
    Parameters:
        <dbtname> - name of tree database table
        <tprefix> - tree prefix
        <tvalue>  - associated value for prefix
    """
    ctx.vlog('Adding to tree [%s] record [%s] => [%s]', dbtname, tprefix, tvalue)
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    if not tname:
        e.execute('insert into {0!r} ({1!r}, {2!r}) values ({3!r}, {4!r})'.format(dbtname.encode('ascii','ignore'), coltprefix.encode('ascii','ignore'), coltvalue.encode('ascii','ignore'), tprefix.encode('ascii','ignore'), tvalue.encode('ascii','ignore')))
    else:
        e.execute('insert into {0!r} (tname, {1!r}, {2!r}) values ({3!r}, {4!r}, {5!r})'.format(dbtname.encode('ascii','ignore'), tname.encode('ascii','ignore'), coltprefix.encode('ascii','ignore'), coltvalue.encode('ascii','ignore'), tprefix.encode('ascii','ignore'), tvalue.encode('ascii','ignore')))


##
#
#
@cli.command('rm', short_help='Remove a destination from dispatcher table')
@click.option('coltprefix', '--coltprefix', default='tprefix',
            help='Column name for prefix (default: "tprefix")')
@click.argument('dbtname', metavar='<dbtname>')
@click.argument('tprefix', metavar='<tprefix>')
@pass_context
def dispatcher_rm(ctx, coltprefix, dbtname, tprefix):
    """Remove a record from tree database table

    \b
    Parameters:
        <dbtname> - name of tree database table
        <tprefix> - tree prefix value to match the record
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    e.execute('delete from {0!r} where {1!r}={2!r}'.format(dbtname.encode('ascii','ignore'), coltprefix.encode('ascii','ignore'), tprefix.encode('ascii','ignore')))


##
#
#
@cli.command('showdb', short_help='Show dispatcher records in database')
@click.option('oformat', '--output-format', '-F',
                type=click.Choice(['raw', 'json', 'table', 'dict']),
                default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
                default=None, help='Style of the output (tabulate table format)')
@click.option('coltprefix', '--coltprefix', default='tprefix',
            help='Column name for prefix (default: "tprefix")')
@click.argument('dbtname', metavar='<dbtname>')
@click.argument('tprefix', nargs=-1, metavar='[<tprefix>]')
@pass_context
def dispatcher_showdb(ctx, oformat, ostyle, coltprefix, dbtable, tprefix):
    """Show details for records in mtree database table

    \b
    Parameters:
        <dbtname> - name of tree database table
        <tprefix> - tree prefix value to match the record
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    if not tprefix:
        ctx.vlog('Showing all tree database records')
        res = e.execute('select * from {0!r}'.format(dbtname.encode('ascii','ignore')))
    else:
        ctx.vlog('Showing tree database records for prefix')
        res = e.execute('select * from {0!r} where {1!r}={2!r}'.format(dbtname.encode('ascii','ignore'), coltprefix.encode('ascii','ignore'), tprefix.encode('ascii','ignore')))
    ioutils_dbres_print(ctx, oformat, ostyle, res)


##
#
#
@cli.command('list', short_help='Show the records in memory tree')
@click.argument('tname', metavar='<tname>')
@pass_context
def mtree_show(ctx, tname):
    """Show the tree records in memory

    \b
    Parameters:
        <tname> - tree name
    """
    command_ctl(ctx, 'mtree.list', [ tname ])


##
#
#
@cli.command('reload', short_help='Reload tree records from database into memory')
@click.argument('tname', metavar='<tname>')
@pass_context
def mtree_reload(ctx, tname):
    """Reload tree records from database into memory

    \b
    Parameters:
        <tname> - tree name
    """
    command_ctl(ctx, 'mtree.reload', [ tname ])

