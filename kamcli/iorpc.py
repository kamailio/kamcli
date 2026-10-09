import os
import os.path
import sys
import shutil
import socket
import stat
import time
import threading
import json
from random import randint
from configparser import NoOptionError

##
# enable yaml output format if the lib can be loaded
iorpc_yaml_format = True
try:
    import yaml
except ImportError:
    iorpc_yaml_format = False
    pass  # yaml module doesn't exist, deal with it.


##
# RPC/MI commands aliases
#
# "alias" : {
#    "rpc": "rpc command",
# }
#
# - alias is used inside Python function
# - command_ctl(...) will use rpc variant
#   based on config options
COMMAND_NAMES = {
    "dispatcher.list": {
        "rpc": "dispatcher.list",
    },
    "dispatcher.reload": {
        "rpc": "dispatcher.reload",
    },
    "permissions.addressDump": {
        "rpc": "permissions.addressDump",
    },
    "permissions.addressReload": {
        "rpc": "permissions.addressReload",
    },
    "permissions.domainDump": {
        "rpc": "permissions.domainDump",
    },
    "permissions.subnetDump": {
        "rpc": "permissions.subnetDump",
    },
    "stats.clear_statistics": {
        "rpc": "stats.clear_statistics",
    },
    "stats.get_statistics": {
        "rpc": "stats.get_statistics",
    },
    "stats.reset_statistics": {
        "rpc": "stats.reset_statistics",
    },
    "ul.add": {
        "rpc": "ul.add",
    },
    "ul.dump": {
        "rpc": "ul.dump",
    },
    "ul.rm": {
        "rpc": "ul.rm",
    },
    "ul.lookup": {
        "rpc": "ul.lookup",
    },
}


def command_ctl_name(alias, ctype):
    """Return the rpc command name by alias lookup"""
    v = COMMAND_NAMES.get(alias, None)
    if v is None:
        return alias

    return COMMAND_NAMES[alias]["rpc"]


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
    print()
    if oformat == "json":
        print(
            json.dumps(
                json.loads(response.decode()), indent=4, separators=(",", ": ")
            )
        )
    elif oformat == "yaml":
        if iorpc_yaml_format is True:
            print(
                yaml.safe_dump(
                    json.loads(response.decode()), default_flow_style=False
                )
            )
        else:
            print(
                json.dumps(
                    json.loads(response.decode()),
                    indent=4,
                    separators=(",", ": "),
                )
            )
    else:
        print(response.decode())


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


class IOFifoThread(threading.Thread):
    """Thread to listen on a reply fifo file"""

    def __init__(self, ctx, rplpath, oformat, cbexec={}):
        threading.Thread.__init__(self)
        self.ctx = ctx
        self.rplpath = rplpath
        self.oformat = oformat
        self.cbexec = cbexec
        self.stop_signal = False

    def run(self):
        self.ctx.vlog("Starting to wait for reply on: " + self.rplpath)
        r = os.open(self.rplpath, os.O_RDONLY | os.O_NONBLOCK)
        scount = 0
        rcount = 0
        wcount = 0
        rdata = ""
        while not self.stop_signal:
            try:
                rbuf = os.read(r, 4096).decode()
            except BlockingIOError:
                # writer opened the fifo but did not write yet
                rbuf = ""
            if rbuf == "":
                if rcount != 0:
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

        if rcount == 0:
            self.ctx.vlog("timeout - nothing read")
        else:
            command_ctl_response(
                self.ctx, rdata.encode(), self.oformat, self.cbexec
            )


##
# {
#   "jsonrpc": "2.0",
#   "method": "command",
#   "params": [p1, p2, p3],
#   "reply_name": "kamailio_jsonrpc_reply_fifo",
#   "id": 1
# }
#
def command_jsonrpc_fifo(
    ctx,
    dryrun,
    sndpath,
    rcvname,
    oformat,
    storepath,
    cmd,
    params=[],
    cbexec={},
):
    scmd = '{\n  "jsonrpc": "2.0",\n  "method": "' + cmd + '",\n'
    if params:
        scmd += '  "params": ['
        comma = 0
        for p in params:
            if comma == 1:
                scmd += ",\n"
            else:
                comma = 1
            if type(p) is int:
                scmd += str(p)
            elif type(p) is float:
                scmd += str(p)
            else:
                if p.startswith("i:"):
                    scmd += p[2:]
                elif p.startswith("s:"):
                    scmd += '"' + p[2:] + '"'
                else:
                    scmd += '"' + p + '"'
        scmd += "],\n"

    scmd += '  "reply_name": "' + rcvname + '",\n'
    if storepath and len(storepath) > 0:
        scmd += '  "store_path": "' + storepath + '",\n'
    scmd += '  "id": ' + str(randint(2, 10000)) + "\n"
    scmd += "}\n"
    if dryrun:
        print(json.dumps(json.loads(scmd), indent=4, separators=(",", ": ")))
        return

    rcvpath = ctx.gconfig.get("jsonrpc", "rpldir") + "/" + rcvname
    if os.path.exists(rcvpath):
        if stat.S_ISFIFO(os.stat(rcvpath).st_mode):
            os.unlink(rcvpath)
        else:
            ctx.log("File with same name as reply fifo exists")
            sys.exit()

    os.mkfifo(rcvpath, 0o666)
    os.chmod(rcvpath, 0o666)
    try:
        shutil.chown(rcvpath, group=ctx.gconfig.get("jsonrpc", "kamgroup"))
    except NoOptionError:
        pass
    # create new thread to read from reply fifo
    tiofifo = IOFifoThread(ctx, rcvpath, oformat, cbexec)
    # start new threadd
    tiofifo.start()

    w = os.open(sndpath, os.O_WRONLY)
    os.write(w, scmd.encode())

    waitrun = True
    while waitrun:
        try:
            tiofifo.join(500)
            if not tiofifo.is_alive():
                waitrun = False
                break
        except KeyboardInterrupt:
            ctx.log("Ctrl-c received! Sending kill to threads...")
            tiofifo.stop_signal = True

    os.unlink(rcvpath)


