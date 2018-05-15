# http://www.mogumiao.com/ 蘑菇代理 （来自知乎推荐）

from matrix.models import *
from matrix.amazon import proxy_pool
import requests
import json
import time

# 免费试用API
# api = 'http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=5cc71e9d37dd415e94ca237e65d16301&count=30&expiryDate=0&format=1'

# response = requests.get(api)
# result = json.loads(response.text)
# if result['code'] == '0':
#     proxy_list = result['msg']


def get_proxy_from_mogu():
    '''
    类型：迭代器
    这里是测试版。以后购买了蘑菇的ip之后，直接访问api获取代理。
    '''
    result = ''' 
    {
        "code":"0",
        "msg":
        [
            {"port":"26565","ip":"123.55.178.242"},
            {"port":"49213","ip":"110.189.207.15"},
            {"port":"46869","ip":"171.13.37.102"},
            {"port":"22649","ip":"36.59.23.90"},
            {"port":"39748","ip":"113.93.102.174"},
            {"port":"20499","ip":"113.124.93.51"},
            {"port":"33231","ip":"60.167.22.143"},
            {"port":"44357","ip":"60.169.217.78"},
            {"port":"34729","ip":"117.83.116.86"},
            {"port":"33553","ip":"115.217.252.37"},
            {"port":"33697","ip":"171.15.92.166"},
            {"port":"24923","ip":"123.161.156.72"},
            {"port":"44672","ip":"61.174.227.21"},
            {"port":"21455","ip":"123.163.82.252"},
            {"port":"35180","ip":"49.85.4.219"},
            {"port":"44837","ip":"114.231.12.112"},
            {"port":"38315","ip":"59.57.29.111"},
            {"port":"23683","ip":"125.109.199.211"},
            {"port":"26602","ip":"122.4.47.201"},
            {"port":"22495","ip":"115.225.158.70"}
        ]
    }'''

    api = "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=01d3f9183ea74e4180308dd2e425e255&count=10&expiryDate=0&format=1"
    response = requests.get(api)
    result = json.loads(response.text)
    if result['code'] == '0':
        raw_list = result['msg']
        for p in raw_list:
            yield p['ip']+':'+p['port']


def save_proxy_to_db():
    '''将mogu的ip都存为proxy对象'''
    for url in get_proxy_from_mogu():
        if not Proxy.objects.filter(url=url): # 去重
            # country = proxy_pool.get_proxy_country(url)
            country = 'CN' # 蘑菇只有国内代理
            # 未来再设置成 None，现在先设置成 True 一律视为有效，不进行 check
            proxy = Proxy(url=url, country=country, valid=True)
            proxy.save()
            print(country, proxy, 'is saved.')

def main():
    while True:
        time.sleep(5)
        save_proxy_to_db()































