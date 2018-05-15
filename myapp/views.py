from django.shortcuts import render
from django.http import HttpResponse
from .models import *

from . import utils
from ipware.ip import get_ip

def baidu(request):
    return HttpResponse('4ac307e46c51f1fefb94bb785af0b826')

def home(request):
    '''所有内容的目录放到这里'''
    return render(request, "myapp/home.html", {})

def ajaxCodeGenerator(request):
    '''can't put everything locally, gotta leave one thing to python'''
    htmlCode = request.POST['htmlCode']
    result = utils.codeGenerator(htmlCode)
    try:
        ip = get_ip(request)
        Description(ip=ip, content=result).save()
    except:
        pass # 数据库有什么错误都不能影响用户的使用
    return HttpResponse(result)

def ajaxDivide5(request):
    raw = request.POST['raw']
    ip = get_ip(request)
    content = utils.divide_into_5_parts(raw).strip()
    if not content.startswith('Tip:'):
        Keyword(ip=ip, content=content).save()
    return HttpResponse(content)

def ajaxFeedback(request):
    url = request.get_full_path()
    content = request.POST['feedback']
    try:
        ip = get_ip(request)
        Feedback(ip=ip, content=content, url=url).save()
        return HttpResponse('saved.')
    except:
        pass

def tt(request):
    '''处理 title'''
    return render(request, "myapp/tt.html", {})

def st(request):
    '''处理 search terms'''
    return render(request, "myapp/st.html", {})

def bp(request):
    '''处理 bullet points'''
    return render(request, "myapp/bp.html", {})

def pd(request):
    '''处理 product decription'''
    return render(request, "myapp/pd.html", {})

def about(request):
    '''介绍我的信息'''
    return render(request, "myapp/about.html", {})
    