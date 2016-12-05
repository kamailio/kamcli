import os
import time
import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


##
#
#
@click.command('rpcmethods', short_help='Print the list of available raw RPC methods')
@pass_context
def cli(ctx):
    """Print the list of available raw RPC methods

    \b
    Show all available methods that can be executed with command 'rpc'.
    Examples:
        - kamcli rpcmethods
        - kamcli rpc <method> <params>
    """
    command_ctl(ctx, 'system.listMethods', [])
