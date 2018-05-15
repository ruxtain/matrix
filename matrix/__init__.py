# The place where you put all common functions for all scripts

import time
import os


def get_log_path():
    basename = time.strftime('%y%m%d') + '.log'
    root = os.path.dirname(os.path.dirname(__file__))
    logfile = os.path.join(root, 'logs/' + basename) 
    return logfile


def print_log(*args, end='\n'):
    '''
    how to use: from matrix import print_log
    print the stuff on terminal
    as well as in the log file
    gakkit/logs/console.log
    pwd:/Users/michael/gakkit/matrix/__init__.py
    '''
    print(*args, end=end)
    
    stamp = time.strftime('[%y-%m-%d %H:%M:%S]')
    logfile = get_log_path()
    with open(logfile, 'a', encoding='utf-8') as f:
        print(stamp, *args, end=end, file=f)


# def log(filename, content, mode='w', set_stamp=True):
#     '''
#     keep a simple error log for requests
#     save the pages with errors locally
#     '''
#     stamp = time.strftime('%y%m%d-%H%M%S-')
#     root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
#     file = os.path.join(root, 'logs', stamp + filename)
#     with open(file, mode, encoding='utf-8') as f:
#         f.write(content)
#         print('[log recorded logs/{}]'.format(filename))