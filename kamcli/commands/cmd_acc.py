import click
from sqlalchemy import create_engine
from kamcli.ioutils import ioutils_dbres_print
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from kamcli.cli import pass_context
from kamcli.dbutils import dbutils_exec_sqltext


@click.group(
    "acc", help="Accounting management", short_help="Accounting management"
)
@pass_context
def cli(ctx):
    pass


def acc_acc_struct_update_exec(ctx, e):
    sqltext = """
      ALTER TABLE acc ADD COLUMN src_user VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN src_domain VARCHAR(128) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN src_ip VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN dst_ouser VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN dst_user VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN dst_domain VARCHAR(128) NOT NULL DEFAULT '';
      ALTER TABLE acc ADD COLUMN cdr_id INTEGER NOT NULL DEFAULT 0;
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
      ALTER TABLE missed_calls ADD COLUMN src_ip VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE missed_calls ADD COLUMN dst_ouser VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE missed_calls ADD COLUMN dst_user VARCHAR(64) NOT NULL DEFAULT '';
      ALTER TABLE missed_calls ADD COLUMN dst_domain VARCHAR(128) NOT NULL DEFAULT '';
      ALTER TABLE missed_calls ADD COLUMN cdr_id INTEGER NOT NULL DEFAULT 0;
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


@cli.command(
    "cdrs-table-create",
    help="Run SQL statements to create cdrs table structure",
)
@pass_context
def acc_cdrs_table_create(ctx):
    """Run SQL statements to create cdrs table structure
    """
    ctx.vlog("Run SQL statements to create cdrs table structure")
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    sqltext = """
      CREATE TABLE `cdrs` (
      `cdr_id` bigint(20) NOT NULL auto_increment,
      `src_username` varchar(64) NOT NULL default '',
      `src_domain` varchar(128) NOT NULL default '',
      `dst_username` varchar(64) NOT NULL default '',
      `dst_domain` varchar(128) NOT NULL default '',
      `dst_ousername` varchar(64) NOT NULL default '',
      `call_start_time` datetime NOT NULL default '2000-01-01 00:00:00',
      `duration` int(10) unsigned NOT NULL default '0',
      `sip_call_id` varchar(128) NOT NULL default '',
      `sip_from_tag` varchar(128) NOT NULL default '',
      `sip_to_tag` varchar(128) NOT NULL default '',
      `src_ip` varchar(64) NOT NULL default '',
      `cost` integer NOT NULL default '0',
      `rated` integer NOT NULL default '0',
      `created` datetime NOT NULL,
      PRIMARY KEY  (`cdr_id`),
      UNIQUE KEY `uk_cft` (`sip_call_id`,`sip_from_tag`,`sip_to_tag`)
      );
    """
    e.execute(sqltext)


@cli.command(
    "cdrs-proc-create",
    help="Run SQL statements to create the stored procedure to generate cdrs",
)
@pass_context
def acc_cdrs_proc_create(ctx):
    """Run SQL statements to create the stored procedure to generate cdrs
    """
    ctx.vlog(
        "Run SQL statements to create the stored procedure to generate cdrs"
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    sqltext = """
      CREATE PROCEDURE `kamailio_cdrs`()
      BEGIN
        DECLARE done INT DEFAULT 0;
        DECLARE bye_record INT DEFAULT 0;
        DECLARE v_src_user,v_src_domain,v_dst_user,v_dst_domain,v_dst_ouser,v_callid,
           v_from_tag,v_to_tag,v_src_ip VARCHAR(64);
        DECLARE v_inv_time, v_bye_time DATETIME;
        DECLARE inv_cursor CURSOR FOR SELECT src_user, src_domain, dst_user,
           dst_domain, dst_ouser, time, callid,from_tag, to_tag, src_ip
           FROM acc
           where method='INVITE' and cdr_id='0';
        DECLARE CONTINUE HANDLER FOR SQLSTATE '02000' SET done = 1;
        OPEN inv_cursor;
        REPEAT
          FETCH inv_cursor INTO v_src_user, v_src_domain, v_dst_user, v_dst_domain,
                  v_dst_ouser, v_inv_time, v_callid, v_from_tag, v_to_tag, v_src_ip;
          IF NOT done THEN
            SET bye_record = 0;
            SELECT 1, time INTO bye_record, v_bye_time FROM acc WHERE
                 method='BYE' AND callid=v_callid AND ((from_tag=v_from_tag
                 AND to_tag=v_to_tag)
                 OR (from_tag=v_to_tag AND to_tag=v_from_tag))
                 ORDER BY time ASC LIMIT 1;
            IF bye_record = 1 THEN
              INSERT INTO cdrs (src_username,src_domain,dst_username,
                 dst_domain,dst_ousername,call_start_time,duration,sip_call_id,
                 sip_from_tag,sip_to_tag,src_ip,created) VALUES (v_src_user,
                 v_src_domain,v_dst_user,v_dst_domain,v_dst_ouser,v_inv_time,
                 UNIX_TIMESTAMP(v_bye_time)-UNIX_TIMESTAMP(v_inv_time),
                 v_callid,v_from_tag,v_to_tag,v_src_ip,NOW());
              UPDATE acc SET cdr_id=last_insert_id() WHERE callid=v_callid
                 AND from_tag=v_from_tag AND to_tag=v_to_tag;
            END IF;
            SET done = 0;
          END IF;
        UNTIL done END REPEAT;
      END
    """
    e.execute(sqltext)


@cli.command(
    "rating-table-create",
    help="Run SQL statements to create billing_rates table structure",
)
@pass_context
def acc_rating_table_create(ctx):
    """Run SQL statements to create billing_rates table structure
    """
    ctx.vlog("Run SQL statements to create billing_rates table structure")
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    sqltext = """
      CREATE TABLE `billing_rates` (
      `rate_id` bigint(20) NOT NULL auto_increment,
      `rate_group` varchar(64) NOT NULL default 'default',
      `prefix` varchar(64) NOT NULL default '',
      `rate_unit` integer NOT NULL default '0',
      `time_unit` integer NOT NULL default '60',
      PRIMARY KEY  (`rate_id`),
      UNIQUE KEY `uk_rp` (`rate_group`,`prefix`)
      );
    """
    e.execute(sqltext)


@cli.command(
    "list", short_help="List accounting records",
)
@click.option(
    "oformat",
    "--output-format",
    "-F",
    type=click.Choice(["raw", "json", "table", "dict"]),
    default=None,
    help="Format the output",
)
@click.option(
    "ostyle",
    "--output-style",
    "-S",
    default=None,
    help="Style of the output (tabulate table format)",
)
@click.option(
    "limit",
    "--limit",
    "-l",
    type=int,
    default=20,
    help="The limit of listed records (default: 20)",
)
@pass_context
def acc_list(ctx, oformat, ostyle, limit):
    """List accounting records

    \b
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    ctx.vlog("Showing accounting records")
    res = e.execute(
        "select * from acc order by id desc limit {0}".format(limit)
    )
    ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command(
    "cdrs-generate",
    help="Run SQL stored procedure to generate CDRS",
)
@pass_context
def acc_cdrs_generate(ctx):
    """Run SQL stored procedure to generate CDRS
    """
    ctx.vlog("Run SQL stored procedure to generate CDRS")
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    e.execute("call kamailio_cdrs()")


