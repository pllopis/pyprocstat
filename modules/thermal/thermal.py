from stat_iface import StatIface
import fnmatch
import os

class Stat(StatIface):
    def __init__(self, uname):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')
        paths = {}
        for z in self.find_thermal():
            paths[z[0]] = z[1]
        for i in self.find_input():
            paths[i[0]] = i[1]

        self.files = self.open_files(paths)
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()

    def find_thermal(self):
        matches = []
        for root, dirnames, filenames in os.walk('/sys/devices/virtual/thermal/'):
            for filename in filenames:
                if filename == 'temp' or filename == 'cur_state':
                    yield ('%s_%s' % (os.path.split(root)[1], filename), os.path.join(root, filename))

    def find_input(self):
        matches = []
        for root, dirnames, filenames in os.walk('/sys/devices/platform/coretemp.0/'):
            for filename in filenames:
                if fnmatch.fnmatch(root, '*coretemp*') and fnmatch.fnmatch(filename, '*input'):
                    yield (filename, os.path.join(root, filename))

    def update(self):
        for key, value in self.files.iteritems():
            self.data[key] = [self.file_read_int(value)]

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

