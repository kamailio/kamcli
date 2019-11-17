import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.group("address", help="Manage permissions address records")
@pass_context
def cli(ctx):
    pass


@cli.command("add", short_help="Add a new record to address table")
@click.option(
    "mask", "--mask", type=int, default=32, help="Mask value (default 32)"
)
@click.option(
    "port", "--port", type=int, default=0, help="Port value (default 0)"
)
@click.option("tag", "--tag", default="", help='Tag value (default: "")')
@click.argument("group", metavar="<group>", type=int)
@click.argument("address", metavar="<address>")
@pass_context
def address_add(ctx, mask, port, tag, group, address):
    """Add a new record to address db table

    \b
    Parameters:
        <group> - group id
        <address> - IP address
    """
    ctx.vlog("Adding to group id [%d] address [%s]", group, address)
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute(
        "insert into address (grp, ip_addr, mask, port, tag) values "
        "({0}, {1!r}, {2}, {3}, {4!r})".format(
            group,
            address.encode("ascii", "ignore").decode(),
            mask,
            port,
            tag.encode("ascii", "ignore").decode(),
        )
    )


@cli.command("rm", short_help="Remove a record from address db table")
@click.option("mask", "--mask", type=int, help="Mask value")
@click.option("port", "--port", type=int, help="Port value")
@click.argument("group", metavar="<group>", type=int)
@click.argument("address", metavar="<address>")
@pass_context
def address_rm(ctx, mask, port, group, address):
    """Remove a record from address db table

    \b
    Parameters:
        <group> - group id
        <address> - IP address
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    addr = address.encode("ascii", "ignore").decode()
    if not mask:
        if not port:
            e.execute(
                "delete from address where grp={0} and ip_addr={1!r}".format(
                    group, addr
                )
            )
        else:
            e.execute(
                "delete from address where grp={0} and ip_addr={1!r} "
                "and port={2}".format(group, addr, port)
            )
    else:
        if not port:
            e.execute(
                "delete from address where grp={0} and "
                "ip_addr={1!r} and mask={2}".format(group, addr, mask)
            )
        else:
            e.execute(
                "delete from address where setid={0} and destination={1!r} "
                "and mask={2} and port={3}".format(group, addr, mask, port)
            )


@cli.command("showdb", short_help="Show address records in database")
@click.option(
    "oformat",
    "--output-format",
    "-F",
    type=click.Choice(["raw", "json", "table", "dict"]),
    default=None,
    help="Format the output",
)
@click.option(
    "ostyle",
    "--output-style",
    "-S",
    default=None,
    help="Style of the output (tabulate table format)",
)
@click.argument("group", nargs=-1, metavar="[<group>]", type=int)
@pass_context
def address_showdb(ctx, oformat, ostyle, group):
    """Show details for records in address db table

    \b
    Parameters:
        <group> - address group
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    if not group:
        ctx.vlog("Showing all address records")
        res = e.execute("select * from address")
    else:
        ctx.vlog("Showing address records for group")
        res = e.execute("select * from address where group=%d", group)
    ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command("list", short_help="Show details for address records in memory")
@click.option(
    "tag",
    "--mode",
    default="all",
    help="What to be printed (all, addresses, subnets, domains)",
)
@click.argument("group", nargs=-1, metavar="[<group>]", type=int)
@pass_context
def address_list(ctx, mode, group):
    """Show details for address records in memory

    \b
    Parameters:
        <group> - address group
    """
    if mode == "all":
        command_ctl(ctx, "permissions.addressDump", [])
        command_ctl(ctx, "permissions.subnetDump", [])
        command_ctl(ctx, "permissions.domainDump", [])
    elif mode == "addresses":
        command_ctl(ctx, "permissions.addressDump", [])
    elif mode == "subnets":
        command_ctl(ctx, "permissions.subnetDump", [])
    elif mode == "domains":
        command_ctl(ctx, "permissions.domainDump", [])
    else:
        command_ctl(ctx, "permissions.addressDump", [])


@cli.command(
    "reload", short_help="Reload address records from database into memory"
)
@pass_context
def address_reload(ctx):
    """Reload address records from database into memory
    """
    command_ctl(ctx, "permissions.addressReload", [])
