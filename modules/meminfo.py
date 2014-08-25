from stat_iface import StatIface

class Stat(StatIface):
    def __init__(self):
        self.files = self.open_files({'meminfo': '/proc/meminfo'})
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()

    def update(self):
        fields = ['MemTotal', 'MemFree', 'Buffers', 'Cached',
                    'Dirty', 'Writeback']
        self.data = self.file_read_fields(self.files['meminfo'], 
                        val_idx=1, fields=fields)

    def diff(self):
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

