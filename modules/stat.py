from stat_iface import StatIface

class Stat(StatIface):
    def __init__(self):
        self.files = self.open_files({'stat': '/proc/stat'})
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()

    def update(self):
        self.data = self.file_read_fields(self.files['stat'])
        
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
        self.summarize() # summarize diff_data

    def summarize(self):
        self.diff_data['intr'] = [sum(self.diff_data['intr'])]
        self.diff_data['softirq'] = [sum(self.diff_data['softirq'])]

    def bundle(self):
        bundle = []
        cpudata = dict((k, v) for k, v in self.diff_data.items() if k.startswith('cpu'))
        for k in cpudata:
            bundle.extend(cpudata[k])
        bundle.extend(self.diff_data['intr'])
        bundle.extend(self.diff_data['ctxt'])
        bundle.extend(self.diff_data['btime'])
        bundle.extend(self.diff_data['processes'])
        bundle.extend(self.diff_data['procs_running'])
        bundle.extend(self.diff_data['procs_blocked'])
        bundle.extend(self.diff_data['softirq'])
        bundle = map(lambda x: str(x), bundle)
        return bundle

