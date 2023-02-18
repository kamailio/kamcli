import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl_name
from kamcli.iorpc import command_jsonrpc_fifo
from kamcli.iorpc import command_jsonrpc_socket


@click.command("jsonrpc", short_help="Execute JSONRPC commands")
@click.option(
    "dryrun",
    "--dry-run",
    is_flag=True,
    help="Do not execute the command, only print it",
)
@click.option(
    "nolog",
    "--no-log",
    is_flag=True,
    help="Do not print the log with executed command",
)
@click.option(
    "storepath",
    "--store-path",
    "-s",
    default="",
    help="Path on server where to store the result",
)
@click.argument("cmd", nargs=1, metavar="[<command>]")
@click.argument("params", nargs=-1, metavar="[<params>]")
@pass_context
def cli(ctx, dryrun, nolog, storepath, cmd, params):
    """Execute JSONRPC command

        \b
        Command alias: rpc
        Parameters:
            - <command> - the JSONRPC command
            - <params>  - parameters for JSONRPC command
                        - by default the value of a parameter is considered
                          of type string
                        - to enforce integer value prefix with 'i:'
                          (e.g., i:10)
                        - string values can be also prefixed with 's:'
                        - if a parameter starts with 's:', prefix it with 's:'
        Examples:
            - jsonrpc system.listMethods
            - jsonrpc core.psx
            - jsonrpc stats.get_statistics all
            - jsonrpc pv.shvSet counter i:123
    """
    if not nolog:
        ctx.log("Running JSONRPC command: [%s]", cmd)
    if ctx.gconfig.get("jsonrpc", "transport") == "socket":
        command_jsonrpc_socket(
            ctx,
            dryrun,
            ctx.gconfig.get("jsonrpc", "srvaddr"),
            ctx.gconfig.get("jsonrpc", "rcvaddr"),
            ctx.gconfig.get("jsonrpc", "outformat"),
            storepath,
            command_ctl_name(cmd, "rpc"),
            params,
        )
    else:
        command_jsonrpc_fifo(
            ctx,
            dryrun,
            ctx.gconfig.get("jsonrpc", "path"),
            ctx.gconfig.get("jsonrpc", "rplnamebase"),
            ctx.gconfig.get("jsonrpc", "outformat"),
            storepath,
            command_ctl_name(cmd, "rpc"),
            params,
        )
