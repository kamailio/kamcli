import os
import sys
import click
import shutil
from kamcli.cli import pass_context
from kamcli.cli import COMMAND_ALIASES


@click.group(
    "config",
    help="Manage the config file",
    short_help="Manage the config file",
)
@pass_context
def cli(ctx):
    pass


@cli.command("raw", short_help="Display raw content of configuration file")
@pass_context
def config_raw(ctx):
    """Show content of configuration file for kamcli"""
    ctx.log("\n---")
    ctx.gconfig.write(sys.stdout)
    ctx.log("\n---")


@cli.command(
    "show", short_help="Show expanded content of configuration file sections"
)
@click.argument("sections", nargs=-1, metavar="<sections>")
@pass_context
def config_show(ctx, sections):
    """Show expanded content of configuration file section"""
    if sections:
        ctx.log("\n---")
    for s in sections:
        ctx.log("[%s]", s)
        for k, v in ctx.gconfig.items(s):
            ctx.log("%s= %s", k, v)
        ctx.log("\n---")


@cli.command("paths", short_help="Show the paths of configuration files")
@pass_context
def config_paths(ctx):
    """Show the paths of configuration files for kamcli"""
    print()
    print(ctx.gconfig_paths)
    print()


@cli.command("cmdaliases", short_help="Show the command aliases")
@pass_context
def config_cmdaliases(ctx):
    """Show the command aliases"""
    print()
    print(COMMAND_ALIASES)
    print()


@cli.command("install", short_help="Install the config file")
@click.option(
    "user", "--user", "-u", is_flag=True, help="Install in user home folder",
)
@pass_context
def config_install(ctx, user):
    if os.path.isfile("./kamcli/kamcli.ini"):
        if user:
            dirName = os.path.expanduser("~/.kamcli")
        else:
            dirName = "/etc/kamcli"
        if not os.path.exists(dirName):
            os.mkdir(dirName)
            click.echo("directory " + dirName + " created")
        else:
            click.echo("directory " + dirName + " already exists")
        shutil.copyfile("./kamcli/kamcli.ini", dirName + "/kamcli.ini")
        click.echo("config file installed to " + dirName + "/kamcli.ini")
    else:
        click.echo("command must be run in the source code root directory")
