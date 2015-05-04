import os
import sys
import stat
import time
import threading
import json
from random import randint


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

    rcvpath = "/tmp/" + rcvname
    if os.path.exists(rcvpath):
        if stat.S_ISFIFO(os.stat(rcvpath).st_mode):
            os.unlink(rcvpath)
        else:
            print "File with same name as reply fifo exists"
            sys.exit()

    os.mkfifo(rcvpath)
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

    rcvpath = "/tmp/" + rcvname
    if os.path.exists(rcvpath):
        if stat.S_ISFIFO(os.stat(rcvpath).st_mode):
            os.unlink(rcvpath)
        else:
            print "File with same name as reply fifo exists"
            sys.exit()

    os.mkfifo(rcvpath)
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
        command_jsonrpc_fifo(ctx, False, "/var/run/kamailio/kamailio_jsonrpc_fifo",
                "kamailio_jsonrpc_fifo_reply", "json", cmd, params)
    else:
        command_mi_fifo(ctx, False, "/var/run/kamailio/kamailio_fifo",
                "kamailio_fifo_reply", "raw", cmd, params)

