from stat_iface import StatIface
import serial
import select

class Stat(StatIface):
    def __init__(self, uname, serial_port, serial_baudrate, interval):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')
        self.serial = serial.Serial(serial_port, serial_baudrate)
        # empty WattsUp buffer
        self.serial.write('#L,W,3,E,,%d;' % (int(interval)))
        self.poll = select.poll()
        self.poll.register(self.serial, select.POLLIN)
        self.fastforward()
        self.last_data = None
        self.data = {}
        self.diff_data = {}
        self.update()

    def fastforward(self):
        while len(self.poll.poll(0)) > 0:
            self.serial.readline()

    def line_watts(self, line):
        fields = line.split(',')
        watts_field = fields[3]
        return float(watts_field) / 10

    def update(self):
        # while data is available for serial port read
        while len(self.poll.poll(0)) > 0:
            line = self.serial.readline()
            if line.startswith('#d,'):
                self.data['wuwatts'] = [self.line_watts(line)]
                return # mission complete
        # no data available at serial port, so 
        # avoid blocking, go with last read data
        # treat case where there was no last data
        if self.last_data == None:
            self.data['wuwatts'] = [None]
        else:
            self.data = self.last_data
        

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

