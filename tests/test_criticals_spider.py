'''
本脚本专门用于测试核心爬虫 critical_spider.py
'''


# from matrix.amazon import criticals_spider
# from matrix.models import *
# a = Asin.objects.get(value='B0744FD9M4')
# criticals_spider.get_critical_from_asin(a)

from matrix.amazon import utils, criticals_spider

file = '/Users/michael/gakkit/logs/UK-B075DZP1GS 2018-02-06 19:54:46.015015.html'
soup = utils.get_soup_from_file(file)
a_review = soup.find('a', attrs={'data-reftag': 'cm_cr_arp_d_viewpnt_rgt'})
print(criticals_spider.has_no_review(soup))