@cli.command(
    "cdrs-list", short_help="List call data records",
)
@click.option(
    "oformat",
    "--output-format",
    "-F",
    type=click.Choice(["raw", "json", "table", "dict"]),
    default=None,
    help="Format the output",
)
@click.option(
    "ostyle",
    "--output-style",
    "-S",
    default=None,
    help="Style of the output (tabulate table format)",
)
@click.option(
    "limit",
    "--limit",
    "-l",
    type=int,
    default=20,
    help="The limit of listed records (default: 20)",
)
@pass_context
def acc_cdrs_list(ctx, oformat, ostyle, limit):
    """List call data records

    \b
    """
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    ctx.vlog("Showing call data records")
    res = e.execute(
        "select * from cdrs order by cdr_id desc limit {0}".format(limit)
    )
    ioutils_dbres_print(ctx, oformat, ostyle, res)


@cli.command("rates-add", short_help="Add a new rating record to database")
@click.option(
    "dbtname",
    "--dbtname",
    default="",
    help='The name of the database table (default: "billing_rates")',
)

@click.argument("rate_group", metavar="<rate_group>")
@click.argument("prefix", metavar="<prefix>")
@click.argument("rate_unit", metavar="<rate_unit>")
@click.argument("time_unit", metavar="<time_unit>")
@pass_context
def acc_rates_add(ctx, dbtname, rate_group, prefix, rate_unit, time_unit):
    """Add a new rating record in database table

    \b
    Parameters:
        <rate_group> - name of rating group
        <prefix> - matching prefix
        <rate_unit>  - rate unit
        <time_unit>  - time unit
    """
    ctx.vlog(
        "Adding to db table [%s] record [%s] => [%s]", dbtname, rate_group, prefix
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    v_dbtname = dbtname.encode("ascii", "ignore").decode()
    v_rate_group = rate_group.encode("ascii", "ignore").decode()
    v_prefix = prefix.encode("ascii", "ignore").decode()
    e.execute(
        "insert into {0} (rate_group, prefix, rate_unit, time_unit) values "
        "({1!r}, {2!r}, {3}, {4})".format(
            v_dbtname,
            v_rate_group,
            v_prefix,
            rate_unit,
            time_unit
        )
    )


@cli.command("rates-rm", short_help="Remove a rating record from database")
@click.option(
    "dbtname",
    "--dbtname",
    default="",
    help='The name of the database table (default: "billing_rates")',
)

@click.argument("rate_group", metavar="<rate_group>")
@click.argument("prefix", metavar="<prefix>")
@pass_context
def acc_rates_rm(ctx, dbtname, rate_group, prefix):
    """Remove a rating record from database

    \b
    Parameters:
        <rate_group> - name of rating group
        <prefix> - matching prefix
    """
    ctx.vlog(
        "Remove from db table [%s] record [%s] => [%s]", dbtname, rate_group, prefix
    )
    e = create_engine(ctx.gconfig.get("db", "rwurl"))
    v_dbtname = dbtname.encode("ascii", "ignore").decode()
    v_rate_group = rate_group.encode("ascii", "ignore").decode()
    v_prefix = prefix.encode("ascii", "ignore").decode()
    e.execute(
        "delete from {0} where rate_group=({1!r} and prefix={2!r}".format(
            v_dbtname,
            v_rate_group,
            v_prefix,
        )
    )
