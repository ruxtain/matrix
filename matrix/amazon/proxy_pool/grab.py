# 目前只能处理本地的raw_proxy.txt文件
from matrix.models import *
from matrix.amazon import proxy_pool
import multiprocessing
import time
import json
import random
import requests
import os

def tmp_save_proxy_to_db(raw_proxy_file='raw_proxy.txt'):
    '''
    将 raw_proxy.txt 的 proxy 存入数据库, production 下是肯定不会用这个的，所以前面加了 tmp
    '''
    current_path = os.path.dirname(os.path.realpath(__file__))
    proxy_file = os.path.join(current_path, raw_proxy_file)
    with open(proxy_file, 'r', encoding='utf-8') as f:
        for line in f:
            url = line.strip()
            if not Proxy.objects.filter(url=url): # 去重
                country = proxy_pool.get_proxy_country(url)
                # 未来再设置成 None，现在先设置成 True 一律视为有效，不进行 check
                proxy = Proxy(url=url, country=country, valid=True)
                proxy.save()
                print(country, proxy, 'is saved.')
                time.sleep(0.5)

def main():
    tmp_save_proxy_to_db()
