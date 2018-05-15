from django.contrib import admin
from .models import *

class DescriptionAdmin(admin.ModelAdmin):
    list_display = ('ip', 'datetime', 'content')

class KeywordAdmin(admin.ModelAdmin):
    list_display = ('ip', 'datetime', 'content')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('ip', 'datetime', 'url', 'content')

admin.site.register(Description, DescriptionAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Feedback, FeedbackAdmin)