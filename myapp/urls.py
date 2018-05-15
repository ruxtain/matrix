from django.conf.urls import url

from . import views

app_name = 'myapp' # 这个的作用就是增加一个 namespace

urlpatterns = [
    # project目录下的url必须是开放式的r'^',而app目录下的，必须是封闭式的，否则会url错乱，全部都匹配到r'^'这里
    url(r'^$', views.home, name='home'),
    url(r'^tt$', views.tt, name='tt'),
    url(r'^st$', views.st, name='st'),
    url(r'^bp$', views.bp, name='bp'),
    url(r'^pd$', views.pd, name='pd'),
    url(r'^about$', views.about, name='about'),
    url(r'^bdunion.txt$', views.baidu, name='baidu'), # 百度联盟验证用


    url(r'^code-generator$', views.ajaxCodeGenerator, name='ajaxCodeGenerator'),
    url(r'^divide-5$', views.ajaxDivide5, name='ajaxDivide5'),
    url(r'^feedback$', views.ajaxFeedback, name='ajaxFeedback'),
]