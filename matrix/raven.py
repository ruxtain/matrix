# 特别提示 https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140543
# 这里的《被动回复用户消息》的示例有问题，一定要去掉 <ToUserName>< ![CDATA[{}] ]></ToUserName> 中多余的空格！！！！

import xml.etree.cElementTree as ET # 理论上比BeautifulSoup快, cElementTree 比 ElementTree 更快
import time
import re
from matrix.models import *
from matrix import print_log, get_log_path
from matrix.amazon import utils, asins_spider

R_WELCOME = '感谢您关注「矩阵数据」公众号(内测版)。\n\n立即享受全自动的差评监控！\n\n请点击「使用方法」进行配置。'
R_UNKNOWN = '不好意思，不明白「{}」的含义，请点击下方「使用方法」了解更多。'
R_SAVE_EMAIL = '您提交的邮箱已经保存。回复「邮箱」即可查看邮箱地址。请将 info@service.gakkit.com 设置到白名单，以免接收不到警报邮件。'
R_SAVE_ASIN = '您提交的 ASIN {}-{} 已经保存。'
R_ASIN_EXIST = '您提交的 ASIN {}-{} 已经已经存在，无需重复提交哦。'
R_NO_STORE = '不好意思，请您在提交店铺之后再添加断货的 ASIN。'
R_QUESTION = '您的问题我们已经收到，请耐心等待客服回复（最迟48小时内）。'
R_HELP = '''您可以回复以下词语：
★ 回复「店铺」可以查看店铺设置情况。
★ 回复「邮箱」可以查看设置的邮箱，重新回复一个邮箱地址会覆盖掉原先的。
​★ 回复「帮助」查看本信息。
更多帮助信息请点击下方「使用方法」、「答疑解惑」。
'''

# 条件判断区块

def is_listing_url(url):
    '''判断是否是listing的链接，如果则保存单个的asin对象'''
    try:
        country = utils.get_country_from_url(url)
        value = re.findall(r'/dp/([A-Z\d]{9,11})', url)[0]
        return True
    except IndexError:
        return False

# 初步判断是否是店铺链接
def is_store_url(url):
    if url.startswith('https'):
        if 'marketplaceID' in url:
            if 'merchant' in url:
                print_log('[raven.py] 捕获到了店铺。')
                return True

# 判断是否是邮箱
def is_email(c):
    if re.findall(r"^[\da-zA-Z]{1}[\-_\da-zA-Z]{3,17}@[a-zA-Z\d]+\.[a-zA-Z\d]+", c):
        return True

# 接下来是用户输入分析
def get_msg_type(request_msg):
    '''
    在一切处理开始之前首先要明确消息是文本还是事件，未来也可能是其他类型，如图片
    '''
    MsgType = re.findall(r'<MsgType><!\[CDATA\[(\w+)\]\]></MsgType>', request_msg)[0]
    return MsgType

def make_dict(request_msg):
    '''convert request_msg(xml) to dict'''
    request_msg_dict = {}
    xml = ET.fromstring(request_msg)
    for i in xml:
        request_msg_dict[i.tag] = i.text
    return request_msg_dict 

