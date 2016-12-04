import os
import sys
import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl_name
from kamcli.iorpc import command_mi_fifo

@click.command('mi', short_help='Execute raw MI command')
@click.option('dryrun', '--dry-run', is_flag=True,
            help='Do not execute the command, only print it')
@click.argument('cmd', nargs=1, metavar='[<command>]')
@click.argument('params', nargs=-1, metavar='[<params>]')
@pass_context
def cli(ctx, dryrun, cmd, params):
    """Execute raw MI command

        \b
        Command alias: fifo
        Parameters:
            - <command> - the MI command
            - <params>  - parameters for command
        Examples:
            - mi uptime
            - mi ps
    """
    ctx.log("Running MI command: [%s]", cmd)
    command_mi_fifo(ctx, dryrun, ctx.gconfig.get('mi', 'path'),
                ctx.gconfig.get('mi', 'rplnamebase'), "raw",
                cmd, params)

