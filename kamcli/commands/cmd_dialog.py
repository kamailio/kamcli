import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec
from kamcli.iorpc import command_ctl


##
#
#
@click.group('dialog', help='Manage dialog module (active calls tracking)')
@pass_context
def cli(ctx):
    pass


##
#
#
@cli.command('showdb', short_help='Show dialog records in database')
@click.option('oformat', '--output-format', '-F',
                type=click.Choice(['raw', 'json', 'table', 'dict']),
                default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
                default=None, help='Style of the output (tabulate table format)')
@pass_context
def dialog_showdb(ctx, oformat, ostyle):
    """Show details for records in dialog table

    \b
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    ctx.vlog('Showing all dialog records')
    res = e.execute('select * from dialog')
    ioutils_dbres_print(ctx, oformat, ostyle, res)


##
#
#
@cli.command('list', short_help='Show details for dialog records in memory')
@pass_context
def dialog_list(ctx):
    """Show details for dialog records in memory

    \b
    """
    command_ctl(ctx, 'dlg.list', [ ])


##
#
#
@cli.command('terminate', short_help='Send BYE to the dialog identified by call-id, from-tag and to-tag')
@click.argument('callid', metavar='<domain>')
@click.argument('fromtag', metavar='<fromtag>')
@click.argument('totag', metavar='<totag>')
@pass_context
def dialog_list(ctx, callid, fromtag, totag):
    """Send BYE to the dialog identified by callid, from-tag and to-tag

    \b
    Parameters:
        <callid> - Call-Id value
        <fromtag> - From-Tag value
        <to-tag> - To-Tag value
    """
    command_ctl(ctx, 'dlg.terminate_dlg', [ callid, fromtag, totag ])


##
#
#
@cli.command('stats_active', short_help='Show statistics for active dialogs')
@pass_context
def dialog_stats_active(ctx):
    """Show statistics for active dialogs

    \b
    """
    command_ctl(ctx, 'dlg.stats_active', [ ])


##
#
#
@cli.command('profile_list', short_help='List the content of a profile')
@click.argument('profile', metavar='<profile>')
@pass_context
def dialog_profile_list(ctx, profile):
    """List the dialogs groupped in a profile

    \b
    Parameters:
        <profile> - the name of the profile
    """
    command_ctl(ctx, 'dlg.profile_list', [ profile ])
