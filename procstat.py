import glob
import time
import importlib
import os
from os.path import join
from stat_iface import StatIface

default_modules = ['stat', 'meminfo', 'vmstat', 'temp']

class ProcStat:
    def __init__(self, load_modules=default_modules):
        uname = os.uname()
        try:
            modules = [importlib.import_module('modules.%s' % m) for m in load_modules]
            self.instances = [getattr(m, 'Stat')(uname) for m in modules]
            for i in self.instances:
                if not isinstance(i, StatIface):
                    raise NotImplementedError('module %s does not implement Stat' % m)
#        except ImportError:
#            raise Exception('Module %s not found.' % m)
#        except AttributeError:
#            raise Exception('Module %s does not contain class Stat.' % m)
#        except NotImplementedError:
#            raise Exception('Module %s does not implement StatIface.' % m)
        except Exception:
            raise

    def update(self):
        [instance.update() for instance in self.instances]
        [instance.diff() for instance in self.instances]
        self.bundle_data = []
        bundles = [instance.bundle() for instance in self.instances]
        map(self.bundle_data.extend, bundles)
    
    def __str__(self):
        return "%s\n" % ' '.join(self.bundle_data)

