class ProcStat:
    def __init__(self):
        self.fstat = None
        self.fmem = None
        try:
            fstat = open('/proc/stat')
            fmem = open('/proc/meminfo')
        except IOError:
            raise Exception('Fatal error: no procfs') 
        else:
            self.fstat = fstat
            self.fmem = fmem
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
        self.update_stat()
        self.update_mem()
        
    def update_stat(self):
        self.fstat.seek(0)
        rawdata = self.fstat.readlines()
        data = {}
        for line in rawdata:
            items = line.split()
            data[items[0]] = map(int, items[1:])
        data['intr'] = [sum(data['intr'])] # summarize intr
        self.last_data = self.current_data
        self.current_data = data.copy()
        if self.diff_data != None: # no reason to do difference when initializing class
            self.difference()
        print self.diff_data

    def  update_mem(self):
        self.fmem.seek(0)
        rawdata = self.fmem.readlines()
        data = {}
        for line in rawdata:
            if line.startswith('MemTotal'):
                data['MemTotal'] = line.split()[1]
            elif line.startswith('MemFree'):
                data['MemFree'] = line.split()[1]
            elif line.startswith('Buffers'):
                data['Buffers'] = line.split()[1]
            elif line.startswith('Cached'):
                data['Cached'] = line.split()[1]
        self.memdata = data
        print data

    def __del__(self):
        # Avoid opening the file more than once. Keep file open, close on del
        if (self.fstat != None):
            self.fstat.close()
        if (self.fmem != None):
            self.fmem.close()
