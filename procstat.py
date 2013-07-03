class ProcStat:
    def __init__(self):
        self.fstat = None
        try:
            fstat = open('/proc/stat')
        except IOError:
            raise Exception('Fatal error: no procfs') 
        else:
            self.fstat = fstat
            self.current_data = None
            self.diff_data = None
            self.update()
            self.orig_data = self.current_data.copy()
            self.last_data = self.orig_data
            self.diff_data = self.current_data.copy() # initialize structure, will get overwritten

    def difference(self):
        if self.last_data == None:
            self.last_data = self.current_data
        for key in self.current_data:
            i = 0
            while i < len(self.current_data[key]):
                self.diff_data[key][i] = self.current_data[key][i] - self.last_data[key][i]
                i = i + 1

    def update(self):
        self.fstat.seek(0)
        rawdata = self.fstat.readlines()
        data = {}
        for line in rawdata:
            items = line.split()
            data[items[0]] = map(int, items[1:])

        self.last_data = self.current_data
        self.current_data = data.copy()
        if self.diff_data != None: # no reason to do difference when initializing class
            self.difference()


    def __del__(self):
        # Avoid opening the file more than once
        if (self.fstat != None):
            self.fstat.close()
