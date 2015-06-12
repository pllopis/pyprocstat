import glob
import time
import importlib
import os
import ConfigParser
from os.path import join
from stat_iface import StatIface

class ProcStat:
    def __init__(self, config_path=os.path.expanduser('~/.pyprocstat/config')):
        try:
            self.instances = [i for i in self._get_instances(config_path)]
#        except ImportError:
#            raise Exception('Module %s not found.' % m)
#        except AttributeError:
#            raise Exception('Module %s does not contain class Stat.' % m)
#        except NotImplementedError:
#            raise Exception('Module %s does not implement StatIface.' % m)
        except Exception:
            raise

    def _get_instances(self, config_file):
        config = ConfigParser.RawConfigParser()
        config.read([config_file])
        module_names = config.sections()
        for module_name in module_names:
            module_kwargs = dict(config.items(module_name))
            module = importlib.import_module('modules.%s.%s' % (module_name, module_name))
            instance = getattr(module, 'Stat')(os.uname(), **module_kwargs)
            if not isinstance(instance, StatIface):
                raise NotImplementedError('module %s does not implement Stat' % m)
            yield instance

    def update(self, sleeptime):
        [instance.update() for instance in self.instances]
        [instance.diff(sleeptime) for instance in self.instances]
        self.bundle_data = []
        bundles = [instance.bundle() for instance in self.instances]
        map(self.bundle_data.extend, bundles)
        # add timestamp for this sample
        self.bundle_data.insert(0, '%.6f' % time.time()) 
    
    def __str__(self):
        return "%s\n" % ' '.join(self.bundle_data)

