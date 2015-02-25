from stat_iface import StatIface

class Stat(StatIface):
    def __init__(self, uname):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')
        self.files = self.open_files({'diskstat': '/sys/block/sdb/stat'})
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()

    def read_stats(self, f):
        f.seek(0)
        line = f.readlines()[0].split()
        return {'reads_completed': [int(line[0])],
                'reads_merged': [int(line[1])], 
                'sectors_read': [int(line[2])], 
                'millis_reading': [int(line[3])], 
                'writes_completed': [int(line[4])], 
                'writes_merged': [int(line[5])], 
                'sectors_written': [int(line[6])],
                'millis_writing': [int(line[7])]}

    def update(self):
        self.data = self.read_stats(self.files['diskstat'])

    def diff(self, sleeptime):
        if self.last_data == None:
            self.last_data = self.data
            for key in self.data:
                self.diff_data[key] = [key]
            return
        for key in self.data:
            self.diff_data[key] = self.list_diff(self.data[key], self.last_data[key])
        self.last_data = self.data

    def bundle(self):
        bundle = []
        # join all values from self.diff_data dict into a single list
        # and convert each item to string
        values = [v for k, v in self.diff_data.iteritems()]
        map(bundle.extend, values)
        return map(lambda x: str(x), bundle)

