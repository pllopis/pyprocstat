from stat_iface import StatIface
import glob
import os
import multiprocessing

class Stat(StatIface):
    def __init__(self, uname):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')
        # basic sanity check
	if (not os.path.isdir('/sys/devices/system/cpu/cpu0/cpustat') or
	   (not os.path.isfile('/sys/devices/system/cpu/cpu0/cpustat/temp'))):
	    raise Exception('cpustat module does not seem to be present.')
        self.files = {}
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()
        for cpu in xrange(0, multiprocessing.cpu_count()):
            for filename in glob.glob('/sys/devices/system/cpu/cpu%d/cpustat/*' % cpu):
                file = os.path.basename(filename)
                name = 'cpu%d_%s' % (cpu, file)
                self.files[name] = open(filename)
 

    def update(self):
        for name, file in self.files.iteritems():
            if name.endswith('cpustat'):
                d = self.file_read_fields(file)
                cpudata = dict(('%s_%s' % (name, key), value) for (key, value) in d.items())
                self.data.update(cpudata)
            else:
                self.data[name] = [self.file_read_int(file)]

    def diff(self, sleeptime):
        if self.last_data == None:
            self.last_data = self.data
            for key in self.data:
                self.diff_data[key] = [key]
            return
        for key in self.data:
            self.diff_data[key] = self.data[key]


    def bundle(self):
        bundle = []
        # join all values from self.diff_data dict into a single list
        # and convert each item to string
        values = [v for k, v in self.diff_data.iteritems()]
        map(bundle.extend, values)
        return map(lambda x: str(x), bundle)

