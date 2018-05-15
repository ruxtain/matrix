from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import hashlib
from matrix import raven, models
import time

token = ''

def is_from_wechat_server(request):
    '''
    判断请求是否来自微信的服务器
    '''
    signature = request.GET["signature"]
    timestamp = request.GET["timestamp"]
    nonce = request.GET["nonce"]
    my_list = [token,timestamp,nonce]
    my_list.sort()
    my_str = ''.join(my_list)
    hashcode = hashlib.sha1(my_str.encode('utf-8')).hexdigest()
    if hashcode == signature:
        return True
    else:
        return False

@csrf_exempt
def reply(request):
    #  POST 来自用户的消息 然后处理后进行自动回复
    # 根据官方指示，回复的是一个xml格式

    # with open('log.tan', 'a', encoding='utf-8') as f:
    #     log_tan = '############### {} ###############\nPOST: {}\nGET: {}\nBODY: {}\n'.format(
    #         time.strftime('%Y-%m-%d %H:%M'), 
    #         request.POST, 
    #         request.GET,
    #         request.body
    #     )
    #     print(log_tan, file=f)

    # 除了初次服务器验证用到GET方法，后面所有请求都是POST方法
    if request.method == 'POST':
        if is_from_wechat_server(request):
            xml = request.body.decode('utf-8')
            with open('requests.log', 'a', encoding='utf-8') as f:
                print('-'*80, file=f)
                print(xml, file=f)
            msg = raven.analyse(xml)     
            return HttpResponse(msg, content_type="text/xml") 
        else:
            return HttpResponse(status=403)

    # 用于微信服务器的首次校验，依然保留在这里供日后参考
    elif request.method == 'GET':
        # this is for debug
        with open('freeze-get-request.tan', 'w', encoding='utf-8') as f:
            print(request.GET, file=f)
        # 自定义的用于识别的签名
        # https://mp.weixin.qq.com/advanced/advanced?action=interface&t=advanced/interface&token=1219580966&lang=zh_CN
        signature = request.GET["signature"]
        timestamp = request.GET["timestamp"]
        nonce = request.GET["nonce"]
        echostr = request.GET["echostr"]
        my_list = [token,timestamp,nonce]
        my_list.sort()
        my_str = ''.join(my_list)
        hashcode = hashlib.sha1(my_str.encode('utf-8')).hexdigest()
        if hashcode == signature:
            return HttpResponse(str(echostr))
        else:
            return HttpResponse("Dude, don't you mess with my server.")

