import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group("srv", help="Common server interaction commands")
@pass_context
def cli(ctx):
    pass


@cli.command("sockets", short_help="Show the list of listen sockets")
@pass_context
def srv_sockets(ctx):
    """Show the list of listen sockets

    \b
    """
    command_ctl(ctx, "corex.list_sockets")


@cli.command("aliases", short_help="Show the list of server domain aliases")
@pass_context
def srv_aliases(ctx):
    """Show the list of server domain aliases

    \b
    """
    command_ctl(ctx, "corex.list_aliases")


@cli.command("rpclist", short_help="Show the list of server rpc commands")
@pass_context
def srv_rpclist(ctx):
    """Show the list of server rpc commands

    \b
    """
    command_ctl(ctx, "system.listMethods")


@cli.command("info", short_help="Show server info")
@pass_context
def srv_info(ctx):
    """Show server info

    \b
    """
    command_ctl(ctx, "core.info")


@cli.command("modules", short_help="Show server loaded modules")
@pass_context
def srv_modules(ctx):
    """Show server loaded modules

    \b
    """
    command_ctl(ctx, "core.modules")


@cli.command("version", short_help="Show server version")
@pass_context
def srv_version(ctx):
    """Show server version

    \b
    """
    command_ctl(ctx, "core.version")


@cli.command("ppdefines", short_help="Show pre-processor defines")
@click.option(
    "full", "--full", is_flag=True, help="Show full format of the records."
)
@pass_context
def srv_ppdefines(ctx, full):
    """Show pre-processor defines

    \b
    """
    if full:
        command_ctl(ctx, "core.ppdefines_full")
    else:
        command_ctl(ctx, "core.ppdefines")


@cli.command("shm", short_help="Show shared memory details")
@pass_context
def srv_version(ctx):
    """Show shared memory details

    \b
    """
    command_ctl(ctx, "core.shmmem")
