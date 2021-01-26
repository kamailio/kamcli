import click
import json
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command("sipreq", short_help="Send a SIP request via RPC command")
@click.option(
    "nowait", "--nowait", "-n", is_flag=True, help="Do not wait for response",
)
@click.option(
    "method",
    "--method",
    "-m",
    default="OPTIONS",
    help='SIP method (default: "OPTIONS")',
)
@click.option(
    "furi", "--furi", "-f", default="", help='From URI (default: "")'
)
@click.option(
    "curi", "--curi", "-c", default="", help='Contact URI (default: "")'
)
@click.option(
    "duri", "--duri", "-d", default=".", help='Destination URI (default: "")'
)
@click.option(
    "socket",
    "--socket",
    "-s",
    default=".",
    help='Socket for sending (default: "")',
)
@click.option(
    "body", "--body", "-b", default="", help='Destination URI (default: "")'
)
@click.argument("uri", nargs=1, metavar="[<uri>]")
@pass_context
def cli(ctx, nowait, method, furi, curi, duri, socket, body, uri):
    """Send a SIP request via RPC command

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
    lcuri = lfrom
    if len(curi) != 0:
        lcuri = curi
    plist = [
        method,
        uri,
        duri,
        socket,
        "From: <"
        + lfrom
        + ">\r\nTo: <"
        + uri
        + ">\r\n Contact: <"
        + lcuri
        + ">\r\n",
        body,
    ]
    command_ctl(ctx, lcmd, plist)
