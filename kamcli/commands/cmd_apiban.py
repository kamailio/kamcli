import click
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl
import http.client
import json
import time
import pprint


@click.group(
    "apiban", help="Manage APIBan records", short_help="Manage APIBan records",
)
@pass_context
def cli(ctx):
    pass


def apiban_fetch(ctx, key):
    conn = http.client.HTTPSConnection("apiban.org", timeout=4)
    idval = ""
    allAddresses = []
    while True:
        time.sleep(1)
        conn.request("GET", "/api/" + key + "/banned" + idval)
        r1 = conn.getresponse()
        ctx.vlog("response: " + str(r1.status) + " " + r1.reason)
        if r1.status == 200:
            data1 = r1.read()
            jdata = json.loads(data1)
            ctx.vlog(
                "fetched ipaddress array size: " + str(len(jdata["ipaddress"]))
            )
            allAddresses = allAddresses + jdata["ipaddress"]
            if jdata["ID"] == "none":
                break
            else:
                idval = "/" + jdata["ID"]
        else:
            break
    return allAddresses


@cli.command("show", short_help="Show the addresses returned by apiban.org")
@click.option(
    "key", "--key", "-k", default=None, help="The APIBan key",
)
@pass_context
def apiban_show(ctx, key):
    """Show the APIBan addresses

    \b
    """
    ctx.vlog("fetching APIBan records")
    if key is None:
        key = ctx.gconfig.get("apiban", "key", fallback=None)
        if key is None:
            ctx.log("no APIBan key")
            return

    allAddresses = apiban_fetch(ctx, key)
    ctx.vlog("all ip addresses array size: " + str(len(allAddresses)))
    pprint.pprint(allAddresses)
    print()


@cli.command(
    "load", short_help="Load the records from apiban.org to a Kamailio htable"
)
@click.option(
    "key", "--key", "-k", default=None, help="The APIBan key",
)
@click.option(
    "htname", "--htname", "-t", default=None, help="The htable name",
)
@click.option(
    "expire",
    "--expire",
    "-x",
    type=int,
    default=0,
    help="The expire for htable item",
)
@pass_context
def apiban_load(ctx, key, htname, expire):
    """Load the APIBan addresses to a Kamailio htable

    \b
    """
    ctx.vlog("loading APIBan records")
    if key is None:
        key = ctx.gconfig.get("apiban", "key", fallback=None)
        if key is None:
            ctx.log("no APIBan key")
            return
    if htname is None:
        htname = ctx.gconfig.get("apiban", "htname", fallback=None)
        if htname is None:
            htname = "ipban"
    allAddresses = apiban_fetch(ctx, key)
    ctx.vlog("fetched ip addresses - array size: " + str(len(allAddresses)))
    if len(allAddresses) > 0:
        for a in allAddresses:
            command_ctl(ctx, "htable.seti", [htname, a, 1])
            if expire > 0:
                command_ctl(ctx, "htable.setex", [htname, a, 1])
            time.sleep(0.002)
    else:
        ctx.log("no APIBan records")


@cli.command("check", short_help="Check IP address against apiban.org")
@click.option(
    "key", "--key", "-k", default=None, help="The APIBan key",
)
@click.argument("ipaddr", metavar="<ipaddr>")
@pass_context
def apiban_check(ctx, key, ipaddr):
    """Check IP address against apiban.org

    \b
    Parameters:
        <ipaddr> - IP address
    """
    ctx.vlog("cheking address againt apiban.org")
    if key is None:
        key = ctx.gconfig.get("apiban", "key", fallback=None)
        if key is None:
            ctx.log("no APIBan key")
            return

    conn = http.client.HTTPSConnection("apiban.org", timeout=4)
    conn.request("GET", "/api/" + key + "/check/" + ipaddr)
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    data1 = r1.read()
    print(data1)
    print()
