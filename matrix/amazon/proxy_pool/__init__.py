# 放置 proxy_pool 下共用的部分
# 对外交流的脚本

'''
未来可能购买代理的商家：
阿布 https://www.abuyun.com/pricing.html
西刺 http://www.xicidaili.com/wn/
'''

from matrix.models import *
import multiprocessing
import time
import json
import random
import requests
import os

def get_proxy_country(url):
    '''
    url 需要去掉端口部分
    根据 url 读取其所属的国别，读取失败则返回空字符
    '''
    url = url.split(':')[0]
    try:
        test_url = 'http://ip-api.com/json/{}'
        result = requests.get(test_url.format(url), timeout=10)
        j = json.loads(result.text)
        return j['countryCode']
    except:
        return ''

def save_proxy_to_db(url):
    '''
    将单个的 url，判断国别后，放入数据库，valid=None
    '''
    if not Proxy.objects.filter(url=url): # 去重
        country = get_proxy_country(url)
        proxy = Proxy(url=url, country=country, valid=None)
        proxy.save()
        print(country, proxy, 'is saved.')

def get_proxy(interval=60):
    '''
    从代理池取一个可以用的代理。
    对于 use，fail，rate的更新外置
    先不考虑国别的影响
    '''
    from matrix.models import Proxy
    now = int(time.time())
    pxys = Proxy.objects.filter(valid=True, stamp__lt=now-interval) # now > stamp + interval
    if pxys:
        pxy = pxys[0] # 符合条件里面的第一个 也就是use 最少的那一个
        pxy.stamp = now # 被提取的代理会被打上stamp，在interval时间段内不会再被用到
        pxy.use += 1
        pxy.save()
        return pxy
    else: # 一个符合条件的都没有，一般是因为所有符合条件的 proxy 冷却时间都未到, 暂停一秒后重试
        time.sleep(1)
        print('No proxy is available. Wait 1 sec and retry.')
        get_proxy(interval=interval)























