# core.py 核心脚本，用于启动、调度整个项目，实现全自动化。
# 但是若要启动 core，则依赖于 view 的启动。服务器启动后，view 即启动。

from multiprocessing import Process
import os
import time
import random
import datetime

from matrix.amazon import criticals_spider, asins_spider
from matrix.models import *
from matrix.money import *
from matrix import print_log

def set_interval():
    '''白天用户上班期间2小时1抓，晚上4小时一抓'''
    current_hour = datetime.datetime.now().hour
    if current_hour in range(7, 22): # 7点到晚上9点
        return 3 # hour
    else:
        return 3.5 # hour

def run_spiders():
    '''
    启动所有爬虫
    1. 每48h抓取一次店铺asin。
    2. 1小时抓取一次差评。未来asin太多的话，会独立一台服务器无限抓。
    '''
    while True:
        asins_spider.main() # 自动只处理新店铺和久未更新的店铺
        Asin.objects.all().update(flag=False)
        # set_all_costs() # 每个用户判断一遍
        criticals_spider.main()
        interval = set_interval()
        print_log('[core.py] Wait for {} hour ... '.format(interval))
        time.sleep(interval * 3600 * random.uniform(0.9, 1.2)) # uncertainty
















