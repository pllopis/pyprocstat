class ProcStat:
    def __init__(self):
        self.fstat = None
        try:
            fstat = open("/proc/stat")
        except IOError:
            raise Exception('Fatal error: no procfs') 
        else:
            self.fstat = fstat
            self.update()

    def update(self):
        self.data = self.fstat.readlines()

    def __del__(self):
        # Avoid opening the file more than once
        if (self.fstat != None):
            close(self.fstat)
