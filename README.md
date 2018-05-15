matrix
===
矩阵数据项目（亚马逊差评监控\+微信公众号）<br/>
项目地址：
https://github.com/ruxtain/matrix

---

简介
===
matrix 主要由三个部分组成：
+ Listing 编辑页 （使用方法可以参考 [这里](https://www.douban.com/group/topic/108880198/))
+ 亚马逊差评监控爬虫
+ 微信公众号后台

微信公众号后台的作用是允许用户通过公众号提交店铺地址，从而由产品爬虫遍历店铺并得到所有的 ASIN （即产品 ID）。再由差评监控爬虫定时抓取差评数量，并在差评数增加时发送邮件通知用户。

配置
===
首先创建虚拟环境并添加依赖：
```bash
$ virtualenv your-env
$ source your-env/bin/activate
$ pip -r install requirements.txt
```
数据库
---
后台采用 django 2.0。建议使用 postgresql：
```
# matrix/gakkit/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'matrix', # name of database
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```
公众号关联
---
在你的微信公众号的服务器配置中，有一个令牌（token）。拷贝到这里即可。
```
# matrix/matrix/views.py
token = ''
```
邮件
---
最初我用的阿里云的邮箱。你可以换成你的邮箱服务器。
```
# matrix/matrix/amazon/alert.py
def send_email(recipient, content_text, content_html, subject='No subject'):
    ...
    s = smtplib.SMTP_SSL('smtpdm.aliyun.com:465')
    s.login('info@service.gakkit.com', 'your-password')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()
```

启动服务器
---
可以通过 nginx 启动，但是需要根据你的情况修改相关配置：
matrix/gakkit_uwsgi.ini<br/>
matrix/gakkit_nginx.conf
测试时可以直接用 django 启动：
```
python manage.py runserver
```
启动爬虫
---
```
python manage.py shell < main.py
```
日志
---
```
ls gakkit/logs
```
可以看到按日期命名的所有日志。


