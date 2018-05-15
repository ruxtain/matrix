# 用于检查代理是否有效，将有效的放入代理池
from matrix.models import *
import multiprocessing
import time
import json
import random
import requests
import os

def is_valid_proxy(url):
    '''
    检测一个代理是否有效
    eg:
    In: 123.123.123.123:123
    Out: True
    '''
    test_urls = [
        'http://2017.ip138.com/ic.asp',
        'https://whatismyipaddress.com/proxy-check',
        'http://ip.chinaz.com/getip.aspx',
        'http://httpbin.org/ip',
    ]
    for test_url in test_urls:
        try:

            proxies = {
                'http': 'http://' + url, 
                'https': 'https://' + url, 
                }
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"}
            result = requests.get(test_url, proxies=proxies, headers=headers, timeout=5)
            # result.encoding='utf-8'
            if url.split(':')[0] in result.text: # 只要有一个测试网站测到了这个代理，就认为是 alive的
                return True 
        except:
            pass
    return False

def get_raw_proxies():
    '''
    返回所有的 野生的代理 进行检查
    '''
    for proxy in Proxy.objects.filter(valid=None):
        yield proxy

def check_proxy(proxy):
    '''
    输入 proxy 对象
    检查，合格的存，不合格的valid=False
    '''
    if is_valid_proxy(proxy.url):
        print('[check.py] {} is alive!'.format(proxy))
        proxy.valid = True
    else:
        print('[check.py] {} is dead.'.format(proxy))
        proxy.valid = False
    proxy.save()

def main():
    pool = multiprocessing.Pool(processes=3)
    pool.map(check_proxy, get_raw_proxies())        
    pool.close()














































