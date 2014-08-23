import unittest
import procstat
from modules.stat_iface import StatIface
from StringIO import StringIO

class StatIfaceTest(StatIface):
    def __init__(self):
        pass
    def update(self):
        pass
    def diff(self):
        pass
    def bundle(self):
        pass

class MyTests(unittest.TestCase):
    def test_default_constructor(self):
        procstat.ProcStat()
    
    def test_custom_constructor(self):
        procstat.ProcStat(load_modules=['stat', 'meminfo'])

    def test_fail_custom_constructor(self):
        with self.assertRaises(Exception):
            procstat.ProcStat(load_modules=['nonexistingASDFASDF'])

    def test_statiface_file_read_fields_single_column(self):
        f=StringIO("field1: 5\nfield2 20 kB\n")
        d = {}
        d = StatIfaceTest().file_read_fields(f, fields=['field1', 'field2'], val_idx=1)
        self.assertItemsEqual(d, {'field1': [5], 'field2': [20]})

    def test_statiface_file_read_fields_multi_column(self):
        f=StringIO("field1: 1 2\nfield2 3 4\n")
        d = {}
        d = StatIfaceTest().file_read_fields(f, fields=['field1', 'field2'])
        self.assertItemsEqual(d, {'field1': [1, 2], 'field2': [3, 4]})

    def test_statiface_file_read_fields(self):
        f=StringIO("field1: 1 2\nfield2 3 4\nfield3 5 6 7 8\n")
        d = {}
        d = StatIfaceTest().file_read_fields(f)
        self.assertItemsEqual(d, {'field1': [1, 2], 'field2': [3, 4], 'field3': [5, 6]})

def main():
    unittest.main()

if __name__ == "__main__":
    main()
