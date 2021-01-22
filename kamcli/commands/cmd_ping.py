import click
import json
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command("ping", short_help="Send an OPTIONS ping request")
@click.argument("uri", nargs=1, metavar="[<uri>]")
@pass_context
def cli(ctx, uri):
    """Send an OPTIONS ping request

        Parameters:
            - <uri> - the SIP URI of the target
    \b
    """
    ldomain = ctx.gconfig.get("main", "domain", fallback="localhost")
    plist = [
        "OPTIONS",
        uri,
        ".",
        ".",
        "From: <sip:daemon@"
        + ldomain
        + ">\r\nTo: <"
        + uri
        + ">\r\n Contact:<sip:daemon@"
        + ldomain
        + ">\r\n",
    ]
    command_ctl(ctx, "tm.t_uac_wait_block", plist)
