import os, sys, getopt, socket, time, struct
from procstat import ProcStat

def capture(sleeptime, port, quiet=False):
    stat = ProcStat()
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

def main(argv):
    sleeptime = 1
    port = 1234
    quiet = False
    try:
        opts, args = getopt.getopt(argv[1:], 'ht:p:q')
    except getopt.GetoptError:
        print "%s -t <sleep time (s)>" % argv[0]
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "%s -t <sleep time (s)> -p <listen port> -q (set quiet flag)" % argv[0]
            sys.exit(2)
        elif opt == '-t':
            # sanity check for int/float supplied value
            try:
                sleeptime = float(arg)
            except ValueError:
                print "Argument for -t must be float or int. Supplied: %s" % arg
                sys.exit(3)
        elif opt == '-p':
            try:
                port = int(arg)
            except ValueError:
                print "Argument for -p must be an integer port number. Supplied: %s" % arg
                sys.exit(4)
        elif opt == '-q':
            quiet = True

    # /proc gets updated at USER_HZ, so don't allow frequencies above this value
    user_hz_t = float(1) / os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    if user_hz_t > sleeptime:
        print "There is no point in having a sleep time (%s) smaller than 1/USER_HZ (%s). Supply a greater sleep time." % (sleeptime, user_hz_t)
        sys.exit(4)
    # capture system data at specified time intervals
    capture(sleeptime, port, quiet)

if __name__ == '__main__':
    main(sys.argv)
