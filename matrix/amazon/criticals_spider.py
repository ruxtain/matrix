# 根据asin爬取差评的情况
# 直接爬取所有 flag=False的asin，并把爬取到的flag调成True

# TODO LIST:
# A COMBINATION OF MULTIPROCESSING AND GEVENT
# http://xiaorui.cc/2016/01/17/python%E4%B8%8Bmultiprocessing%E5%92%8Cgevent%E7%9A%84%E7%BB%84%E5%90%88%E4%BD%BF%E7%94%A8/

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
from matrix import print_log
from matrix.models import *
from matrix.amazon import utils, alert
import multiprocessing
from django.db import connection 
from matrix.amazon import domains, listing_urls, BASE_URL


def save_critical(critical, asin):
    Data(number=critical, asin=asin).save()
    asin.flag = True
    asin.save()
    # 为了让日志更清爽，成功的就不显示了
    # print_log('[criticals_spider.py]', asin, critical, 'is saved.')

def debug_save_html(asin, soup, head=''):
    the_date = str(datetime.datetime.now())
    the_asin = str(asin)
    with open('logs/'+head+the_asin+' '+the_date+'.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

def get_critical_from_asin(asin):
    '''
    asin指asin object，不是字符串
    '''
    def get_few_review(soup): # 一般是1个
        # base_url 本来就是查询的差评页，所以只要底下有任何评论，都是差评，都是含有 data-hook="review"字段的
        reviews = soup.find_all('div', attrs={'data-hook': 'review'})  # 找不到返回 []，注意是find_all 有下划线
        return len(reviews) # 直接返回 critical reviews 的个数 可以为0

    url = urljoin(domains[asin.country], BASE_URL.format(asin.value))
    response, proxy = utils.get_response(url)
    if type(response) != int:
        soup = BeautifulSoup(response, 'lxml')

        # 有差评才有这个
        critical_review_list = soup.find(id='cm_cr-review_list')
        if critical_review_list: # 有差评
            try:
                raw_nums = critical_review_list.find('span', class_='a-size-base')
                nums = raw_nums.text.replace(',', '').replace('.', '')
                nums = re.findall('\d+', nums)
            except AttributeError:
                with open('none.txt', 'a', encoding='utf-8') as f:
                    f.write(soup)
                print_log('[criticals_spider.py] none.txt captured.')
            try:
                num = max(nums)
                print(asin, 'get {} review.'.format(num))
                save_critical(num, asin) 
            except ValueError: # 有评论，但是没有差评
                print(asin, 'get 0 critical review.')
                save_critical(0, asin) 
        elif 'Correios.DoNotSend' in str(soup):
            proxy.fail += 1
            proxy.set_rate()
            proxy.set_stamp()
            proxy.save()
            print(asin, 'is busted.') # 没有用print_log
        else: # 这种是完全没任何评论
            print(asin, 'get no review at all.')
            save_critical(0, asin)            
    else:
        print('ERR CODE:', response, asin)
        if response == 404: # 该asin已经失效
            asin.valid = False
            asin.save()
        elif response == 503:
            proxy.fail += 1
            proxy.set_rate()
            proxy.set_stamp()
            proxy.save()            

def get_asins():
    # asin 乱序
    for asin in Asin.objects.filter(valid=True, flag=False).order_by('?'):
        yield asin

############## 以下为中央部分 #################

def main():
    connection.close()
    print_log('[criticals_spider.py] Get criticals from ASINs...')
    # 经过测试如果进程为10，勉强服务器还能带得动，如果再大，没有试过
    # 进程为30则直接宕机。
    pool = multiprocessing.Pool(processes=3)
    while Asin.objects.filter(flag=False): # as long as it's not done, it will start another poll
        pool.map(get_critical_from_asin, get_asins())        
    pool.close()
    # print_log('[criticals_spider.py] Entering alert.send_alerts()...')
    alert.send_alerts() # 每次数据全部爬完来一次
    print_log('[criticals_spider.py] All done.')
    connection.close()




















