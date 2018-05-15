# 费用计算，日更
'''
    和run_spiders一样，是永久进程。
    每天00:00运行一次用于统计用户所有店铺下asin的总数。
    月末的00:00计算总费用并生成账单。
    记ASIN数为A，A1表示计费周期第一天的ASIN数量。An表示最后一天的ASIN数量。T表述总天数。费用为C（cost）。系数为K。
    C = (A1 + A2 + ... + An)/T * K
    每天的费用显然是：
    C = An * K

'''

from matrix.models import *
from matrix.amazon import alert
import datetime

K = 0.008 # 费用系数

def get_cost(user):
    '''
    根据data计算当天费用
    data作为proof of work比每天记录cost的进程更加稳定
    '''
    today = datetime.datetime.today()

    ds = Data.objects.filter(
        asin__store__user=user,
        datetime__year=today.year, 
        datetime__month=today.month, 
        datetime__day=today.day,
        )

    asin_number = len(set([i.asin for i in ds])) # set 去重
    if asin_number:
        return Cost(user=user, amount=asin_number * K, date=datetime.date.today())
    else: # 如果一个asin都没有，就返回False表示没有扣费
        return 'NO ASIN'

def set_all_costs():
    '''
    为每位用户更新当天的cost对象，并更新balance和_balance的值
    根据proof of work生成，但是要注意不能重复产生同一天的费用
    '''
    print('[money.py] generating costs ...')
    for user in User.objects.all():
        cost = get_cost(user)
        if cost != 'NO ASIN': # 如果 cost 为空则跳过这个用户
            if not Cost.objects.filter(user=cost.user, date=cost.date): # 一个用户一天扣一次费 已经扣费则不保存这个cost对象
                cost.save()
                # print('[money.py]', '{} is saved.'.format(cost))

                # 上面是算钱并计入流水账，下面是直接扣钱
                print(user._balance, cost.amount)

                if user._balance - cost.amount >= 0: # 有代金券先扣除代金券
                    user._balance = user._balance - cost.amount
                else: # 代金券不足以支付
                    leftover = cost.amount - user._balance
                    user._balance = 0  # 支付后代金券归零
                    if user.balance - leftover >= 0: # 余额足以支付
                        user.balance = user.balance - leftover
                    else:
                        user.balance = 0 # 余额不足以支付，则直接归零
                user.save()
                if user.get_money() <= cost.amount: # 每个用户余额更新后判断一次，预计下次费用不足时，会发邮件提醒
                    alert.alert_to_charge(user)
                    print('[money.py] alert user to pay for the service')





