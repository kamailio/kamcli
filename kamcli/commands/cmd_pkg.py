import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group(
    "pkg",
    help="Private memory (pkg) management",
    short_help="Private memory (pkg) management",
)
@pass_context
def cli(ctx):
    pass


@cli.command("stats", short_help="Show the stats for pkg memory")
@pass_context
def pkg_stats(ctx):
    """Show the stats for pkg memory

    \b
    """
    command_ctl(ctx, "pkg.stats", [])


@cli.command("info", short_help="Show the info for pkg memory manager")
@pass_context
def pkg_info(ctx):
    """Show the info for pkg memory manager

    \b
    """
    command_ctl(ctx, "pkg.info", [])
