import click
import hashlib
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from kamcli.cli import pass_context
from kamcli.cli import parse_user_spec


@click.group('subscriber', help='Manage the subscribers')
@pass_context
def cli(ctx):
    pass


@cli.command('add', short_help='Add a new subscriber')
@click.option('pwtext', '--text-password', '-t',
              type=click.Choice(['yes', 'no']),
              default='yes', help='Store password in clear text (default yes)')
@click.argument('userid', metavar='<userid>')
@click.argument('password', metavar='<password>')
@pass_context
def subscriber_add(ctx, pwtext, userid, password):
    """Add a new subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <password> - the password
    """
    udata = parse_user_spec(ctx, userid)
    ctx.vlog('Adding subscriber [%s] in domain [%s] with password [%s]',
             udata['username'], udata['domain'], password)
    dig = '{}:{}:{}'.format(udata['username'], udata['domain'], password)
    ha1 = hashlib.md5(dig.encode()).hexdigest()
    dig = '{}@{}:{}:{}'.format(
        udata['username'], udata['domain'], udata['domain'], password)
    ha1b = hashlib.md5(dig.encode()).hexdigest()
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    if pwtext == 'yes':
        e.execute(
            'insert into subscriber (username, domain, password, ha1, ha1b) '
            'values (%s, %s, %s, %s, %s)',
            udata['username'], udata['domain'], password, ha1, ha1b
        )
    else:
        e.execute(
            'insert into subscriber (username, domain, ha1, ha1b) values '
            '(%s, %s, %s, %s)',
            udata['username'], udata['domain'], ha1, ha1b
        )


@cli.command('rm', short_help='Remove an existing subscriber')
@click.argument('userid', metavar='<userid>')
@pass_context
def subscriber_rm(ctx, userid):
    """Remove an existing subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log('Removing subscriber [%s@%s]', udata['username'], udata['domain'])
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    e.execute('delete from subscriber where username=%s and domain=%s',
              udata['username'], udata['domain'])


@cli.command('passwd', short_help='Update the password for a subscriber')
@click.option(
    'pwtext', '--text-password', '-t',
    type=click.Choice(['yes', 'no']),
    default='yes',
    help='Store password in clear text (default yes)'
)
@click.argument('userid', metavar='<userid>')
@click.argument('password', metavar='<password>')
@pass_context
def subscriber_passwd(ctx, pwtext, userid, password):
    """Update password for a subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <password> - the password
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log('Updating subscriber [%s@%s] with password [%s]',
            udata['username'], udata['domain'], password)
    dig = '{}:{}:{}'.format(udata['username'], udata['domain'], password)
    ha1 = hashlib.md5(dig.encode()).hexdigest()
    dig = '{}@{}:{}:{}'.format(
        udata['username'], udata['domain'], udata['domain'], password)
    ha1b = hashlib.md5(dig.encode()).hexdigest()
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    if pwtext == 'yes':
        e.execute(
            'update subscriber set password=%s, ha1=%s, ha1b=%s where '
            'username=%s and domain=%s',
            password, ha1, ha1b, udata['username'], udata['domain']
        )
    else:
        e.execute(
            'update subscriber set ha1=%s, ha1b=%s where '
            'username=%s and domain=%s',
            ha1, ha1b, udata['username'], udata['domain']
        )


@cli.command('show', short_help='Show details for subscribers')
@click.option('oformat', '--output-format', '-F',
              type=click.Choice(['raw', 'json', 'table', 'dict']),
              default=None, help='Format the output')
@click.option('ostyle', '--output-style', '-S',
              default=None, help='Style of the output (tabulate table format)')
@click.argument('userid', nargs=-1, metavar='[<userid>]')
@pass_context
def subscriber_show(ctx, oformat, ostyle, userid):
    """Show details for subscribers

    \b
    Parameters:
        [<userid>] - username, AoR or SIP URI for subscriber
                   - it can be a list of userids
                   - if not provided then all subscribers are shown
    """
    if not userid:
        ctx.vlog('Showing all subscribers')
        e = create_engine(ctx.gconfig.get('db', 'rwurl'))
        res = e.execute('select * from subscriber')
        ioutils_dbres_print(ctx, oformat, ostyle, res)
    else:
        for u in userid:
            udata = parse_user_spec(ctx, u)
            ctx.vlog('Showing subscriber [%s@%s]',
                     udata['username'], udata['domain'])
            e = create_engine(ctx.gconfig.get('db', 'rwurl'))
            res = e.execute(
                'select * from subscriber where username=%s and domain=%s',
                udata['username'], udata['domain']
            )
            ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command('setattrs', short_help='Set a string attribute for a subscriber')
@click.argument('userid', metavar='<userid>')
@click.argument('attr', metavar='<attribute>')
@click.argument('val', metavar='<value>')
@pass_context
def subscriber_setattrs(ctx, userid, attr, val):
    """Set a string attribute a subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <attribute> - the name of the attribute (column name in
                      subscriber table)
        <value> - the value to be set for the attribute
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log('Updating subscriber [%s@%s] with str attribute [%s]=[%s]',
            udata['username'], udata['domain'], attr, val)
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    e.execute(
        'update subscriber set {0}={1!r} where username={2!r} and '
        'domain={3!r}'.format(
            attr.encode('ascii', 'ignore').decode(),
            val.encode('ascii', 'ignore').decode(),
            udata['username'], udata['domain']
        )
    )


@cli.command(
    'setattri', short_help='Set an integer attribute for a subscriber')
@click.argument('userid', metavar='<userid>')
@click.argument('attr', metavar='<attribute>')
@click.argument('val', metavar='<value>')
@pass_context
def subscriber_setattri(ctx, userid, attr, val):
    """Set an integer attribute a subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <attribute> - the name of the attribute (column name in
                      subscriber table)
        <value> - the value to be set for the attribute
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log('Updating subscriber [%s@%s] with int attribute [%s]=[%s]',
            udata['username'], udata['domain'], attr, val)
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    e.execute(
        'update subscriber set {0}={1} where username={2!r} and '
        'domain={3!r}'.format(
            attr.encode('ascii', 'ignore').decode(),
            val.encode('ascii', 'ignore').decode(),
            udata['username'], udata['domain']
        )
    )


@cli.command(
    'setattrnull', short_help='Set an attribute to NULL for a subscriber')
@click.argument('userid', metavar='<userid>')
@click.argument('attr', metavar='<attribute>')
@pass_context
def subscriber_setattrnull(ctx, userid, attr):
    """Set an attribute to NULL for a subscriber

    \b
    Parameters:
        <userid> - username, AoR or SIP URI for subscriber
        <attribute> - the name of the attribute (column name in
                      subscriber table)
    """
    udata = parse_user_spec(ctx, userid)
    ctx.log('Updating subscriber [%s@%s] with attribute [%s]=NULL',
            udata['username'], udata['domain'], attr)
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    e.execute(
        'update subscriber set {0}=NULL where username={1!r} and '
        'domain={2!r}'.format(
            attr.encode('ascii', 'ignore').decode(),
            udata['username'], udata['domain']
        )
    )
