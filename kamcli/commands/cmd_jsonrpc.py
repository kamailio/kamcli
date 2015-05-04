import os
import sys
import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_jsonrpc_fifo

@click.command('jsonrpc', short_help='Execute JSONRPC command')
@click.option('dryrun', '--dry-run', is_flag=True,
            help='Do not execute the command, only print it')
@click.argument('cmd', nargs=1, metavar='[<command>]')
@click.argument('params', nargs=-1, metavar='[<params>]')
@pass_context
def cli(ctx, dryrun, cmd, params):
    """Execute JSONRPC command

        \b
        Parameters:
            - <command> - the JSONRPC command
            - <params>  - parameters for JSONRPC command
                        - by default the value of a parameter is considered
                          of type string
                        - to enforce integer value prefix with 'i:' (e.g., i:10)
                        - string values can be also prefixed with 's:'
                        - if a parameter starts with 's:', prefix it with 's:'
        Examples:
            - jsonrpc system.listMethods
            - jsonrpc core.psx
            - jsonrpc stats.get_statistics all
            - jsonrpc pv.shvSet counter i:123
    """
    ctx.log("Running JSONRPC command: [%s]", cmd)
    command_jsonrpc_fifo(ctx, dryrun, "/var/run/kamailio/kamailio_jsonrpc_fifo",
            "kamailio_jsonrpc_fifo_reply", "json", cmd, params)

