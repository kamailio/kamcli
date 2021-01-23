import click
import json
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command("ping", short_help="Send an OPTIONS ping request")
@click.option("furi", "--furi", default="", help='From URI (default: "")')
@click.argument("uri", nargs=1, metavar="[<uri>]")
@pass_context
def cli(ctx, furi, uri):
    """Send an OPTIONS ping request

        Parameters:
            - <uri> - the SIP URI of the target
    \b
    """
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
    command_ctl(ctx, "tm.t_uac_wait_block", plist)
