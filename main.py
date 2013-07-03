import sys, getopt
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
            sleeptime = arg
    capture(sleeptime)

if __name__ == '__main__':
    main(sys.argv)
