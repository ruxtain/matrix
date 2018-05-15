from django.conf.urls import url

from . import views

app_name = 'matrix' # 这个的作用就是增加一个 namespace

urlpatterns = [
    # project目录下的url必须是开放式的r'^',而app目录下的，必须是封闭式的，否则会url错乱，全部都匹配到r'^'这里
    url(r'^$', views.reply, name='reply'),
]