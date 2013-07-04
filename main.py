import os, sys, getopt
from time import sleep
from procstat import ProcStat

def capture(sleeptime):
    stat = ProcStat()
    while True:
        stat.update()
        sleep(sleeptime)

def main(argv):
    sleeptime = 1
    try:
        opts, args = getopt.getopt(argv[1:], 't:')
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
    # /proc gets updated at USER_HZ, so don't allow frequencies above this value
    user_hz_t = float(1) / os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    if user_hz_t > sleeptime:
        print "There is no point in having a sleep time (%s) smaller than 1/USER_HZ (%s). Supply a greater sleep time." % (sleeptime, user_hz_t)
        sys.exit(4)
    # capture system data at specified time intervals
    capture(sleeptime)

if __name__ == '__main__':
    main(sys.argv)
