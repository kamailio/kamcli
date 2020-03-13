import sys
import json

# import pprint

ioutils_tabulate_format = True
try:
    from tabulate import tabulate
except ImportError:
    ioutils_tabulate_format = False
    pass  # module doesn't exist, deal with it.


ioutils_formats_list = ["raw", "json", "table", "dict"]


def ioutils_dbres_print(ctx, oformat, ostyle, res):
    """ print a database result using different formats and styles """
    if oformat is None:
        if ctx.oformat is None:
            if ioutils_tabulate_format is True:
                oformat = "table"
            else:
                oformat = "json"
        else:
            oformat = ctx.oformat

    if oformat == "table":
        if ioutils_tabulate_format is False:
            ctx.log("Package tabulate is not installed")
            sys.exit()

    if ostyle is None:
        ostyle = "grid"

    if oformat == "json":
        for row in res:
            print(json.dumps(dict(row), indent=4))
            print()
    elif oformat == "dict":
        for row in res:
            print(dict(row))
            # pprint.pprint(dict(row), indent=4)
            print()
    elif oformat == "table":
        allrows = res.fetchall()
        gstring = tabulate(allrows, headers=res.keys(), tablefmt=ostyle)
        print(gstring)
    else:
        allrows = res.fetchall()
        print(allrows)
