from stat_iface import StatIface
from pyghmi.ipmi import command
import fnmatch
import os

class Stat(StatIface):
    def __init__(self, uname, ip, user, password):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')

        self.ipmisession = command.Command(bmc=ip, userid=user, password=password)
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()

    def update(self):
        for reading in self.ipmisession.get_sensor_data():
            key = 'IPMI_' + reading.name.replace(' ', '_').replace('-', '_')
            self.data[key] = [reading.value]

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

