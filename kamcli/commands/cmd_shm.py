import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group(
    "shm",
    help="Shared memory (shm) management",
    short_help="Shared memory (shm) management",
)
@pass_context
def cli(ctx):
    pass


@cli.command("stats", short_help="Show the stats for shared (shm) memory")
@pass_context
def shm_stats(ctx):
    """Show the stats for shared (shm) memory

    \b
    """
    command_ctl(ctx, "shm.stats", [])


@cli.command(
    "info", short_help="Show the info for shared (shm) memory manager"
)
@pass_context
def shm_info(ctx):
    """Show the info for shared (shm) memory manager

    \b
    """
    command_ctl(ctx, "shm.info", [])
