import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec
from kamcli.iorpc import command_ctl


##
#
#
@click.group('dispatcher', help='Manage dispatcher module (load balancer)')
@pass_context
def cli(ctx):
    pass


##
#
#
@cli.command('add', short_help='Add a new dispatcher destination')
@click.option('flags', '--flags', type=int, default=0,
            help='Flags value')
@click.option('priority', '--priority', type=int, default=0,
            help='Priority value')
@click.option('attrs', '--attrs', default='',
            help='Attributes (default: "")')
@click.option('description', '--desc', default='',
            help='Description (default: "")')
@click.argument('setid', metavar='<setid>', type=int)
@click.argument('destination', metavar='<destination>')
@pass_context
def dispatcher_add(ctx, flags, priority, attrs, description, setid, destination):
    """Add a new destination in a set of dispatcher db table

    \b
    Parameters:
        <setid> - dispatching set id
        <destination> - SIP URI for destination
    """
    ctx.vlog('Adding to setid [%d] destination [%s]', setid, destination)
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    e.execute('insert into dispatcher (setid, destination, flags, priority, attrs, description) values ({0}, {1!r}, {2}, {3}, {4!r}, {5!r})'.format(setid, destination.encode('ascii','ignore').decode(), flags, priority, attrs.encode('ascii','ignore').decode(), description.encode('ascii','ignore').decode()))


##
#
#
@cli.command('rm', short_help='Remove a destination from dispatcher table')
@click.argument('setid', metavar='<setid>', type=int)
@click.argument('destination', metavar='<destination>')
@pass_context
def dispatcher_rm(ctx, setid, destination):
    """Remove a destination from db dispatcher table

    \b
    Parameters:
        <setid> - dispatching set id
        <destination> - SIP URI for destination
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    e.execute('delete from dispatcher where setid={0} and destination={1!r}'.format(setid, destination.encode('ascii','ignore').decode()))


##
#
#
@cli.command('showdb', short_help='Show dispatcher records in database')
@click.option('oformat', '--output-format', '-F',
                type=click.Choice(['raw', 'json', 'table', 'dict']),
                default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
                default=None, help='Style of the output (tabulate table format)')
@click.argument('setid', nargs=-1, metavar='[<setid>]', type=int)
@pass_context
def dispatcher_showdb(ctx, oformat, ostyle, setid):
    """Show details for records in dispatcher table

    \b
    Parameters:
        [<setid>] - dispatching set id
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    if not setid:
        ctx.vlog('Showing all dispatcher records')
        res = e.execute('select * from dispatcher')
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for s in setid:
            ctx.vlog('Showing dispatcher records for set id')
            res = e.execute('select * from dispatcher where setid=%d', s)
            ioutils_dbres_print(ctx, oformat, ostyle, res)


##
#
#
@cli.command('list', short_help='Show details for dispatcher records in memory')
@pass_context
def dispatcher_list(ctx):
    """Show details for dispatcher records in memory

    \b
    """
    command_ctl(ctx, 'dispatcher.list', [ ])


##
#
#
@cli.command('reload', short_help='Reload dispatcher records from database into memory')
@pass_context
def dispatcher_reload(ctx):
    """Reload dispatcher records from database into memory

    \b
    """
    command_ctl(ctx, 'dispatcher.reload', [ ])


##
#
#
@cli.command('memadd', short_help='Add a new dispatcher destination in memory')
@click.option('flags', '--flags', type=int, default=0,
            help='Flags value')
@click.argument('setid', metavar='<setid>', type=int)
@click.argument('destination', metavar='<destination>')
@pass_context
def dispatcher_memadd(ctx, flags, setid, destination):
    """Add a new destination in a set of dispatcher memory

    \b
    Parameters:
        <setid> - dispatching set id
        <destination> - SIP URI for destination
    """
    ctx.vlog('Adding to setid [%d] destination [%s]', setid, destination)
    command_ctl(ctx, 'dispatcher.add', [ setid, destination, flags ])


##
#
#
@cli.command('memrm', short_help='Remove a destination from dispatcher memory')
@click.argument('setid', metavar='<setid>', type=int)
@click.argument('destination', metavar='<destination>')
@pass_context
def dispatcher_memrm(ctx, setid, destination):
    """Remove a destination from dispatcher memory

    \b
    Parameters:
        <setid> - dispatching set id
        <destination> - SIP URI for destination
    """
    command_ctl(ctx, 'dispatcher.remove', [ setid, destination ])


