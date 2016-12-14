import os
import os.path
import sys
import socket
import stat
import time
import threading
import json
from random import randint

##
# enable yaml output format if the lib can be loaded
iorpc_yaml_format = True
try:
    import yaml
except ImportError, e:
    iorpc_yaml_format = False
    pass # yaml module doesn't exist, deal with it.


##
# RPC/MI commands aliases
#
# "alias" : {
#    "mi": "mi command",
#    "rpc": "rpc command",
# }
#
# - alias is used inside Python function
# - command_ctl(...) will use mi or rpc variant
#   based on config options
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


##
#
def command_ctl_name(alias, ctype):
    """Return the rpc command name by alias lookup"""
    v = COMMAND_NAMES.get(alias, None)
    if v == None:
        return alias

    if ctype == "mi":
        return COMMAND_NAMES[alias]['mi'];
    else:
        return COMMAND_NAMES[alias]['rpc']


##
#
def command_ctl_response_print(response, oformat):
    """Print the rpc control command response

    \b
    Parameters:
      - response: the jsonrpc response
      - oformat: output format:
        * json: json pretty formating
        * yaml: yaml pretty formating (list like, more compact)
        * raw output - just print the response
    """
    print
    if oformat == "json":
        print json.dumps(json.loads(response), indent=4, separators=(',', ': '))
    elif oformat == "yaml":
        if iorpc_yaml_format is True:
            print yaml.safe_dump(json.loads(response), default_flow_style=False)
        else:
            print json.dumps(json.loads(response), indent=4, separators=(',', ': '))
    else:
        print response


##
#
def command_ctl_response(ctx, response, oformat, cbexec={}):
    """Process a rpc control command response"""
    if not cbexec:
        command_ctl_response_print(response, oformat)
    else:
        if "func" in cbexec:
            if "params" in cbexec:
                cbexec["func"](ctx, response, cbexec["params"])
            else:
                cbexec["func"](ctx, response)
        else:
            ctx.log("invalid callback structure - function is missing")


##
# Thread to listen on a reply fifo file
class IOFifoThread (threading.Thread):
    def __init__(self, ctx, rplpath, oformat, cbexec={}):
        threading.Thread.__init__(self)
        self.ctx = ctx
        self.rplpath = rplpath
        self.oformat = oformat
        self.cbexec = cbexec
        self.stop_signal = False

    def run(self):
        self.ctx.vlog("Starting to wait for reply on: " + self.rplpath)
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
            self.ctx.vlog("timeout - nothing read")
        else:
            command_ctl_response(self.ctx, rdata, self.oformat, self.cbexec)


##
# :command:reply_fifo
# p1
# p2
# p3
# _empty_line_
def command_mi_fifo(ctx, dryrun, sndpath, rcvname, oformat, cmd, params=[], cbexec={}):
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
            ctx.log("File with same name as reply fifo exists")
            sys.exit()

    os.mkfifo(rcvpath, 0666)
    os.chmod(rcvpath, 0666)
    # create new thread to read from reply fifo
    tiofifo = IOFifoThread(ctx, rcvpath, oformat)
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
            ctx.log("Ctrl-c received! Sending kill to threads...")
            tiofifo.stop_signal = True

    os.unlink(rcvpath)


##
#{
# "jsonrpc": "2.0",
#  "method": "command",
#  "params": [p1, p2, p3],
#  "reply_name": "kamailio_jsonrpc_reply_fifo",
#  "id": 1
#}
#
def command_jsonrpc_fifo(ctx, dryrun, sndpath, rcvname, oformat, cmd, params=[], cbexec={}):
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
            ctx.log("File with same name as reply fifo exists")
            sys.exit()

    os.mkfifo(rcvpath, 0666)
    os.chmod(rcvpath, 0666)
    # create new thread to read from reply fifo
    tiofifo = IOFifoThread(ctx, rcvpath, oformat)
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
            ctx.log("Ctrl-c received! Sending kill to threads...")
            tiofifo.stop_signal = True

    os.unlink(rcvpath)


