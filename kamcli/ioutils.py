import sys
import json

# import pprint

ioutils_tabulate_format = True
try:
    from tabulate import tabulate
except ImportError:
    ioutils_tabulate_format = False
    pass  # module doesn't exist, deal with it.

##
# enable yaml output format if the lib can be loaded
ioutils_yaml_format = True
try:
    import yaml
except ImportError:
    ioutils_yaml_format = False
    pass  # yaml module doesn't exist, deal with it.


ioutils_formats_list = ["raw", "json", "table", "dict", "yaml"]


def ioutils_dbres_print(ctx, oformat, ostyle, res):
    """ print a database result using different formats and styles """
    if oformat is None:
        oformat = ctx.gconfig.get("db", "outformat")
        if oformat is None:
            if ioutils_tabulate_format is True:
                oformat = "table"
            else:
                oformat = "json"

    if oformat == "table":
        if ioutils_tabulate_format is False:
            ctx.log("Package tabulate is not installed")
            sys.exit()

    if oformat == "yaml":
        if ioutils_yaml_format is False:
            ctx.log("Package yaml is not installed")
            sys.exit()

    if ostyle is None:
        ostyle = ctx.gconfig.get("db", "outstyle")
        if ostyle is None:
            ostyle = "grid"

    if oformat == "json":
        jdata = []
        for row in res:
            jdata.append(dict(row))
        print(json.dumps(jdata, indent=4))
        print()
    elif oformat == "yaml":
        ydata = []
        for row in res:
            ydata.append(dict(row))
        print(yaml.dump(ydata, indent=4))
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
