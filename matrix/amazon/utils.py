# 只放功能性的

from bs4 import BeautifulSoup
import requests
import time
import os
import re

from matrix.amazon import meta
from matrix.amazon import proxy_pool
from matrix.models import *


# 根据一篇博客[https://blog.hartleybrody.com/scrape-amazon/]试一下简化版（strip query params）
# BASE_URL = '/product-reviews/{}/?reviewerType=all_reviews&filterByStar=critical&pageNumber=1&sortBy=recent'

def get_me(url):
    return re.findall(r'me=([A-Z0-9]+)', url)[0]

def get_asin_from_url(url):
    return re.findall(r'/([A-Z0-9]{10})', url)[0]

def get_store_by_url(url):
    from matrix.models import Store
    store = Store.objects.filter(me=get_me(url))
    if len(store) == 1:
        return store[0]

# 暂时只支持英美两国
def get_country_from_url(url):
    if 'www.amazon.co.uk/' in url:
        return 'UK'
    elif 'www.amazon.com/' in url:
        return 'US'
    elif 'www.amazon.es/' in url:
        return 'ES'
    elif 'www.amazon.co.jp/' in url:
        return 'JP'
    elif 'www.amazon.fr/' in url:
        return 'FR'
    elif 'www.amazon.it/' in url:
        return 'IT'
    elif 'www.amazon.de/' in url:
        return 'DE'
    elif 'www.amazon.ca/' in url:
        return 'CA'
    elif 'www.amazon.com.au/' in url:
        return 'AU'
    else:
        return False

def get_soup_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        c = f.read()    
    return BeautifulSoup(c, 'lxml')

def get_response(url):
    '''从url获取response，失败则返回 status_code, 负数表示我自定义的错误码'''
    proxy = None
    while not proxy: # 保证不为None
        proxy = proxy_pool.get_proxy()
    headers = {
            'User-agent': meta.get_user_agent(),
            'content-type':'text/plain',
            'cache-control':'no-cache'
        }
    flag = 0 # flag 为0表示代理健康，为负数表示错误代码
    try:
        response = requests.get(url, proxies={'http':proxy.url}, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        flag = -1 # time out (my own status_code)
    except requests.exceptions.ConnectionError:
        flag = -2 # requests.exceptions.ConnectionError: HTTPSConnectionPool(host='www.amazon.com', port=443): Read timed out.
    except requests.exceptions.SSLError:
        flag = -3 # 原因不详
    if flag != 0:
        proxy.fail += 1
        proxy.save()
        return (flag, proxy)
    status_code = response.status_code
    if status_code == 200:
        response.encoding = 'utf-8'
        # debug
        # log('soup-fail-{}.html'.format(time.time()), response.text)
        # 注意debug一律只有一行，请不要随便注释掉有用的代码
        return (response.text, proxy)
    else:
        proxy.fail += 1
        proxy.save()
        # debug
        # with open('error-{}.html'.format(time.time()), 'w', encoding='utf-8') as f:
        #     f.write(response.text)
        return (status_code, proxy)



# 2018-02-09 更新
def get_soup_from_url(url):
    '''
    输入一个url和一个明确的国别，还你一个正确的soup
    我的理解是美国的网站只用美国地址访问，减少可疑的程度
    分离request部分和解析部分。
    '''
    proxy = proxy_pool.get_proxy()
    proxies = {
            'http': 'http://' + url, 
            'https': 'https://' + url, 
        }
    headers = {
            'User-agent': meta.get_user_agent(),
            'content-type':'text/plain',
            'cache-control':'no-cache'
        }
    try:
        requests.get(url, proxies=proxies, headers=headers, timeout=10)
    except: # 不管错误原因，没有抓到页面，一律怪代理
        pass








