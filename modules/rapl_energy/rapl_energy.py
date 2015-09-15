from stat_iface import StatIface

class Stat(StatIface):
    def __init__(self, uname):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')
        self.files = self.open_files({'rapl0_energy': '/sys/class/powercap/intel-rapl:0/energy_uj',
                                      'rapl1_energy': '/sys/class/powercap/intel-rapl:1/energy_uj'})
        self.last_data = None
        self.data = {}
        self.diff_data = {}

    def update(self):
        self.data['rapl0_energy'] = self.file_read_int(self.files['rapl0_energy'])
        self.data['rapl1_energy'] = self.file_read_int(self.files['rapl1_energy'])

    def diff(self, sleeptime):
        if self.last_data == None:
            # Since one iteration is not enough to gather differential data,
            # make sure first iteration returns a header with key name for every column,
            # while initializing last_data for second iteration and onwards.
            self.last_data = self.data.copy()
            for key in self.data:
                self.diff_data[key] = key
            return
        for key in self.data:
            self.diff_data[key] = self.data[key] - self.last_data[key]
        self.last_data = self.data.copy()

    def bundle(self):
        bundle = []
        # join all values from self.diff_data dict into a single list
        # and convert each item to string
        values = [v for k, v in self.diff_data.iteritems()]
        bundle.extend(values)
        m = map(lambda x: str(x), bundle)
        return m

