import click
import json
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec
from kamcli.iorpc import command_ctl


##
#
#
@click.group('dialplan', help='Manage dialplan module (regexp translations)')
@pass_context
def cli(ctx):
    pass


##
#
#
@cli.command('add', short_help='Add a new dialplan rule')
@click.option('priority', '--priority', type=int, default=0,
            help='Priority value (default: 0)')
@click.option('matchop', '--match-op', default='equal',
            help='Match operator: equal, regexp, fnmatch (default: equal)')
@click.option('matchlen', '--match-len', type=int, default=0,
            help='Match target lenght (default: 0)')
@click.option('attrs', '--attrs', default='',
            help='Attributes (default: "")')
@click.argument('dpid', metavar='<dpid>', type=int)
@click.argument('matchexp', metavar='<matchexp>')
@click.argument('substrepl', nargs=-1, metavar='<substrepl>')
@pass_context
def dialplan_add(ctx, priority, matchop, matchlen, attrs, dpid, matchexp, substrepl):
    """Add a new translation rule in dialplan table

    \b
    Parameters:
        <dpid> - dialplan id
        <matchexp> - match expression
        [<substexp>] - substitution match expression
        [<replexp>] - replacement expression
    """
    matchid = 0
    if matchop == "regexp":
        matchid = 1;
    elif matchop == "fnmatch":
        matchid = 2;
    substexp = ""
    replexp = ""
    if len(substrepl) > 0:
        substexp = substrepl[0]
    if len(substrepl) > 1:
        replexp = substrepl[1]

    ctx.vlog('Adding to dialplan id [%d] match [%s] expression [%s]', dpid, matchop, matchexp)
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    e.execute('insert into dialplan (dpid, pr, match_op, match_exp, match_len, subst_exp, repl_exp, attrs) values ({0}, {1}, {2}, {3!r}, {4}, {5!r}, {6!r}, {7!r})'.format(dpid, priority, matchid, matchexp.encode('ascii','ignore').decode(), matchlen, substexp.encode('ascii','ignore').decode(), replexp.encode('ascii','ignore').decode(), attrs.encode('ascii','ignore').decode()))


##
#
#
@cli.command('rm', short_help='Remove records from dialplan')
@click.argument('dpid', metavar='<dpid>', type=int)
@click.argument('matchexp', nargs=-1, metavar='<match exp>')
@pass_context
def dialplan_rm(ctx, dpid, matchexp):
    """Remove records from dialplan

    \b
    Parameters:
        <dpid> - dialplan id
        [<matchexp>] - match expression
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    if not matchexp:
        e.execute('delete from dialplan where dpid={0}'.format(dpid))
    else:
        for m in matchexp:
            e.execute('delete from dialplan where dpid={0} and match_exp={1!r}'.format(dpid, m.encode('ascii','ignore').decode()))


##
#
#
@cli.command('showdb', short_help='Show dialplan records in database')
@click.option('oformat', '--output-format', '-F',
                type=click.Choice(['raw', 'json', 'table', 'dict']),
                default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
                default=None, help='Style of the output (tabulate table format)')
@click.argument('dpid', nargs=-1, metavar='[<dpid>]', type=int)
@pass_context
def dispatcher_showdb(ctx, oformat, ostyle, dpid):
    """Show details for records in dialplan

    \b
    Parameters:
        [<dpid>] - dialplan id
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    if not dpid:
        ctx.vlog('Showing all dialplan records')
        res = e.execute('select * from dialplan')
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for d in dpid:
            ctx.vlog('Showing dialplan records for set id: ' + d)
            res = e.execute('select * from dialplan where dpid=%d', d)
            ioutils_dbres_print(ctx, oformat, ostyle, res)


##
#
#
@cli.command('list', short_help='Show details for dialplan records in memory')
@click.argument('dpid', metavar='[<dpid>]', type=int)
@pass_context
def dispatcher_list(ctx, dpid):
    """Show details for dialplan records in memory

    \b
    Parameters:
        <dpid> - dialplan id
    """
    command_ctl(ctx, 'dialplan.dump', [ dpid ])


##
#
#
@cli.command('reload', short_help='Reload dialplan records from database into memory')
@pass_context
def dialplan_reload(ctx):
    """Reload dialplan records from database into memory
    """
    command_ctl(ctx, 'dialplan.reload', [ ])


##
#
#
@cli.command('translate', short_help='Translate using the rules from dialplan applied to input value')
@click.argument('dpid', metavar='<dpid>', type=int)
@click.argument('ivalue', metavar='<ivalue>')
@pass_context
def dispatcher_list(ctx, dpid, ivalue):
    """Translate using the rules from dialplan applied to input value

    \b
    Parameters:
        <dpid> - dialplan id
        <ivalue> - input value
    """
    command_ctl(ctx, 'dialplan.translate', [ dpid, ivalue ])


