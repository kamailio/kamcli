import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group('rtpengine', help='Manage rtpengine module')
@pass_context
def cli(ctx):
    pass


@cli.command('showdb', short_help='Show the rtpengine records in database')
@click.option('oformat', '--output-format', '-F',
              type=click.Choice(['raw', 'json', 'table', 'dict']),
              default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
              default=None, help='Style of the output (tabulate table format)')
@pass_context
def rtpengine_showdb(ctx, oformat, ostyle):
    """Show the rtpengine records in database table

    \b
    Parameters:
        none
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    ctx.vlog('Showing all rtpengine database records')
    res = e.execute('select * from rtpengine')
    ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command('show', short_help='Show the rtpengine records in memory')
@pass_context
def rtpengine_show(ctx):
    """Show the rtpengine records in memory

    \b
    Parameters:
        none
    """
    command_ctl(ctx, 'rtpengine.show', ['all'])


@cli.command(
    'reload',
    short_help='Reload the rtpengine records from database into memory'
)
@pass_context
def rtpengine_reload(ctx):
    """Reload the rtpengine records from database into memory

    \b
    Parameters:
        none
    """
    command_ctl(ctx, 'rtpengine.reload', [])