class TextMessage():
    '''
    将xml转成python对象，增强代码的可读性
    一种消息、事件类型建一个类
    '''
    def get_user(self):
        try:
            return User.objects.get(openID=self.FromUserName)
        except: # DoNotExist
            user = User(openID=self.FromUserName, subscribe=True) # 新建用户
            user.save()
            return user

    def __init__(self, request_msg):
        self.dict = make_dict(request_msg) # 预处理
        self.ToUserName = self.dict['ToUserName']
        self.FromUserName = self.dict['FromUserName']
        self.CreateTime = self.dict['CreateTime']
        self.MsgType = self.dict['MsgType']
        self.Content = self.dict['Content']
        self.MsgId = self.dict['MsgId']
        self.user = self.get_user()

    def __str__(self):
        return self.MsgId

    def reply(self, content): # 回复消息
        response_msg = '''<xml>\
                        <ToUserName><![CDATA[{}]]></ToUserName>\
                        <FromUserName><![CDATA[{}]]></FromUserName>\
                        <CreateTime>{}</CreateTime><MsgType>\
                        <![CDATA[text]]></MsgType>\
                        <Content><![CDATA[{}]]></Content>\
                        </xml>'''
        response_msg = response_msg.format(self.FromUserName, self.ToUserName, int(time.time()), content)
        return response_msg.encode('utf-8')

    def get_first_store(self): # 获取用户首个店铺
        try:
            return self.user.store_set.first()
        except:
            return False

    # 警告！以下数据库操作都需要先进行条件判断

    def is_admin(self):
        if self.user.pk == 1:
            return True 
        else:
            return False

    def save_asin(self): # 保存单个的asin到第一个店铺下，用于处理断货产品
        url = self.Content
        store = self.get_first_store()
        country = utils.get_country_from_url(url)
        value = re.findall(r'/dp/([A-Z\d]{9,11})', url)[0]
        if store: # 有至少一家店铺
            if not Asin.objects.filter(country=country, value=value, store=store):
                asin = Asin(country=country, value=value, store=store)
                asin.save() # 直接保存到第一个店铺下，即使不属于这个店铺，也没有影响
                return self.reply(R_SAVE_ASIN.format(country, value))
            else:
                return self.reply(R_ASIN_EXIST.format(country, value))
        else:
            return self.reply(R_NO_STORE)

    def save_email(self): # 为用户保存邮箱
        email = self.Content
        print_log('[raven.py] email 的样子：{}'.format(email))
        self.user.email = email
        self.user.save()
        print_log('[raven.py] email 已经储存。')
        return self.reply('您的邮箱地址 {} 已经储存。请确保正确，如欲更换，只需重新回复一次正确邮箱。'.format(email))

    def query_email(self):
        email = self.user.email
        if email:
            return self.reply('您的邮箱地址是：\n' + email)
        else:
            return self.reply('您还没有设置邮箱，请回复您的邮箱进行设置。')

    def save_store(self): # 保存店铺链接
        url = self.Content
        print_log('[raven.py] URL 的样子：{}'.format(url))
        me = utils.get_me(url)
        print_log('[raven.py] me 的样子：{}'.format(me))
        if not Store.objects.filter(user=self.user, url=url):  # 重复提交的不保存
            store = Store(user=self.user, url=url, me=me, last_update=0) # 此时的store.last_update=0
            store.save()
            print_log('[raven.py] 店铺已经保存。')
            return self.reply('您提交的店铺已经保存。回复「店铺」即可查看已经保存的全部店铺。回复「邮箱」可以进一步查看邮箱设置。')

    def query_store(self): # 根据用户请求查询店铺
        text = '您现有的店铺有：\n'
        if self.user.store_set.first():
            for store in self.user.store_set.all():
                text += str(store) + '\n'
        else:
            text = '您还没有设置店铺，请回复您的 Storefront 链接进行设置。'
        return self.reply(text)

    def query_balance(self): # 查询余额，不区分代金券和现金，统统告诉用户这是现金
        balance = self.user.balance + self.user._balance
        text = '您的余额是：\n{:.2f} 元'.format(balance)
        return self.reply(text)

    def query_log(self):
        try:
            with open(get_log_path(), 'r', encoding='utf-8') as f:
                text = '最后8行日志：\n'
                for line in f.readlines()[-8:]:
                    text += line
            return self.reply(text)
        except:
            return self.reply('今日尚未生成任何日志。')

    def query_proxy(self): # 查询剩余的可用proxy
        vps = Proxy.objects.filter(valid=True).count()
        aps = Proxy.objects.all().count()
        percent = '{:.2f}%'.format(vps/aps*100)
        text = '您的 proxy 总数：{}，可用：{}，占比：{}。'.format(aps, vps, percent)
        return self.reply(text)

    def query_user(self): # 查看注册用户数和订阅用户数
        all_cus = User.objects.all().count()
        all_sub = User.objects.filter(subscribe=True).count()
        text = '总用户数：{}，订阅用户数：{}。'.format(all_cus, all_sub)
        return self.reply(text)

    def query_all_store(self): # 查看总的店铺数
        all_store = Store.objects.all().count()
        text = '总的店铺数：{}。'.format(all_store)
        return self.reply(text)

    def query_memory(self):
        from matrix import control
        text = control.get_memory()
        return self.reply(text)

    def reply_test(self):
        response_msg = '''<xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>1</ArticleCount><Articles>
            <item>
                <Title><![CDATA[矩阵·使用方法]]></Title>
                <Description>< ![CDATA[请您在使用前仔细阅读本文，以确保您接下来的正确使用。]]></Description>
                <PicUrl><![CDATA[https://mmbiz.qpic.cn/mmbiz_jpg/ou02YejFLlVaiaF2c41686dm5zRzibPHOI4Mbvl0G7ewYyLNAWqJSe7wx6AZeMGQiaic7gyJostagn0H0AAa7Sjy6Q/0?wx_fmt=jpeg]]></PicUrl>
                <Url><![CDATA[http://mp.weixin.qq.com/s?__biz=MzU2MDQwMzc5Ng==&mid=100000016&idx=1&sn=cf9f7492330cb74821e1ecbad318d8b4&chksm=7c09c52b4b7e4c3d7026ed4fc9c5a613961e91c062a690d274dc7af6bba0a56d55d5813081e6&scene=18#rd]]></Url>
            </item>
        </Articles>
        </xml>'''        
        response_msg = response_msg.format(self.FromUserName, self.ToUserName, int(time.time()))
        print(response_msg)
        return response_msg.encode('utf-8')

