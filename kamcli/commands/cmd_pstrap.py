import click
import os
import subprocess
import json
import datetime
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


@click.command(
    "pstrap",
    help="Store runtime details and gdb full backtrace for all Kamailio processes to a file",
    short_help="Get runtime details and gdb backtrace with ps",
)
@click.option(
    "all",
    "--all",
    "-a",
    is_flag=True,
    help="Print all details in the trap file",
)
@click.option(
    "sysps",
    "--sys-ps",
    "-s",
    is_flag=True,
    help="Get the system ps line for each PID",
)
@pass_context
def cli(ctx, all, sysps):
    """Store runtime details and gdb full backtrace for all Kamailio processes to a file

    \b
    """
    ofile = (
        "/tmp/gdb_kamailio_"
        + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".txt"
    )
    ctx.printf("Trap file: " + ofile)
    os.system(
        'echo "--- ps output -----------------------------------------------------" >'
        + ofile
    )

    os.system(
        "ps auxw | grep kamailio | grep -v grep | grep -v kamcli | sort >>"
        + ofile
    )

    if all:
        os.system("echo >>" + ofile)
        os.system("kamailio -v >>" + ofile)
        os.system("echo >>" + ofile)
        os.system("kamailio -I >>" + ofile)

    ctx.printf("Trapping Kamailio processes with gdb. It can take a while.")

    child = subprocess.Popen(
        ["pgrep", "kamailio"], stdout=subprocess.PIPE, shell=False
    )
    response = child.communicate()[0]
    if len(response) > 0:
        for pid in response.split():
            ctx.printnlf(".")
            os.system("echo >>" + ofile)
            os.system(
                'echo "---start '
                + pid
                + ' -----------------------------------------------------" >>'
                + ofile
            )
            if sysps:
                os.system(
                    "ps -o pid,ni,pri,pcpu,stat,pmem,rss,vsz,args -w -p "
                    + str(pid)
                    + " >>"
                    + ofile
                )
            os.system(
                "gdb kamailio "
                + pid
                + ' -batch -batch --eval-command="p process_no" --eval-command="p pt[process_no]" --eval-command="bt full" >>'
                + ofile
                + " 2>&1"
            )
            os.system(
                'echo "---end '
                + pid
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
