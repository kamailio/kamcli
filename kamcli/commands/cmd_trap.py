import click
import os
import json
import datetime
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command(
    "trap",
    short_help="Store runtime details and gdb full backtrace for all Kamailio processes to a file",
)
@pass_context
def cli(ctx):
    """Store runtime details and gdb full backtrace for all Kamailio processes to a file

    \b
    """
    ofile = (
        "/tmp/gdb_kamailio_"
        + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".txt"
    )
    command_ctl(
        ctx,
        "core.psx",
        [],
        {"func": cmd_trap_print, "params": {"ofile": ofile}},
    )


# callback to write backtraces to file using the result of an rpc command
def cmd_trap_print(ctx, response, params=None):
    ofile = None
    if params is not None:
        if "ofile" in params:
            ofile = params["ofile"]
    if ofile is None:
        ofile = (
            "/tmp/gdb_kamailio_"
            + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".txt"
        )
    ctx.printf("Trap file: " + ofile)
    with open(ofile, "a") as outfile:
        outfile.write(
            "---start core.psx -------------------------------------------------------\n"
        )
        outfile.write(response.decode())
        outfile.write(
            "\n---end core.psx -------------------------------------------------------\n\n"
        )
    rdata = json.loads(response)
    if "result" in rdata:
        ctx.printf(
            "Trapping "
            + str(len(rdata["result"]))
            + " Kamailio processes with gdb. It can take a while."
        )
        for r in rdata["result"]:
            ctx.printnlf(".")
            os.system("echo >>" + ofile)
            os.system(
                'echo "---start '
                + str(r["PID"])
                + ' -----------------------------------------------------" >>'
                + ofile
            )
            os.system(
                "gdb kamailio "
                + str(r["PID"])
                + ' -batch --eval-command="bt full" >>'
                + ofile
                + " 2>&1"
            )
            os.system(
                'echo "---end '
                + str(r["PID"])
                + ' -------------------------------------------------------" >>'
                + ofile
            )
    else:
        os.system("echo >>" + ofile)
        os.system(
            'echo "Unable to get the list with PIDs of running Kamailio processes" >>'
            + ofile
        )
    ctx.printf("")