class EventMessage():
    '''
    典型事件示例
    <xml><ToUserName><![CDATA[gh_bda3d54b63c5]]></ToUserName>
    <FromUserName><![CDATA[oVHM31I2B9__Z26RJue-5h9GBc0s]]></FromUserName>
    <CreateTime>1517670932</CreateTime>
    <MsgType><![CDATA[event]]></MsgType>
    <Event><![CDATA[subscribe]]></Event>
    <EventKey><![CDATA[]]></EventKey>
    </xml>
    '''
    def get_user(self):
        try:
            return User.objects.get(openID=self.FromUserName)
        except: # DoNotExist
            user = User(openID=self.FromUserName, subscribe=True) # 新建用户
            user.save()
            return user

    def __init__(self, request_msg):
        self.dict = make_dict(request_msg) # 预处理
        self.ToUserName = self.dict['ToUserName']
        self.FromUserName = self.dict['FromUserName']
        self.CreateTime = self.dict['CreateTime']
        self.MsgType = self.dict['MsgType']
        self.Event = self.dict['Event']
        self.EventKey = self.dict['EventKey']
        self.user = self.get_user()  

    def reply(self, content): # 回复消息
        response_msg = '''<xml>\
                        <ToUserName><![CDATA[{}]]></ToUserName>\
                        <FromUserName><![CDATA[{}]]></FromUserName>\
                        <CreateTime>{}</CreateTime><MsgType>\
                        <![CDATA[text]]></MsgType>\
                        <Content><![CDATA[{}]]></Content>\
                        </xml>'''
        response_msg = response_msg.format(self.FromUserName, self.ToUserName, int(time.time()), content)
        return response_msg.encode('utf-8')

    def send_article(self): # 回复一篇指定的文章
        response_msg = '''
        <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>1</ArticleCount><Articles>
            <item>
                <Title><![CDATA[请您先读一下这个说明 (ง •̀_•́)ง]]></Title>
                <Description>< ![CDATA[请您在使用前仔细阅读本文，以确保您接下来的正确使用。]]></Description>
                <PicUrl><![CDATA[https://mmbiz.qpic.cn/mmbiz_jpg/ou02YejFLlVaiaF2c41686dm5zRzibPHOI4Mbvl0G7ewYyLNAWqJSe7wx6AZeMGQiaic7gyJostagn0H0AAa7Sjy6Q/0?wx_fmt=jpeg]]></PicUrl>
                <Url><![CDATA[http://mp.weixin.qq.com/s?__biz=MzU2MDQwMzc5Ng==&mid=100000016&idx=1&sn=cf9f7492330cb74821e1ecbad318d8b4&chksm=7c09c52b4b7e4c3d7026ed4fc9c5a613961e91c062a690d274dc7af6bba0a56d55d5813081e6&scene=18#rd]]></Url>
            </item>
        </Articles>
        </xml>''' 
        response_msg = response_msg.format(self.FromUserName, self.ToUserName, int(time.time()))
        return response_msg.encode('utf-8')

    def subscribe(self): # 初始化的时候已经保存用户，所以这里只针对推定后重新订阅的用户
        self.user.subscribe = True
        self.user.save()
        # return self.reply(R_WELCOME)
        return self.send_article()

    def unsubscribe(self):
        self.user.subscribe = False
        self.user.save()
        return ''


