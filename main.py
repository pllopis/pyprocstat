import os, sys, getopt, socket, time
from procstat import ProcStat

def capture(sleeptime, address):
    stat = ProcStat()
    print "Sending samples to %s:%s" % (address[0], address[1])
    s = socket.create_connection(address, 10)
    while True:
        stat.update()
        data = str(stat)
        t1 = time.time()
        s.sendall(data)
        t2 = time.time()
        t = t2 - t1
        print "Send time: %s" % t
        try:
            time.sleep(sleeptime)
        except:
            print "Interrupted! Closing up.."
            s.close()
            break

def main(argv):
    sleeptime = 1
    server = 'faisan8.arcos.inf.uc3m.es'
    port = 1234
    try:
        opts, args = getopt.getopt(argv[1:], 't:s:p:')
    except getopt.GetoptError:
        print "%s -t <sleep time (s)>" % argv[0]
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            # sanity check for int/float supplied value
            try:
                sleeptime = float(arg)
            except ValueError:
                print "Argument for -t must be float or int. Supplied: %s" % arg
                sys.exit(3)
        elif opt == '-s':
            server = arg
        elif opt == '-p':
            try:
                port = int(arg)
            except ValueError:
                print "Argument for -p must be an integer port number. Supplied: %s" % arg
                sys.exit(4)

    # /proc gets updated at USER_HZ, so don't allow frequencies above this value
    user_hz_t = float(1) / os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    if user_hz_t > sleeptime:
        print "There is no point in having a sleep time (%s) smaller than 1/USER_HZ (%s). Supply a greater sleep time." % (sleeptime, user_hz_t)
        sys.exit(4)
    # capture system data at specified time intervals
    capture(sleeptime, (server, port))

if __name__ == '__main__':
    main(sys.argv)
