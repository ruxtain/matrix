from django.contrib import admin
from matrix.models import *


class UserAdmin(admin.ModelAdmin):    
    list_display = ('openID', 'datetime','email', '__str__')

class CostAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount')

class StoreAdmin(admin.ModelAdmin):
    list_display = ('url', 'user', 'last_update')

class AsinAdmin(admin.ModelAdmin):
    list_display = ('value', 'country', 'flag')

class DataAdmin(admin.ModelAdmin):
    def getCountry(obj): # 从critical/data 引出 url
        return obj.asin.country
    getCountry.short_description = 'Country'    
    list_display = ('asin', getCountry, 'number', 'datetime')

class ProxyAdmin(admin.ModelAdmin):
    list_display = ('url', 'country', 'use', 'fail', 'rate', 'stamp', 'valid')

admin.site.register(User, UserAdmin)
admin.site.register(Cost, CostAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Asin, AsinAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(Proxy, ProxyAdmin)