class ImageMessage():
    def get_user(self):
        try:
            return User.objects.get(openID=self.FromUserName)
        except: # DoNotExist
            user = User(openID=self.FromUserName, subscribe=True) # 新建用户
            user.save()
            return user

    def reply(self, content): # 回复消息
        response_msg = '''<xml>\
                        <ToUserName><![CDATA[{}]]></ToUserName>\
                        <FromUserName><![CDATA[{}]]></FromUserName>\
                        <CreateTime>{}</CreateTime><MsgType>\
                        <![CDATA[text]]></MsgType>\
                        <Content><![CDATA[{}]]></Content>\
                        </xml>'''
        response_msg = response_msg.format(self.FromUserName, self.ToUserName, int(time.time()), content)
        return response_msg.encode('utf-8')            

    def __init__(self, request_msg):
        self.dict = make_dict(request_msg) # 预处理
        self.ToUserName = self.dict['ToUserName']
        self.FromUserName = self.dict['FromUserName']
        self.CreateTime = self.dict['CreateTime']
        self.MsgType = self.dict['MsgType']
        self.PicUrl = self.dict['PicUrl']
        self.MediaId = self.dict['MediaId']
        self.MsgId = self.dict['MsgId']
        self.user = self.get_user()

    def save_msg(self):
        print_log(str(self.dict))
        return self.reply('您提交的图片我们已收到。我们会尽快进行人工审核。')

# 母函数
def analyse(request_msg):
    '''
    request_msg = """
        <xml><ToUserName><![CDATA[gh_bda3d54b63c5]]></ToUserName>
        <FromUserName><![CDATA[oVHM31I2B9__Z26RJue-5h9GBc0s]]></FromUserName>
        <CreateTime>1515927571</CreateTime>
        <MsgType><![CDATA[event]]></MsgType>
        <Event><![CDATA[unsubscribe]]></Event>
        <EventKey><![CDATA[]]></EventKey></xml>
    """
    处理用户的xml输入，然后返回对应的xml。
    具体的格式参考： https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140543

    request_msg_dict 形如：
    {
        'ToUserName': 'gh_bda3d54b63c5', '
        FromUserName': 'oVHM31I2B9__Z26RJue-5h9GBc0s', 
        'CreateTime': '1515828808', 
        'MsgType': 'text', 
        'Content': '捕获request.body', 
        'MsgId': '6510435157128279881'
    }
    '''
    msg_type = get_msg_type(request_msg)
    if msg_type == 'text':
        text_message = TextMessage(request_msg)
        content = text_message.Content
        if is_store_url(content):
            return text_message.save_store()
        elif is_email(content):
            return text_message.save_email()
        elif is_listing_url(content):
            return text_message.save_asin()
        elif content == '帮助':
            return text_message.reply(R_HELP)
        elif content == '余额':
            # return text_message.query_balance()
            return text_message.reply('完全免费，无需查询余额。')
        elif content == '店铺':
            return text_message.query_store()
        elif content == '邮箱':
            return text_message.query_email()
        elif content.startswith('问题'):
            return text_message.reply(R_QUESTION)

        # 以下只能管理员调用        
        elif text_message.is_admin():
            if content == '日志':
                return text_message.query_log()
            elif content == '代理':
                return text_message.query_proxy()
            elif content == '用户':
                return text_message.query_user()
            elif content == '内存':
                return text_message.query_memory()                
            elif content == '1': # 来简洁点
                return text_message.query_all_store()
            elif content == '0': # 专用于测试
                return text_message.reply_test()
            else:
                return text_message.reply(R_UNKNOWN.format(content)) # admin 尽量和用户看到的一致    
        else:
            return text_message.reply(R_UNKNOWN.format(content))

    elif msg_type == 'image':
        image_message = ImageMessage(request_msg)
        return image_message.save_msg()

    elif msg_type == 'event':
        event_message = EventMessage(request_msg)
        event = event_message.Event
        if event == 'subscribe':
            return event_message.subscribe()
        elif event == 'unsubscribe':
            return event_message.unsubscribe()
    else:
        return ''



















