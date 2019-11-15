import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group('tcp', help='Manage TCP options and connections')
@pass_context
def cli(ctx):
    pass


@cli.command('options', short_help='Show details for TCP options in memory')
@pass_context
def tcp_options(ctx):
    """Show details for TCP options in memory

    \b
    """
    command_ctl(ctx, 'core.tcp_options', [])


@cli.command('list', short_help='List current TCP connections')
@pass_context
def tcp_list(ctx):
    """List current TCP connections

    \b
    """
    command_ctl(ctx, 'core.tcp_list', [])


@cli.command('info', short_help='Summary of TCP usage')
@pass_context
def tcp_info(ctx):
    """Summary of TCP usage

    \b
    """
    command_ctl(ctx, 'core.tcp_info', [])
