import os.path
from pprint import pprint
import imp

def import_gcpy_file(name):
    module = imp.load_source(name, '../data/gcpy/{}.py'.format(name))
    module.int = lambda x: x == []
    return module
    
if __name__ == '__main__':
    zz = import_gcpy_file('ff')
    pprint(zz.main(([[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]], None), None))
        
    