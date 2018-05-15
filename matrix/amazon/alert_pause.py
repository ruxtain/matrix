# alert 用于发送警报邮件#! /usr/local/bin/python3
# 用于用户的各类验证


import smtplib

from matrix.amazon import domains, listing_urls, BASE_URL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from email.header import Header
from email.utils import formataddr

from urllib.parse import urljoin

from matrix.models import *
from matrix import print_log
from matrix.amazon import utils

def make_report(user):
    '''
    输入用户，输出该用户最近的差评报告，字典形式

    比较同一asin的近两次data，如果number增加了则发邮件警报
    比较的时候，此时的flag都转成了True 表示已经爬取
    '''
    report = {}
    for store in user.store_set.all():
        for asin in store.asin_set.filter(valid=True):
            list_of_data = asin.data_set.order_by('-datetime')
            data0 = list_of_data[0] # 最新
            try:
                data1 = list_of_data[1] # 次新
            except IndexError:
                data1 = data0 # 报错表示没有次新，那么就是只有一次数据 视为没有变化即可
            delta = data0.number - data1.number
            if delta > 0 and delta <= 2: # 有新的差评
                url = urljoin(domains[asin.country], BASE_URL.format(asin.value))
                report[url] = delta
            elif delta > 2: # 一次增加超过两个差评，那么可能有bug
                try:
                    data2 = list_of_data[2] # 第三新
                except IndexError:
                    data2 = data1
                if data1.number != 0: #  data0, data1, data2 分别是 0 1 3
                    url = urljoin(domains[asin.country], BASE_URL.format(asin.value))
                    report[url] = delta
                elif data2.number == 0: # data0, data1, data2 分别是 0 0 2
                    url = urljoin(domains[asin.country], BASE_URL.format(asin.value))
                    report[url] = delta
    if report:  # report 不为空
        content_text = ''
        content_html = ''
        for url in report:
            content_text += '{} 有新差评 {} 个\n您现在的余额是 {} 元\n您也可以在“矩阵数据”公众号内回复“余额”查询。'.format(url, report[url], user.get_money())
            content_html += '<h2><a href="{}" target=_blank>{}-{}</a> 有新差评 {} 个</h2>'.format(\
                                                        url, \
                                                        utils.get_country_from_url(url),\
                                                        utils.get_asin_from_url(url),\
                                                        report[url])
        content_html += '<br><p>您现在的余额是 {} 元</p><p>您也可以在“矩阵数据”公众号内回复“余额”查询。</p>'.format(user.get_money())
        content_html += '<p>这个工具尚处于测试阶段，有任何问题，请您回复邮件，或者回复公众号哦，多谢合作！请记得设置本邮箱到白名单以免遗漏差评警报。</p>'
        content_html += '<p>温馨提示：多个变体的 ASIN，可能会在一封邮件里提示各个变体，但是其实没有那么多差评的。<br />此外，合并listing可能导致差评数陡然增加（因为叠加了两者的差评数），但下一次的警报即恢复正常。</p>'
        return content_text, content_html
    else:
        return [False, False]

def send_email(recipient, content_text, content_html, subject='No subject'):
    # print_log("[alert.py] email initialization ...")
    sender = "info@service.gakkit.com"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    # 只有这样发的邮件才有中文昵称哦。
    msg['From'] = formataddr(["矩阵数据", "info@service.gakkit.com"])
    msg['To'] = recipient
    # Create the body of the message (a plain-text and an HTML version).
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(content_text, 'plain')
    part2 = MIMEText(content_html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    s = smtplib.SMTP_SSL('smtpdm.aliyun.com:465')
    s.login('info@service.gakkit.com', 'wenQianYiZhengLu2018')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()

def alert_to_charge(user):
    '''计算是否足以支持现有ASIN数的一日抓取，如果不够，邮件提示用户充值'''
    content_text = '您现在的余额是 {} 元'.format(user.get_money)
    content_html = '<h2>您现在的余额是 {} 元</h2>'.format(user.get_money)
    send_email(user.email, content_text, content_html, subject='矩阵数据提醒您：您的余额将在24小时内耗尽，请尽快充值')
        

def send_alerts():
    '''
    遍历用户的asin，并整合成比较结果，然后发送邮件。
    '''
    for user in User.objects.filter(subscribe=True):
        content_text, content_html = make_report(user)
        if content_html: # non empty
            if user.email:
                print_log('[criticals_spider.py] Sending alerts to {}...'.format(user.email))
                send_email(user.email, content_text, content_html, subject="矩阵数据提醒您：亚马逊店铺有新的差评，请及时处理")
                Email(address=user.email, content_html=content_html).save()
            else:
                print_log('[criticals_spider.py] {} has\'t set email.'.format(user))

def test():
    recipient = 'ruxtain@foxmail.com'
    # recipient = '571061858@qq.com'
    content_html = '<head><link rel="shortcut icon" href="http://www.gakkit.com/static/myapp/img/matrix.png"/></head><title>警报</title><h1>您好，这是测试邮件。</h1>'
    content_text = ".您好，这是测试邮件。"
    send_email(recipient, content_text, content_html)

#B06ZXYVG4G


