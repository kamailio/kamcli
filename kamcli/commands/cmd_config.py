import os
import sys
import click
from kamcli.cli import pass_context

@click.group('config', help='Manage the config file')
@pass_context
def cli(ctx):
    pass


@cli.command('raw', short_help='Display raw content of configuration file')
@pass_context
def config_raw(ctx):
    """Show content of configuration file for kamcli"""
    ctx.log('\n---')
    ctx.gconfig.write(sys.stdout)
    ctx.log('\n---')


@cli.command('show', short_help='Show expanded content of configuration file sections')
@click.argument('sections', nargs=-1, metavar='<sections>')
@pass_context
def config_show(ctx, sections):
    """Show expanded content of configuration file section"""
    if sections:
        ctx.log('\n---')
    for s in sections:
        ctx.log('[%s]', s)
        for k, v in ctx.gconfig.items(s):
            ctx.log("%s= %s", k, v)
        ctx.log('\n---')


@cli.command('paths', short_help='Show the paths of configuration files')
@pass_context
def config_paths(ctx):
    """Show the patsh of configuration files for kamcli"""
    print
    print ctx.gconfig_paths
    print

