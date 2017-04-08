import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


##
#
#
@click.group('srv', help='Common server interaction commands')
@pass_context
def cli(ctx):
    pass

##
#
#
@cli.command('sockets', short_help='Show the list of listen sockets')
@pass_context
def srv_sockets(ctx):
    """Show the list of listen sockets

    \b
    """
    command_ctl(ctx, 'corex.list_sockets')

##
#
#
@cli.command('aliases', short_help='Show the list of server domain aliases')
@pass_context
def srv_aliases(ctx):
    """Show the list of server domain aliases

    \b
    """
    command_ctl(ctx, 'corex.list_aliases')

##
#
#
@cli.command('rpclist', short_help='Show the list of server rpc commands')
@pass_context
def srv_rpclist(ctx):
    """Show the list of server rpc commands

    \b
    """
    command_ctl(ctx, 'system.listMethods')

