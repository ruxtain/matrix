# 需要修改，只需要 https://www.amazon.com/s?&me=AY5XLL1NQPR7O&merchant=AY5XLL1NQPR7O&redirect=true
# 只要有 sellerID (也就是me, merchant，都是同一个值) 和国家就OK。

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import multiprocessing

import re
import time

from matrix.models import *
from matrix import print_log
from matrix.amazon import utils
from django.db import connection 

def get_asins_from_page(url):
    '''
    0. 工作原理：可以同时写两个yield，一个yield内容迭代完毕后，会接着
    迭代第二个的具体而言，先输出asin，该页面asin输出完毕后，就输出下一
    页的链接外函数判断是链接，则重复调用内函数，直至无法找到下一页链接为止

    1. 每次爬取店铺。如果asin未保存过，则保存，已保存过则忽略。
    2. 如果之前保存的asin，本次没有爬取到，则不做任何处理。
    3. 因为在criticals_spider中，可能发生302或者404（未经测试）
    4. 发生404，该asin直接valid=False就不再处理
    5. 发生302可能是跳到尚有货的变体（未经测试）
    '''
    response, proxy = utils.get_response(url)
    country=utils.get_country_from_url(url)
    if type(response) != int and 'Correios.DoNotSend' not in response:
        soup = BeautifulSoup(response, 'lxml')
        asin_strs = []
        lis = soup.find_all('li')
        for li in lis:
            if li.has_attr('data-asin'):
                asin_str = li['data-asin']
                if asin_str not in asin_strs:
                    asin_strs.append(asin_str) # 一般没有重复，但是确保万无一失，啰嗦一下 以后可能会去掉
        for asin_str in asin_strs:
            if not Asin.objects.filter(value=asin_str, country=country):
                asin = Asin(value=asin_str, country=utils.get_country_from_url(url), store=utils.get_store_by_url(url))
                asin.save() # 此asin是Asin对象和前面的字符串asin不是一回事
                print_log('[asins_spider.py]', asin, 'is newly added.')
            else:
                print('[asins_spider.py]', asin_str + '-' + utils.get_country_from_url(url), 'exists already.')
        try:
            time.sleep(5) # 确保万无一失，毕竟这个的实际频率很低
            next_page = urljoin(url, soup.find(id='pagnNextLink')['href'])
            get_asins_from_page(next_page) # 自我迭代
        except TypeError: # 最后一页
            print_log('[asins_spider.py]', url, 'is done.')
    else:
        print('[asins_spider.py]', 'Busted or other error!')
        proxy.fail += 1
        proxy.set_rate()
        proxy.set_stamp()
        proxy.save()        
        get_asins_from_page(url) # 重新爬一次（换了个代理）

def get_stores():
    '''
    根据last_update和当前时间戳的比较的确定要不要爬取
    如果last_update的值为0，表示新增的店铺，当然要爬取
    '''
    for user in User.objects.all():
        for store in user.store_set.all():
            last_update = store.last_update
            if time.time() - last_update > 259200: # 距离上次更新店铺已经3天
                store.last_update = int(time.time()) # 每次抓取前标记时间
                store.save()
                yield store.url

def main():
    connection.close()
    print_log('[asins_spider.py] Get ASINs from stores... ')
    pool = multiprocessing.Pool(processes=2) # 少于criticals_spider
    pool.map(get_asins_from_page, get_stores())        
    pool.close()
    connection.close()

def test():
    print(1)


























