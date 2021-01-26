import click
import json
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command("ping", short_help="Send an OPTIONS ping request")
@click.option(
    "nowait", "--nowait", "-n", is_flag=True, help="Do wait for response",
)
@click.option("furi", "--furi", default="", help='From URI (default: "")')
@click.argument("uri", nargs=1, metavar="[<uri>]")
@pass_context
def cli(ctx, nowait, furi, uri):
    """Send an OPTIONS ping request

        Parameters:
            - <uri> - the SIP URI of the target
    \b
    """
    lcmd = "tm.t_uac_wait_block"
    if nowait:
        lcmd = "tm.t_uac_start"
    lfrom = ""
    if len(furi) == 0:
        ldomain = ctx.gconfig.get("main", "domain", fallback="localhost")
        lfrom = "sip:daemon@" + ldomain
    else:
        lfrom = furi
    plist = [
        "OPTIONS",
        uri,
        ".",
        ".",
        "From: <"
        + lfrom
        + ">\r\nTo: <"
        + uri
        + ">\r\n Contact: <"
        + lfrom
        + ">\r\n",
    ]
    command_ctl(ctx, lcmd, plist)
