class StatIface:
    def __init__(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def diff(self):
        raise NotImplementedError

    def bundle(self):
        raise NotImplementedError

    def summarize(self):
        raise NotImplementedError

    def open_files(self, files):
       '''
       Expects a dict where key is a name (str), and value is file path (str).
       Returns a dict with the same keys, but open file descriptors instead of paths.
       '''
       return dict((name, open(files[name])) for name in files )
        
    def file_read_int(self, f):
        '''
        Expects file contents to be: "n\n". Returns n as integer.
        '''
        # readline() will not return new values untiles the file is re-opened
        # we have to use readlines() for re-reading files using the same file handle.
        if type(f) is file:
            f.seek(0)
            n = int(f.readlines()[0].rstrip())
        else:
            fh = open(f)
            fh.seek(0)
            n = int(fh.readlines()[0].rstrip())
            fh.close()
        return n

    def file_read_fields(self, f, fields=None, val_idx=0):
        '''
        Grep for certain fields in a file. Returns a dict with field:int(value)
        For a file such as
        field1: 10
        field2  20 kb
        Will return { 'field1': 10, 'field2': 20 }. Field can have : as suffix,
        If fields=None, all fields are returned. Otherwise greps for strings in fields list.
        The val_idx argument determines which column (index from 0) contains the value.
        val_idx=0 means return everything from the second to last column as array of ints
        '''
        f.seek(0)
        lines = f.readlines()
        if fields is None:
            grep_lines = lines
        else:
            grep_lines = [w for w in lines if w.split()[0].rstrip(':') in fields]

        d = {}
        for line in grep_lines:
            columns = line.split()
            field = columns[0].rstrip(':')
            if val_idx != 0:
                value = [int(line.split()[val_idx])]
            else:
                value = map(int, columns[1:])
            d[field] = value
        return d

    def list_diff(self, a, b):
        '''
        return vector a - vector b
        '''
        return map(lambda x: x[0] - x[1], zip(a, b))