##
#
#{
# "jsonrpc": "2.0",
#  "method": "command",
#  "params": [p1, p2, p3],
#  "id": 1
#}
def command_jsonrpc_socket(ctx, dryrun, srvaddr, rcvaddr, oformat, cmd, params=[], cbexec={}):
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

    scmd += '  "id": ' + str(randint(2,10000)) + '\n'
    scmd += "}\n"
    if dryrun:
        print json.dumps(json.loads(scmd), indent=4, separators=(',', ': '))
        return

    sockclient = None
    response = None
    socktype = "IPv4"
    host = None
    port = None
    if srvaddr.startswith("udp:"):
        ctx.vlog("udp socket provided: " + srvaddr)
        sproto, saddr = srvaddr.split(":", 1)
        if server.find("[", 0, 2) == -1:
            ctx.vlog("IPv4 socket address")
            host, port = saddr.split(':')
        else:
            ctx.vlog("IPv6 socket address")
            ehost, port = saddr.rsplit(':', 1)
            host = ehost.strip('[]')
            socktype = "IPv6"

        # create datagram udp socket
        try:
            if socktype == "IPv6":
                sockclient = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            else:
                sockclient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            sockclient.settimeout(4.0)
            sockclient.sendto(scmd, (host, port))

            # receive the response (content, sockserver)
            data = sockclient.recvfrom(84000)
            response = data[0]
            sockserver = data[1]

            ctx.vlog('Server response: ' + response)

        except socket.timeout, emsg:
            ctx.log('Timeout receiving response on udp socket')
            sys.exit()
        except socket.error, emsg:
            ctx.log('Error udp sock: ' + str(emsg[0]) + ' - ' + emsg[1])
            sys.exit()
    else:
        ctx.vlog("unix socket provided: " + srvaddr)
        if not os.path.exists( srvaddr ):
            ctx.vlog("server unix socket file not found")
            ctx.vlog("be sure kamailio is running and listening on: " + srvaddr)
            return
        # create datagram udp socket
        try:
            sockclient = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
            sockclient.settimeout( 4.0 )
            rcvaddr = rcvaddr + "." + str(os.getpid())
            sockclient.bind( rcvaddr )
            sockclient.connect( srvaddr )
            sockclient.send( scmd )

            # receive the response (content, sockserver)
            response = sockclient.recv(84000)
            sockclient.close()
            os.remove( rcvaddr )

            ctx.vlog('Server response: ' + response)

        except socket.timeout, emsg:
            ctx.log('Timeout receiving response on unix sock')
            sockclient.close()
            os.remove( rcvaddr )
            sys.exit()
        except socket.error, emsg:
            ctx.log('Error unix sock: ' + str(emsg[0]) + ' - ' + emsg[1])
            sockclient.close()
            os.remove( rcvaddr )
            sys.exit()

    if response is None :
        ctx.vlog("timeout - nothing read")
    else:
        command_ctl_response(ctx, response, oformat, cbexec)


##
#
def command_ctl(ctx, cmd, params=[], cbexec={}):
    """Execute a rpc control command

    \b
    Parameters:
      - ctx: kamcli execution context
      - cmd: the string with rpc control command
      - params: an array with the parameters for the rpc control command
      - cbexec: dictionary with callaback function and its parameters
                to handle the response of the rpc control commands. If not
                provided, the response will be printed with the function
                command_ctl_response_print().
                The callback function has to be provided by 'func' key in
                the dictionary and its parameters by 'params' key.
    """

    if ctx.gconfig.get('ctl', 'type') == 'jsonrpc':
        if ctx.gconfig.get('jsonrpc', 'transport') == 'socket':
            command_jsonrpc_socket(ctx, False, ctx.gconfig.get('jsonrpc', 'srvaddr'),
                    ctx.gconfig.get('jsonrpc', 'rcvaddr'), ctx.gconfig.get('jsonrpc', 'outformat'),
                    command_ctl_name(cmd, 'rpc'), params, cbexec)
        else:
            command_jsonrpc_fifo(ctx, False, ctx.gconfig.get('jsonrpc', 'path'),
                    ctx.gconfig.get('jsonrpc', 'rplnamebase'), ctx.gconfig.get('jsonrpc', 'outformat'),
                    command_ctl_name(cmd, 'rpc'), params, cbexec)
    else:
        command_mi_fifo(ctx, False, ctx.gconfig.get('mi', 'path'),
                ctx.gconfig.get('mi', 'rplnamebase'), "raw",
                command_ctl_name(cmd, 'mi'), params, cbexec)

