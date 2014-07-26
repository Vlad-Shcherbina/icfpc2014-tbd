import sys, os

import nose


if __name__ == '__main__':
    argv = sys.argv + [
        '--verbose', '--with-doctest',
        #'--with-coverage', '--cover-package=production',
        '--logging-level=DEBUG'
        ]
    if os.name == 'nt':
        # there's no curses on Windows
        argv.append('--ignore-files=^visualizer.py$')
    nose.run_exit(argv=argv)
