import glob
import time
from os.path import join

class ProcStat:
    def __init__(self):
        self.fstat = None
        self.fmem = None
        try:
            fstat = open('/proc/stat')
            fmem = open('/proc/meminfo')
            cpu_data = self.init_cpu_data()
        except IOError:
            raise Exception('Fatal error: some /proc or /sys features not available') 
        else:
            self.fstat = fstat
            self.fmem = fmem
            self.cpu_data = cpu_data
            self.current_data = None
            self.diff_data = None
            self.update()
            self.last_data = self.current_data.copy()
            self.diff_data = self.current_data.copy() # initialize structure, will get overwritten

    def file_read_int(self, f):
        '''
        Expects file contents to be: "n\n". Returns n as integer.
        '''
        # readline() will not return new values untiles the file is re-opened
        # we have to use readlines() for re-reading files using the same file handle.
        if type(f) is file:
            f.seek(0)
            n = int(f.readlines()[0].rstrip())
        else:
            fh = open(f)
            fh.seek(0)
            n = int(fh.readlines()[0].rstrip())
            fh.close()

        return n

    def read_pstates(self, fh):
        fh.seek(0)
        v = fh.readlines()
        return map(lambda x: int(x.rstrip().split()[-1]), v)

    def v_diff(self, a, b):
        '''
        return vector a - vector b
        '''
        return map(lambda x: x[0] - x[1], zip(a, b))

    def init_cpu_data(self):
        '''
        Open files and count present cpus.
        returns a dict: 
        'present' is the file handle for /sys/devices/system/cpu/present
        'num_cpus' is an integer representing the number of processors in the system
        'cstates' is a list, the ith element being the ith processor.
          Each processor is a list of C-states, and each C-state is a dict with three keys:
          'time_fh' is the file handle for the time in useconds spent in that C-state.
          'usage_fh' is the file handle for the number of times that was transitioned to that C-state.
          'latency' is the time penalty in usec for transitioning out of that C-state.
        'pstates' is a list, the ith element being the ith processor.
          Each processor is a dict with two keys:
          'time_in_state_fh' is the file handle for /sys/devices/system/cpu/cpuN/cpufreq/stats/time_in_state
          'pstates' is a list of integers for the time spent in each state, same order as time_in_state file
        '''
        data = {} 
        fpresent = open('/sys/devices/system/cpu/present')
        data['num_cpus'] = self.count_cpus(fpresent)
        fpresent.close()
        data['cstates'] = []
        data['pstates'] = []
        for i in range(0, data['num_cpus']):
            #cstate data
            cpu = []
            for state_path in glob.glob("/sys/devices/system/cpu/cpu%s/cpuidle/state*" % i):
                d = {}
                d['time'] = None
                d['usage'] = None
                d['time_diff'] = None
                d['usage_diff'] = None
                d['time_fh'] = open(join(state_path, 'time'))
                d['usage_fh'] = open(join(state_path, 'usage'))
                # read latency value
                d['latency'] = self.file_read_int(join(state_path, 'latency'))
                cpu.append(d)
            data['cstates'].append(cpu)

            #pstate data
            d = {}
            d['time_in_state_fh'] = open("/sys/devices/system/cpu/cpu%s/cpufreq/stats/time_in_state" % i)
            d['pstates'] = None
            d['diff'] = None
            data['pstates'].append(d) 

        return data
        
    def count_cpus(self, fpresent):
        fpresent.seek(0)
        line = fpresent.readline()
        # format of /sys/devices/system/cpu/present is "0\n" for single core or "0-X\n" for X-1 core
        # return X
        return int(line.rstrip()[-1]) + 1

    def create_bundle(self):
        '''Create the final data bundle that is to be sent. 
        Include any summarizing/aggregation and formatting.
        While explicitly listing values to be bundled reduces
        portability across architectures, it enhances the readability
        of what is being bundled, and in what order the data is stored.
        
        Each line:
        cpu[10] cpu0[10] .. cpuN[10] sum(intr) ctxt btime processes procs_running procs_blocked sum(softirq) memtotal memfree buffers cached dirty writeback cpu0_cstate0..cpu0_cstateN .. cpuN_cstate0..cpuN_cstateN
        '''
        bundle = []
        # get all values from diff_data that have cpu* keys
        cpudata = dict((k, v) for k, v in self.diff_data.items() if k.startswith('cpu'))
        #f = lambda x: int(x*1000) # convert from 0..1 double to 0..1000 integer
        # apply f to every cpudata item
        #cpudata = dict((k, map(f, v)) for k, v in cpudata.items())
        
        # bundle proc stats
        for k in cpudata:
            bundle.extend(cpudata[k])

        bundle.extend([sum(self.diff_data['intr'])])
        bundle.extend(self.diff_data['ctxt'])
        bundle.extend(self.diff_data['btime'])
        bundle.extend(self.diff_data['processes'])
        bundle.extend(self.diff_data['procs_running'])
        bundle.extend(self.diff_data['procs_blocked'])
        bundle.extend([sum(self.diff_data['softirq'])])
        bundle.extend([self.memdata[k] for k in self.memdata])

        # bundle cstates
        for cpu in self.cpu_data['cstates']:
            for cstate in cpu:
                bundle.extend(cstate['diff'])

        # bundle pstates
        for cpu in self.cpu_data['pstates']:
            bundle.extend(cpu['diff'])

        self.bundle = map(lambda x: str(x), bundle)

    #TODO: use count_cpus instead of this function
    def is_single_cpu(self, key):
            return (key.startswith('cpu') and len(key) > 3) # 'cpu0', 'cpu1', etc

    def cstates_difference(self):
        pass

    def pstates_difference(self):
        pass

    def stat_difference(self):
        if self.last_data == None:
            self.last_data = self.current_data
        for key in self.current_data:
            if key.startswith('proc'): # these values are not incremental
                continue
            i = 0
            while i < len(self.current_data[key]):
                self.diff_data[key][i] = self.current_data[key][i] - self.last_data[key][i]
                i = i + 1
        ## normalize CPU aggregate
        #period = self.diff_data['totaltime'][0]
        #time = period if period != 0 else 1 # first interval period is 0
        #f = lambda x: min(1.0, float(x) / time)
        #self.diff_data['cpu'] = map(f, self.diff_data['cpu'])
        ## normalize single CPU data
        #for key in self.diff_data:
        #    if self.is_single_cpu(key):
        #        old = self.diff_data[key]
        #        self.diff_data[key] = map(f, self.diff_data[key])
        ##        print "(%s %s => %s)" % (key, old, self.diff_data[key])

    def diff(self):
        if self.diff_data != None: # no reason to do difference when initializing class
            self.stat_difference()
            self.cstates_difference()
            self.pstates_difference()
            self.create_bundle()
        #print "(diff_data %s)" % self.diff_data

    def update(self):
        self.update_stat()
        self.update_mem()
        self.update_cstates()
        self.update_pstates()
        self.diff()

    def update_cstates(self):
        for cpu in self.cpu_data['cstates']:
            for cstate in cpu:
                cstate['time_last'] = cstate['time']
                cstate['usage_last'] = cstate['usage']
                cstate['time'] = self.file_read_int(cstate['time_fh'])
                cstate['usage'] = self.file_read_int(cstate['usage_fh'])
                if cstate['time_last'] == None:
                    cstate['time_last'] = cstate['time']
                    cstate['usage_last'] = cstate['usage']
                cstate['diff'] = [  cstate['time'] - cstate['time_last'], 
                                    cstate['usage'] - cstate['usage_last'] ]
                #print "%s - %s = %s" % (cstate['time'], cstate['time_last'], cstate['diff'])

    def update_pstates(self):
        for cpu in self.cpu_data['pstates']:
            cpu['pstates_last'] = cpu['pstates']
            cpu['pstates'] = self.read_pstates(cpu['time_in_state_fh'])
            if cpu['pstates_last'] == None:
                cpu['pstates_last'] = cpu['pstates']
            cpu['diff'] = self.v_diff(cpu['pstates'], cpu['pstates_last'])

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
        # totaltime = user + nice + system + idle + steal + guest
