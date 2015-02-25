from stat_iface import StatIface
from cffi import FFI


class Stat(StatIface):
    cdef = """
    struct thread_data {
        unsigned long long tsc;
        unsigned long long aperf;
        unsigned long long mperf;
        unsigned long long c1;
        unsigned long long extra_msr64;
        unsigned long long extra_delta64;
        unsigned long long extra_msr32;
        unsigned long long extra_delta32;
        unsigned int smi_count;
        unsigned int cpu_id;
        unsigned int flags;
    #define CPU_IS_FIRST_THREAD_IN_CORE	0x2
    #define CPU_IS_FIRST_CORE_IN_PACKAGE	0x4
    };

    struct core_data {
        unsigned long long c3;
        unsigned long long c6;
        unsigned long long c7;
        unsigned int core_temp_c;
        unsigned int core_id;
    };

    struct pkg_data {
        unsigned long long pc2;
        unsigned long long pc3;
        unsigned long long pc6;
        unsigned long long pc7;
        unsigned long long pc8;
        unsigned long long pc9;
        unsigned long long pc10;
        unsigned int package_id;
        unsigned int energy_pkg;	/* MSR_PKG_ENERGY_STATUS */
        unsigned int energy_dram;	/* MSR_DRAM_ENERGY_STATUS */
        unsigned int energy_cores;	/* MSR_PP0_ENERGY_STATUS */
        unsigned int energy_gfx;	/* MSR_PP1_ENERGY_STATUS */
        unsigned int rapl_pkg_perf_status;	/* MSR_PKG_PERF_STATUS */
        unsigned int rapl_dram_perf_status;	/* MSR_DRAM_PERF_STATUS */
        unsigned int pkg_temp_c;

    };

    typedef struct cpu_data {
        struct thread_data *thread;
        struct core_data *core;
        struct pkg_data *package;
    } cpu_data_t;

    struct timeval {
        long int tv_sec;
        long int tv_usec;
    };

    int libintel_init();

    cpu_data_t *allocate_cpu_data(void);

    int get_cpu_counters(cpu_data_t *cpudata);

    char *compute_counters_row(cpu_data_t *cpudata1, cpu_data_t *cpudata2, struct timeval *tv_delta);

    char *get_header_row(void);
    """

    def __init__(self, uname):
        if uname[0] != 'Linux':
            raise Exception('OS required to be Linux.')
        self.ffi = FFI()
        self.ffi.cdef(self.cdef)
        self.lib = self.ffi.dlopen('./modules/libintel.so')
        ret = self.lib.libintel_init()
        if ret < 0:
            raise Exception('Error initializing libintel: %s' % ret)
        self.data = self.lib.allocate_cpu_data()
        self.last_data = self.lib.allocate_cpu_data()
        self.swap = self.ffi.new('cpu_data_t *')
        self.first_iteration = True
        self.diff_data = {}
        self.tv_delta = self.ffi.new('struct timeval *')
        self.update()

    def update(self):
        self.lib.get_cpu_counters(self.data)

    def pytime_to_timeval(self, timeval, pytime):
        timeval.tv_sec = int(pytime)
        timeval.tv_usec = 0 #int(1000000*(pytime - int(pytime)))

    def swap_counters(self):
        self.swap = self.data
        self.data = self.last_data
        self.last_data = self.swap

    def diff(self, sleeptime):
        self.diff_data = {}
        if self.first_iteration:
            self.first_iteration = False
            self.swap_counters()
            self.header = self.ffi.string(self.lib.get_header_row())
            for key in self.header.split():
                self.diff_data[key] = [key]
            return
        self.pytime_to_timeval(self.tv_delta, sleeptime)
        counters = self.ffi.string(self.lib.compute_counters_row(self.last_data, self.data, self.tv_delta))
        counters = counters.split()
        for idx, val in enumerate(self.header.split()):
            self.diff_data[val] = [counters[idx]]
        self.swap_counters()

    def bundle(self):
        bundle = []
        # join all values from self.diff_data dict into a single list
        # and convert each item to string
        values = [v for k, v in self.diff_data.iteritems()]
        map(bundle.extend, values)
        return map(lambda x: str(x), bundle)
        #return [v for k, v in self.diff_data.iteritems()]

