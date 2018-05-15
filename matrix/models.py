from django.db import models
from matrix.amazon import utils
from matrix.amazon import domains, listing_urls, BASE_URL
import datetime

class User(models.Model):
    '''a normal model, no authentication needed'''
    # eg: oVHM31I2B9__Z26RJue-5h9GBc0s from wechat
    # I doubled the length just in case
    openID = models.CharField(max_length=56) 
    # 记录用户是否订阅，退订后不会直接删除用户数据，因为用户可能是误删
    subscribe = models.BooleanField(default=True)
    # 内部批注，因为可能会针对某些用户做一些简单的记录
    remark = models.CharField(max_length=100, default='', blank=True) # 该项可为空
    email = models.EmailField(blank=True, default='')
    balance = models.FloatField(default=0) # 用户的余额
    _balance = models.FloatField(default=0) # 平台赠送的钱（和真钱区别对待，但在程序中无差异）
    datetime = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.openID

class Cost(models.Model):
    '''
    用户的消费记录，每天结算
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    amount = models.FloatField(blank=True)
    date = models.DateField() # 不可以用auto 因为会导致在save前的cost对象的date=None，从而不能判断是否已经存在同日期的cost
    def __str__(self):
        return '{}-{}-{}'.format(self.user.openID, self.date, self.amount)


class Store(models.Model):
    '''
    ENKEEO UK standard URL for the store:
    https://www.amazon.co.uk/s?marketplaceID=A1F83G8C2ARO7P&merchant=A25DKGOQ5SQ3PA
    只有这种页面可以直接抓next page的url，而传统的seller页面的products则很难抓到
    SUAOKI + ENKEEO US 
    https://www.amazon.com/s?marketplaceID=ATVPDKIKX0DER&me=AY5XLL1NQPR7O&merchant=AY5XLL1NQPR7O&redirect=true
    不需要去区分品牌，因为自己的店铺，不管是哪个品牌，来了差评都是需要关心的

    在保存用户的提交的store前，一定要确保含有 marketplaceID me 和 merchant 这三项，其中 me和merchant等同
    但是为了安全起见，每次访问还是带上这个参数。
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    url = models.URLField()
    me = models.CharField(max_length=50, default='')
    last_update = models.IntegerField(default=0) # 时间对象麻烦，直接保存时间戳, 0表示是新的店铺
    flag = models.BooleanField(default=False)
    def __str__(self):
        country = utils.get_country_from_url(self.url)
        merchant = self.me
        return country + '-' + merchant

class Asin(models.Model):
    '''
    Asin直接和store绑定。与用户是独立开的。
    '''
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    value = models.CharField(max_length=10)
    country = models.CharField(max_length=2)
    flag = models.BooleanField(default=False) # True表示差评已经抓取
    valid = models.BooleanField(default=True) # True表示asin正常有效， False表示下架或者封禁，以后不再爬取，但原有数据保留
    def __str__(self):
        return "{}-{}".format(self.country, self.value)
    def get_link(self):
        return listing_urls[self.country].format(self.value) # 不储存url，浪费数据库

class Data(models.Model):
    '''
    之所以叫data不叫review或者critical是因为有可能拓展
    '''
    asin = models.ForeignKey(Asin, on_delete=models.CASCADE) # 表示这个差评属于哪个asin
    number = models.IntegerField(default=0) # 差评的个数 （1、2、3星都是差评）
    datetime = models.DateTimeField(auto_now_add=True)  # 抓取的时间
    def __str__(self):
        return '{}:{}'.format(self.asin, self.number)

class Proxy(models.Model):
    '''
        2018-02-09 更新
        每次使用Proxy对象后，会加一个时间戳。然后，根据和现时时间戳的比较判断这个对象是否适用。
        筛选出适用对象后，如果成功访问页面（没有遇到robot check），
        那么无视成功率，直接加 1 分钟。
        如果失败，则看成功率，决定加的时间：

        # 注意：以下只针对当次失败的，当次成功的，只加一分钟，不管之前成功率是多少

        成功率为 80% 以上，加10分钟，
        成功率为 60% 到 80%，则加60分钟，  # 1个钟
        成功率为 40% 到 60%，则加180分钟， # 3个钟
        成功率为 40% 以下，则加1440分钟，   # 一天
        成功率为 20% 以下，直接设置为 valid=False 不再使用 （我也不会随意删除，因为未来可以看报废率）
         stamp += 600。每次失败就是这样成吨增加 stamp。
        到时候淘汰不看stamp，而是看成功率。

        此外，由于失败率升高会导致等待时间加长，可以自动规避被亚马逊疯狂ban掉的危险。
        失败率高到一定程度会导致爬虫近乎停滞，而不是疯狗一样冲击服务器。
    '''
    url = models.CharField(max_length=23, default='') # 核心，不适用URL对象，因为我不想去挨个处理掉http://这个协议标示
    use = models.IntegerField(default=0) # 使用次数
    fail = models.IntegerField(default=0) # 失败次数 
    rate = models.FloatField(default=1) # 成功率，反映了代理的健康程度
    country = models.CharField(max_length=2, default='') #  国别
    stamp = models.IntegerField(default=0) # 每次
    valid = models.NullBooleanField(default=None) # None 表示未经过检查，True 经过检查有效， False 检查后无效/失败率过高
    def __str__(self): 
        return self.url
    def set_rate(self): # 成功率
        if self.use > 5: # 至少要用了5次以上，否则第一次用挂了就是0%成功率就浪费一个ip
            self.rate = (self.use - self.fail)/self.use
    def set_stamp(self): # 根据成功率调节等待时间，注意，这个只处理当次失败的
        if self.rate > 0.8:
            self.stamp += 600
        elif self.rate > 0.6:
            self.stamp += 3600
        elif self.rate > 0.4:
            self.stamp += 10800
        elif self.rate > 0.1:
            self.stamp += 86400
        else:
            self.valid = False
    class Meta:
        ordering = ['use'] # 默认升序


class Email(models.Model):
    '''
    用于记录每次发信的内容，作为备份
    '''
    address = models.EmailField()
    datetime = models.DateTimeField(auto_now_add=True)
    content_html = models.TextField()


















