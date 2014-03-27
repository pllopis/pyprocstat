#!/usr/bin/env python
"""
pyprocstat. Gathers system information from /sys, /proc and streams it over the network.

Usage:
  pyprocstat.py (-h | --help)
  pyprocstat.py [--quiet] [--sleep=<sleep_time>] [--port=<listen_port>] 

Options:
  -q --quiet      Do not print info being sent.
  -s --sleep=<sleep time>       Sleep time between proc readings in seconds, may be floating point. [default: 1.0]
  -p --port=<listen port>       Port to listen to. [default: 1234]

"""

import os, sys, getopt, socket, time, struct
from procstat import ProcStat
from docopt import docopt

def capture(sleeptime, port, quiet=False):
    stat = ProcStat()
    #for i in stat.cpu_data['cstates']:
    #    for j in i:
    #        print j['latency']
    #return
    server = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', port))
    server.listen(5)
    while True:
        print "Listening on address 0.0.0.0:%s" % port
        try:
            (s, address) = server.accept()
        except:
            print "Interrupted! Exiting.."
            sys.exit(0)
        if not quiet: print "Incoming connection from", address
        while True:
            stat.update() # gather system data
            data = str(stat)
            if not quiet: print "Sending (len %s): \"%s\"" % (len(data), data)
            data = struct.pack('!I', len(data)) + data # prefix payload with size_u32(payload)
            t1 = time.time()
            try:
                s.sendall(data)
            except:
                print "Connection closed! Restarting.."
                s.close()
                break
            t2 = time.time()
            t = t2 - t1
            if not quiet: print "Send time: %s" % t
            try:
                time.sleep(sleeptime)
            except:
                print "Interrupted! Restarting.."
                s.close()
                break

def main(arguments):
    sleeptime = float(arguments['--sleep'])
    port = int(arguments['--port'])
    quiet = arguments['--quiet']

    # /proc gets updated at USER_HZ, so don't allow frequencies above this value
    user_hz_t = float(1) / os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    if user_hz_t > sleeptime:
        print "There is no point in having a sleep time (%s) smaller than 1/USER_HZ (%s). Supply a greater sleep time." % (sleeptime, user_hz_t)
        sys.exit(4)

    # capture system data at specified time intervals
    capture(sleeptime, port, quiet)

if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)
