from stat_iface import StatIface

class Stat(StatIface):
    def __init__(self, uname):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')
        self.files = self.open_files({'vmstat': '/proc/vmstat'})
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()

    def update(self):
        fields = ['pgfault', 'pgmajfault', 'nr_active_file', 'nr_inactive_file', 'nr_active_anon', 'nr_inactive_anon', 'nr_mapped']
        self.data = self.file_read_fields(self.files['vmstat'], 
                        val_idx=1, fields=fields)

    def diff(self):
        if self.last_data == None:
            self.last_data = self.data
            for key in self.data:
                self.diff_data[key] = [key]
            return
        for key in self.data:
            self.diff_data[key] = self.list_diff(self.data[key], self.last_data[key])


    def bundle(self):
        bundle = []
        # join all values from self.diff_data dict into a single list
        # and convert each item to string
        values = [v for k, v in self.diff_data.iteritems()]
        map(bundle.extend, values)
        return map(lambda x: str(x), bundle)

