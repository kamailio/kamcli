import os
import time
import click
import json
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


##
#
#
@click.command('moni', short_help='Monitor relevant statistics')
@click.option('norefresh', '--no-refresh', is_flag=True,
            help='Do not refresh (execute once)')

@pass_context
def cli(ctx, norefresh):
    """Monitor relevant statistics on display

    \b
    Parameters:
        - --no-refresh - execute once
    Monitored statistics:
        tm, sl and usrloc
    """

    clear = lambda : os.system('tput reset')
    count = 0
    slist = [ "rcv_requests", "fwd_requests", "rcv_replies", "fwd_replies",
            "free_size", "sent_replies", "tmx:", "usrloc:" ]
    if norefresh is True:
        command_ctl(ctx, 'stats.get_statistics', slist, {"func": cmd_moni_result_print})
    else:
        while True:
            count = count + 1
            command_ctl(ctx, 'stats.get_statistics', slist, {"func": cmd_moni_result_print})
            print
            print "[cycle #: " + str(count) + "; if constant make sure server is running]"
            time.sleep(2)
            clear()


##
#
#
def cmd_moni_result_print(ctx, response, params=None):
    ctx.vlog("formatting the response for command ps")
    print
    rdata = json.loads(response)
    if "result" in rdata:
        rd = rdata["result"]
        for a,b in zip(rd[::2],rd[1::2]):
            print '{:<40}{:<}'.format(a,b)
    else:
        print json.dumps(rdata, indent=4, separators=(',', ': '))
