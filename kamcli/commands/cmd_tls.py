import sys
import os
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
@click.option('odir', '--odir', '-d',
                default=None, help='Output directory path for certificates content')
@click.argument('cfgpath', nargs=-1, metavar='[<cfgpath>]', type=click.Path())
@pass_context
def tls_cfgprint(ctx, odir, cfgpath):
    """Print TLS config generated from database records

    \b
        [<cfgpath>] - config file path (optional)
    """
    e = create_engine(ctx.gconfig.get('db', 'rwurl'))
    ctx.vlog('Generating TLS config from database records')
    res = e.execute('select * from tlscfg')

    if cfgpath:
        cfgpath = cfgpath[0]

    if not odir:
        if cfgpath:
            odir = os.path.dirname(str(cfgpath))

    bstdout = sys.stdout
    if cfgpath:
        cfgsock = open(str(cfgpath), 'w')
        sys.stdout = cfgsock

    pcount = 0
    for row in res:
        if pcount > 0:
            print("\n")

        if ( row["profile_type"] and row["profile_type"].strip()
                and row["profile_name"] and row["profile_name"].strip() ):
            print("[{0:s}:{1:s}]".format(row["profile_type"],row["profile_name"]))

            if row["method"] and row["method"].strip():
                print("method={0:s}".format(row["method"]))

            print("verify_certificate={0:d}".format(row["verify_certificate"]))
            print("verify_depth={0:d}".format(row["verify_depth"]))
            print("require_certificate={0:d}".format(row["require_certificate"]))

            if row["file_type"] == 0:
                if row["certificate"] and row["certificate"].strip():
                    print("certificate={0:s}".format(row["certificate"]))

                if row["private_key"] and row["private_key"].strip():
                    print("private_key={0:s}".format(row["private_key"]))

                if row["ca_list"] and row["ca_list"].strip():
                    print("ca_list={0:s}".format(row["ca_list"]))

                if row["crl"] and row["crl"].strip():
                    print("crl={0:s}".format(row["crl"]))
            else:
                if row["certificate"] and row["certificate"].strip():
                    fpath = os.path.join(odir, "certificate_"+str(row["id"])+".pem")
                    fout = open(fpath, 'w')
                    fout.write(row["certificate"])
                    fout.close()
                    print("certificate={0:s}".format(fpath))

                if row["private_key"] and row["private_key"].strip():
                    fpath = os.path.join(odir, "private_key_"+str(row["id"])+".pem")
                    fout = open(fpath, 'w')
                    fout.write(row["private_key"])
                    fout.close()
                    print("private_key={0:s}".format(fpath))

                if row["ca_list"] and row["ca_list"].strip():
                    fpath = os.path.join(odir, "ca_list_"+str(row["id"])+".pem")
                    fout = open(fpath, 'w')
                    fout.write(row["ca_list"])
                    fout.close()
                    print("ca_list={0:s}".format(fpath))

                if row["crl"] and row["crl"].strip():
                    fpath = os.path.join(odir, "crl_"+str(row["id"])+".pem")
                    fout = open(fpath, 'w')
                    fout.write(row["crl"])
                    fout.close()
                    print("crl={0:s}".format(fpath))

            if row["cipher_list"] and row["cipher_list"].strip():
                print("cipher_list={0:s}".format(row["cipher_list"]))

            if row["server_name"] and row["server_name"].strip():
                print("server_name={0:s}".format(row["server_name"]))
                print("server_name_mode={0:d}".format(row["server_name_mode"]))

            if row["server_id"] and row["server_id"].strip():
                print("server_id={0:s}".format(row["server_id"]))

        pcount += 1

    if cfgpath:
        sys.stdout = bstdout
        cfgsock.close()
        print("done")



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
@cli.command('reload', short_help='Reload tls configuration file')
@pass_context
def tls_reload(ctx):
    """Reload tls configuration file

    \b
    """
    command_ctl(ctx, 'tls.reload', [ ])



##
#
#
@cli.command('sqlprint', short_help='Print SQL statement to create the db table')
@pass_context
def tls_sqlprint(ctx):
    """Print SQL statement to create the db table

    \b
    """
    sqls = '''
CREATE TABLE `tlscfg` (
    `id` INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL,
    `profile_type` VARCHAR(64) NOT NULL,
    `profile_name` VARCHAR(128) NOT NULL,
    `method` VARCHAR(128),
    `verify_certificate` INT DEFAULT 0 NOT NULL,
    `verify_depth` INT DEFAULT 9 NOT NULL,
    `require_certificate` INT DEFAULT 0 NOT NULL,
    `cipher_list` VARCHAR(256),
    `server_name` VARCHAR(128),
    `server_name_mode` INT DEFAULT 0 NOT NULL,
    `server_id` VARCHAR(128),
    `file_type` INT DEFAULT 0 NOT NULL,
    `certificate` TEXT,
    `private_key` TEXT,
    `ca_list` TEXT,
    `crl` TEXT
);
'''
    print(sqls)
