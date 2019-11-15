import click
import json
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command('ps', short_help='Print the list of kamailio processes')
@pass_context
def cli(ctx):
    """Show details about running kamailio processes

    \b
    """
    command_ctl(ctx, 'core.psx', [], {"func": cmd_ps_result_print})


# callback to print the result of the rpc command
def cmd_ps_result_print(ctx, response, params=None):
    ctx.vlog("formatting the response for command ps")
    rdata = json.loads(response)
    if "result" in rdata:
        for r in rdata["result"]:
            ctx.printf("%4d %5d %s", r["IDX"], r["PID"], r["DSC"])
    else:
        print(json.dumps(rdata, indent=4, separators=(',', ': ')))
