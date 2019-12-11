import click
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from kamcli.cli import pass_context
from kamcli.dbutils import dbutils_exec_sqltext


@click.group("acc", help="Accounting management")
@pass_context
def cli(ctx):
    pass


def acc_acc_struct_update_exec(ctx, e):
    sqltext = """
      ALTER TABLE acc ADD COLUMN src_user VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN src_domain VARCHAR(128) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN src_ip varchar(64) NOT NULL default '';
      ALTER TABLE acc ADD COLUMN dst_ouser VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN dst_user VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN dst_domain VARCHAR(128) NOT NULL DEFAULT '';
    """
    dbutils_exec_sqltext(ctx, e, sqltext)


@cli.command(
    "acc-struct-update",
    help="Run SQL statements to update acc table structure",
)
@pass_context
def acc_acc_struct_update(ctx):
    """Run SQL statements to update acc table structure
    """
    ctx.vlog("Run statements to update acc table structure")
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    acc_acc_struct_update_exec(ctx, e)


def acc_mc_struct_update_exec(ctx, e):
    sqltext = """
      ALTER TABLE missed_calls ADD COLUMN src_user VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE missed_calls ADD COLUMN src_domain VARCHAR(128) NOT NULL DEFAULT '';
      ALTER TABLE missed_calls ADD COLUMN src_ip varchar(64) NOT NULL default '';
      ALTER TABLE missed_calls ADD COLUMN dst_ouser VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE missed_calls ADD COLUMN dst_user VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE missed_calls ADD COLUMN dst_domain VARCHAR(128) NOT NULL DEFAULT '';
    """
    dbutils_exec_sqltext(ctx, e, sqltext)


@cli.command(
    "mc-struct-update",
    help="Run SQL statements to update missed_calls table structure",
)
@pass_context
def acc_mc_struct_update(ctx):
    """Run SQL statements to update missed_calls table structure
    """
    ctx.vlog("Run statements to update missed_calls table structure")
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    acc_mc_struct_update_exec(ctx, e)


@cli.command(
    "tables-struct-update",
    help="Run SQL statements to update acc and missed_calls tables structures",
)
@pass_context
def acc_tables_struct_update(ctx):
    """Run SQL statements to update acc and missed_calls tables structures
    """
    ctx.vlog("Run statements to update acc and missed_calls tables structures")
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    acc_acc_struct_update_exec(ctx, e)
    acc_mc_struct_update_exec(ctx, e)
