import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError


KDB_IGNORE_MISSING = [
    "userblacklist",
    "userblocklist",
]


def dbutils_exec_sqlfile(ctx, sqlengine, fname):
    if not os.path.exists(fname):
        for i in KDB_IGNORE_MISSING:
            if i in fname:
                return
        ctx.log(
            "sql statements file not found [%s]",
            fname,
        )
        return
    sql_file = open(fname, "r")
    sql_command = ""
    for line in sql_file:
        if not line.startswith("--") and line.strip("\n"):
            sql_command += line.strip("\n")
            if sql_command.endswith(";"):
                try:
                    sqlengine.execute(text(sql_command))
                except SQLAlchemyError:
                    ctx.log(
                        "failed to execute sql statement [%s] from file [%s]",
                        sql_command,
                        fname,
                    )
                finally:
                    sql_command = ""


def dbutils_exec_sqltext(ctx, sqlengine, sqltext):
    sql_command = ""
    for line in sqltext.splitlines():
        tline = line.strip(" \t\r\n")
        if len(tline) > 0 and not tline.startswith("--"):
            sql_command += " " + tline
            if sql_command.endswith(";"):
                try:
                    sqlengine.execute(text(sql_command))
                except SQLAlchemyError:
                    ctx.log(
                        "failed to execute sql statements [%s]",
                        sql_command,
                    )
                finally:
                    sql_command = ""
