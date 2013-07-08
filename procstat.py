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
            self.last_data = self.current_data.copy()
            self.diff_data = self.current_data.copy() # initialize structure, will get overwritten

    def is_single_cpu(self, key):
            return (key.startswith('cpu') and len(key) > 3) # 'cpu0', 'cpu1', etc

    def stat_difference(self):
        if self.last_data == None:
            self.last_data = self.current_data
        for key in self.current_data:
            i = 0
            while i < len(self.current_data[key]):
                self.diff_data[key][i] = self.current_data[key][i] - self.last_data[key][i]
                i = i + 1
        # normalize CPU aggregate
        period = self.diff_data['totaltime'][0]
        time = period if period != 0 else 1 # first interval period is 0
        f = lambda x: min(1.0, float(x) / time)
        self.diff_data['cpu'] = map(f, self.diff_data['cpu'])
        # normalize single CPU data
        for key in self.diff_data:
            if self.is_single_cpu(key):
                old = self.diff_data[key]
                self.diff_data[key] = map(f, self.diff_data[key])
                print "(%s %s => %s)" % (key, old, self.diff_data[key])

    def update(self):
        self.update_stat()
        self.update_mem()
        
    def update_stat(self):
        self.fstat.seek(0)
        rawdata = self.fstat.readlines()
        data = {}
        num_cpus = 0
        for line in rawdata:
            items = line.split()
            data[items[0]] = map(int, items[1:])
            # count only lines starting with cpu0, cpu1, etc.
            # This will give total number of CPUs in system, 
            # as first 'cpu' line is an aggregate
            if line.startswith('cpu') and (not line.startswith('cpu ')):
                num_cpus = num_cpus + 1
        data['intr'] = [ sum(data['intr']) ] # summarize intr
        # totaltime = user + nice + system + idle + steal + guest
        totaltime = (data['cpu'][0] + data['cpu'][1] + data['cpu'][2] + data['cpu'][3] + data['cpu'][7] + data['cpu'][8]) / num_cpus
        data['totaltime'] = [ totaltime ] 
        self.last_data = self.current_data
        self.current_data = data.copy()
        if self.diff_data != None: # no reason to do difference when initializing class
            self.stat_difference()
        print self.diff_data

    def update_mem(self):
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

    def __str__(self):
        return "blablabla "
