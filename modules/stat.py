from stat_iface import StatIface

class Stat(StatIface):
    def __init__(self, uname):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')
        self.files = self.open_files({'stat': '/proc/stat'})
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()

    def update(self):
        self.data = self.file_read_fields(self.files['stat'])
        self.fix_cpudata()

    def fix_cpudata(self):
        keys = self.data.items()
        for key, value in keys:
            if key.startswith('cpu'):
                value = self.data[key]
                self.data.pop(key, None)
                self.data['%s_user' % key] = [value[0]]
                self.data['%s_nice' % key] = [value[1]]
                self.data['%s_system' % key] = [value[2]]
                self.data['%s_idle' % key] = [value[3]]
                self.data['%s_iowait' % key] = [value[4]]
                self.data['%s_irq' % key] = [value[5]]
                self.data['%s_softirq' % key] = [value[6]]
                self.data['%s_steal' % key] = [value[7]]
                self.data['%s_guest' % key] = [value[8]]
                self.data['%s_guest_nice' % key] = [value[9]]
        
    def diff(self):
        if self.last_data == None:
            # Since one iteration is not enough to gather differential data,
            # make sure first iteration returns a header with key name for every column,
            # while initializing last_data for second iteration and onwards.
            self.last_data = self.data
            for key in self.data:
                self.diff_data[key] = [key]
            return
        for key in self.data:
            if key.startswith('proc'): # these values are not incremental
                self.diff_data[key] = self.data[key]
            else:
                self.diff_data[key] = self.list_diff(self.data[key], self.last_data[key])
        self.last_data = self.data
        self.summarize() # summarize diff_data

    def summarize(self):
        self.diff_data['intr'] = [sum(self.diff_data['intr'])]
        self.diff_data['softirq'] = [sum(self.diff_data['softirq'])]

    def bundle(self):
        bundle = []
        # join all values from self.diff_data dict into a single list
        # and convert each item to string
        values = [v for k, v in self.diff_data.iteritems()]
        map(bundle.extend, values)
        return map(lambda x: str(x), bundle)

