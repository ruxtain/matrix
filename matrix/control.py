#! /usr/local/bin/python3
# I use 'free', which is only for Linux. Not for Mac OS.
import os

def get_memory():
    temp = '0x9bdf9212' # random words..
    os.system('free > {}'.format(temp))
    with open(temp) as f:
        m = f.read()
    os.remove(temp)
    ms = m.split()
    if ms[6] == 'Mem:':
        total = ms[7]
        free = ms[9]
        return('TOTAL: {:.2f} MB\nFREE: {:.2f} MB ({:.2f}%)'.format(\
            int(total)/1024,
            int(free)/1024,
            int(free)/int(total)*100))
    else:
        return('Error. Please read the code to fix.')