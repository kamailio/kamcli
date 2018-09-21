import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.iorpc import command_ctl


##
#
#
@click.group('tls', help='Manage tls module')
@pass_context
def cli(ctx):
    pass


##
#
#
@cli.command('showdb', short_help='Show TLS config records in database')
@click.option('oformat', '--output-format', '-F',
                type=click.Choice(['raw', 'json', 'table', 'dict']),
                default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
                default=None, help='Style of the output (tabulate table format)')
@pass_context
def tls_showdb(ctx, oformat, ostyle):
    """Show details for records in tlscfg table

    \b
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    ctx.vlog('Showing all tlscfg records')
    res = e.execute('select * from tlscfg')
    ioutils_dbres_print(ctx, oformat, ostyle, res)



##
#
#
@cli.command('cfgprint', short_help='Print TLS config generated from database records')
@click.argument('cfgpath', nargs=-1, metavar='[<cfgpath>]')
@pass_context
def tls_cfgprint(ctx, cfgpath):
    """Print TLS config generated from database records

    \b
        [<cfgpath>] - config file path (optional)
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    ctx.vlog('Generating TLS config from database records')
    res = e.execute('select * from tlscfg')
    pcount = 0
    for row in res:
        if pcount > 0:
            print("\n")

        if ( row["profile_type"] and row["profile_type"].strip()
                and row["profile_name"] and row["profile_name"].strip() ):
            print("[{0:s}:{1:s}]".format(row["profile_type"],row["profile_name"]))

            if row["method"] and row["method"].strip:
                print("method={0:s}".format(row["method"]))

            if row["certificate"] and row["certificate"].strip:
                print("certificate={0:s}".format(row["certificate"]))

            if row["private_key"] and row["private_key"].strip:
                print("private_key={0:s}".format(row["private_key"]))

        pcount += 1

##
#
#
@cli.command('list', short_help='Show details for TLS config in memory')
@pass_context
def tls_list(ctx):
    """Show details for TLS config records in memory

    \b
    """
    command_ctl(ctx, 'tls.options', [ ])


##
#
#
@cli.command('reload', short_help='Reload domain records from database into memory')
@pass_context
def domain_reload(ctx):
    """Reload domain records from database into memory

    \b
    """
    command_ctl(ctx, 'domain.reload', [ ])