#        totaltime = (data['cpu'][0] + data['cpu'][1] + data['cpu'][2] + data['cpu'][3] + data['cpu'][7] + data['cpu'][8]) / num_cpus
        totaltime = sum(data['cpu']) / num_cpus
        data['totaltime'] = [ totaltime ] 
        self.last_data = self.current_data
        self.current_data = data.copy()

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
            elif line.startswith('Dirty'):
                data['Dirty'] = line.split()[1]
            elif line.startswith('Writeback'):
                data['Writeback'] = line.split()[1]
        self.memdata = data
        #print "(memdata %s)" % data

    def __del__(self):
        # Avoid opening the file more than once. Keep file open, close on del
        if (self.fstat != None):
            self.fstat.close()
        if (self.fmem != None):
            self.fmem.close()
        if (self.cpu_data != None):
            for cpu in self.cpu_data['cstates']:
                for cstate in cpu:
                    cstate['time_fh'].close()
                    cstate['usage_fh'].close()
            for cpu in self.cpu_data['pstates']:
                cpu['time_in_state_fh'].close()
                

    def __str__(self):
        return "%s\n" % ' '.join(self.bundle)

#    def marshal_bundle(self): # Deprecated, no longer used
#        return ''.join([struct.pack('>I', x) for x in self.bundle])
