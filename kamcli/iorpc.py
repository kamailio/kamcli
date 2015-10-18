import os
import sys
import stat
import time
import threading
import json
from random import randint

iorpc_yaml_format = True
try:
    import yaml
except ImportError, e:
    iorpc_yaml_format = False
    pass # module doesn't exist, deal with it.


COMMAND_NAMES = {
    "dispatcher.list": {
        "mi": "ds_list",
        "rpc": "dispatcher.list",
    },
    "dispatcher.reload": {
        "mi": "ds_reload",
        "rpc": "dispatcher.reload",
    },
    "permissions.addressDump": {
        "mi": "address_dump",
        "rpc": "permissions.addressDump",
    },
    "permissions.addressReload": {
        "mi": "address_reload",
        "rpc": "permissions.addressReload",
    },
    "permissions.domainDump": {
        "mi": "perm_domain_dump",
        "rpc": "permissions.domainDump",
    },
    "permissions.subnetDump": {
        "mi": "subnet_dump",
        "rpc": "permissions.subnetDump",
    },
    "stats.clear_statistics": {
        "mi": "clear_statistics",
        "rpc": "stats.clear_statistics",
    },
    "stats.get_statistics": {
        "mi": "get_statistics",
        "rpc": "stats.get_statistics",
    },
    "stats.reset_statistics": {
        "mi": "reset_statistics",
        "rpc": "stats.reset_statistics",
    },
    "ul.add": {
        "mi": "ul_add",
        "rpc": "ul.add",
    },
    "ul.dump": {
        "mi": "ul_dump",
        "rpc": "ul.dump",
    },
    "ul.rm": {
        "mi": "ul_rm",
        "rpc": "ul.rm",
    },
    "ul.lookup": {
        "mi": "ul_show_contact",
        "rpc": "ul.lookup",
    }
}

# Thread to listen on a reply fifo file
#
class IOFifoThread (threading.Thread):
    def __init__(self, rplpath, oformat):
        threading.Thread.__init__(self)
        self.rplpath = rplpath
        self.oformat = oformat
        self.stop_signal = False

    def run(self):
        print "Starting to wait for reply on: " + self.rplpath
        r = os.open( self.rplpath, os.O_RDONLY|os.O_NONBLOCK )
        scount = 0
        rcount = 0
        wcount = 0
        rdata = ""
        while not self.stop_signal:
            rbuf = os.read(r, 4096)
            if rbuf == "":
                if rcount != 0 :
                    wcount += 1
                    if wcount == 8:
                        break
                    time.sleep(0.100)
                else:
                    scount += 1
                    if scount == 50:
                        break
                    time.sleep(0.100)
            else:
                rcount += 1
                wcount = 0
                rdata += rbuf

        if rcount==0 :
            print "timeout - nothing read"
        else:
            print
            if self.oformat == "json":
                print json.dumps(json.loads(rdata), indent=4, separators=(',', ': '))
            elif self.oformat == "yaml":
                if iorpc_yaml_format is True:
                    print yaml.safe_dump(json.loads(rdata), default_flow_style=False)
                else:
                    print json.dumps(json.loads(rdata), indent=4, separators=(',', ': '))
            else:
                print rdata

# :command:reply_fifo
# p1
# p2
# p3
# _empty_line_
#
def command_mi_fifo(ctx, dryrun, sndpath, rcvname, oformat, cmd, params):
    scmd = ":" + cmd + ":" + rcvname + "\n"
    for p in params:
        if type(p) is int:
            scmd += str(p) + "\n"
        elif type(p) is float:
            scmd += str(p) + "\n"
        else:
            if p == '':
                scmd += ".\n"
            else:
                scmd += p + "\n"
    scmd += "\n"
    if dryrun:
        print
        print scmd
        return

    rcvpath = ctx.gconfig.get('mi', 'rpldir') + "/" + rcvname
    if os.path.exists(rcvpath):
        if stat.S_ISFIFO(os.stat(rcvpath).st_mode):
            os.unlink(rcvpath)
        else:
            print "File with same name as reply fifo exists"
            sys.exit()

    os.mkfifo(rcvpath, 0666)
    os.chmod(rcvpath, 0666)
    # create new thread to read from reply firo
    tiofifo = IOFifoThread(rcvpath, oformat)
    # start new threadd
    tiofifo.start()

    w = os.open(sndpath, os.O_WRONLY)
    os.write(w, scmd)

    waitrun = True
    while waitrun:
        try:
            tiofifo.join(500)
            if not tiofifo.isAlive():
                waitrun = False
                break
        except KeyboardInterrupt:
            print "Ctrl-c received! Sending kill to threads..."
            tiofifo.stop_signal = True

    os.unlink(rcvpath)


#{
# "jsonrpc": "2.0",
#  "method": "command",
#  "params": [p1, p2, p3],
#  "reply_name": "kamailio_jsonrpc_reply_fifo",
#  "id": 1
#}
#
def command_jsonrpc_fifo(ctx, dryrun, sndpath, rcvname, oformat, cmd, params):
    scmd = '{\n  "jsonrpc": "2.0",\n  "method": "' + cmd + '",\n'
    if params:
        scmd += '  "params": ['
        comma = 0
        for p in params:
            if comma == 1:
                scmd += ',\n'
            else:
                comma = 1
            if type(p) is int:
                scmd += str(p)
            elif type(p) is float:
                scmd += str(p)
            else:
                if p.startswith("i:") :
                    scmd += p[2:]
                elif p.startswith("s:") :
                    scmd += '"' + p[2:] + '"'
                else :
                    scmd += '"' + p + '"'
        scmd += '],\n'

    scmd += '  "reply_name": "' + rcvname + '",\n'
    scmd += '  "id": ' + str(randint(2,10000)) + '\n'
    scmd += "}\n"
    if dryrun:
        print json.dumps(json.loads(scmd), indent=4, separators=(',', ': '))
        return

    rcvpath = ctx.gconfig.get('jsonrpc', 'rpldir') + "/" + rcvname
    if os.path.exists(rcvpath):
        if stat.S_ISFIFO(os.stat(rcvpath).st_mode):
            os.unlink(rcvpath)
        else:
            print "File with same name as reply fifo exists"
            sys.exit()

    os.mkfifo(rcvpath, 0666)
    os.chmod(rcvpath, 0666)
    # create new thread to read from reply firo
    tiofifo = IOFifoThread(rcvpath, oformat)
    # start new threadd
    tiofifo.start()

    w = os.open(sndpath, os.O_WRONLY)
    os.write(w, scmd)

    waitrun = True
    while waitrun:
        try:
            tiofifo.join(500)
            if not tiofifo.isAlive():
                waitrun = False
                break
        except KeyboardInterrupt:
            print "Ctrl-c received! Sending kill to threads..."
            tiofifo.stop_signal = True

    os.unlink(rcvpath)


##
#
#
def command_ctl(ctx, cmd, params):
    if ctx.gconfig.get('ctl', 'type') == 'jsonrpc':
        command_jsonrpc_fifo(ctx, False, ctx.gconfig.get('jsonrpc', 'path'),
                ctx.gconfig.get('jsonrpc', 'rplnamebase'), ctx.gconfig.get('jsonrpc', 'outformat'),
                COMMAND_NAMES[cmd]['rpc'], params)
    else:
        command_mi_fifo(ctx, False, ctx.gconfig.get('mi', 'path'),
                ctx.gconfig.get('mi', 'rplnamebase'), "raw", COMMAND_NAMES[cmd]['mi'], params)

