import os
import time
import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


##
#
#
@click.command('ps', short_help='Print the list of kamailio processes')
@pass_context
def cli(ctx):
    """Print details about running kamailio processes

    \b
    """
    command_ctl(ctx, 'core.psx', [])