def get_jsonrpc_response(ctx, scmd, proto, host, port, family, s_type):
    response = None
    try:
        sockclient = socket.socket(family, s_type)

        sockclient.settimeout(4.0)
        if proto == "udp":
            sockclient.sendto(scmd.encode(), (host, int(port)))
            data = sockclient.recvfrom(84000)
            response = data[0]
        elif proto == "tcp":
            sockclient.connect((host, int(port)))
            sockclient.sendall(scmd.encode())
            response = sockclient.recv(84000)
        else:
            srvaddr = host
            rcvaddr = port + "." + str(os.getpid())
            ctx.vlog("{proto} socket reply: " + rcvaddr)
            sockclient.bind(rcvaddr)
            os.chmod(rcvaddr, 0o666)
            try:
                shutil.chown(
                    rcvaddr, group=ctx.gconfig.get("jsonrpc", "kamgroup")
                )
            except NoOptionError:
                pass
            sockclient.sendto(scmd.encode(), srvaddr)
            response = sockclient.recv(84000)
        sockclient.close()
        if proto == "unix":
            os.remove(rcvaddr)

        ctx.vlog("Server response: " + response.decode())

    except socket.timeout:
        ctx.log(f"Timeout receiving response on {proto} socket")
        sockclient.close()
        if proto == "unix":
            os.remove(rcvaddr)
        sys.exit()
    except socket.error as emsg:
        ctx.log(f"Error {proto} sock: {emsg.errno} - {emsg.strerror}")
        sockclient.close()
        if proto == "unix":
            os.remove(rcvaddr)
        sys.exit()
    return response


def get_srv_info(ctx, srvaddr):
    socktype = socket.SOCK_DGRAM
    if srvaddr.startswith("udp:") or srvaddr.startswith("tcp:"):
        sproto, saddr = srvaddr.split(":", 1)
        ctx.vlog(f"{sproto} socket provided: " + srvaddr)
        if saddr.find("[", 0, 2) == -1:
            ctx.vlog("IPv4 socket address")
            host, port = saddr.split(":")
            family = socket.AF_INET
        else:
            ctx.vlog("IPv6 socket address")
            host, port = saddr.rsplit(":", 1)
            host = host.strip("[]")
            family = socket.AF_INET6
        if sproto == "tcp":
            socktype = socket.SOCK_STREAM
    else:
        sproto = "unix"
        family = socket.AF_UNIX
    return sproto, host, port, family, socktype


##
#
# {
#   "jsonrpc": "2.0",
#   "method": "command",
#   "params": [p1, p2, p3],
#   "id": 1
# }
def command_jsonrpc_socket(
    ctx,
    dryrun,
    srvaddr,
    rcvaddr,
    oformat,
    storepath,
    cmd,
    params=[],
    cbexec={},
):
    scmd = '{\n  "jsonrpc": "2.0",\n  "method": "' + cmd + '",\n'
    if params:
        scmd += '  "params": ['
        comma = 0
        for p in params:
            if comma == 1:
                scmd += ",\n"
            else:
                comma = 1
            if type(p) in [int, float]:
                scmd += str(p)
            else:
                if p.startswith("i:"):
                    scmd += p[2:]
                elif p.startswith("s:"):
                    scmd += '"' + p[2:] + '"'
                else:
                    scmd += '"' + p + '"'
        scmd += "],\n"

    if storepath and len(storepath) > 0:
        scmd += '  "store_path": "' + storepath + '",\n'

    scmd += '  "id": ' + str(randint(2, 10000)) + "\n"
    scmd += "}\n"
    if dryrun:
        print(json.dumps(json.loads(scmd), indent=4, separators=(",", ": ")))
        return

    response = None
    sproto, host, port, sfamily, stype = get_srv_info(ctx, srvaddr)
    if sproto in ["udp", "tcp"]:
        response = get_jsonrpc_response(
            scmd, sproto, host, port, sfamily, stype
        )
    else:
        if not os.path.exists(srvaddr):
            ctx.vlog("server unix socket file not found")
            ctx.vlog(
                "be sure kamailio is running and listening on: " + srvaddr
            )
            return
        response = get_jsonrpc_response(
            ctx, scmd, sproto, srvaddr, rcvaddr, sfamily, stype
        )

    if response is None:
        ctx.vlog("timeout - nothing read")
    else:
        command_ctl_response(ctx, response, oformat, cbexec)


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

    if ctx.gconfig.get("jsonrpc", "transport") == "socket":
        command_jsonrpc_socket(
            ctx,
            False,
            ctx.gconfig.get("jsonrpc", "srvaddr"),
            ctx.gconfig.get("jsonrpc", "rcvaddr"),
            ctx.gconfig.get("jsonrpc", "outformat"),
            "",
            command_ctl_name(cmd, "rpc"),
            params,
            cbexec,
        )
    else:
        command_jsonrpc_fifo(
            ctx,
            False,
            ctx.gconfig.get("jsonrpc", "path"),
            ctx.gconfig.get("jsonrpc", "rplnamebase"),
            ctx.gconfig.get("jsonrpc", "outformat"),
            "",
            command_ctl_name(cmd, "rpc"),
            params,
            cbexec,
        )
