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
    "hdrs", "--hdrs", "-a", default="", help='Additional headers (default: "")'
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
def cli(ctx, nowait, method, furi, curi, duri, hdrs, socket, body, uri):
    """Send a SIP request via RPC command

        Parameters:
            - <uri> - the SIP URI of the target

        Note: additional headers must not include From, To or Contact
        headers, these are generated from the other parameters. If From
        URI is not provided, then it is generated using local host. The To
        URI is set to <uri>. If Contact URI is not provided, then it is set
        to From URI. If --curi=none, the Contact header is not added.
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
        if curi == "none":
            lcuri = ""
        else:
            lcuri = curi
    lhdrs = "From: <" + lfrom + ">\r\nTo: <" + uri + ">\r\n"
    if len(lcuri) != 0:
        lhdrs += "Contact: <" + lcuri + ">\r\n"
    if len(hdrs) != 0:
        lhdrs += hdrs
        if lhdrs[-2:] != "\r\n":
            lhdrs += "\r\n"
    plist = [
        method,
        uri,
        duri,
        socket,
        lhdrs,
        body,
    ]
    command_ctl(ctx, lcmd, plist)
