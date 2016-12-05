import os
import time
import click
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
    if norefresh is True:
        command_ctl(ctx, 'stats.get_statistics', [ "tm:", "sl:", "usrloc:" ])
    else:
        while True:
            count = count + 1
            command_ctl(ctx, 'stats.get_statistics', [ "tmx:", "sl:", "usrloc:" ])
            print "[cycle #: " + str(count) + "; if constant make sure server is running]"
            time.sleep(2)
            clear()

