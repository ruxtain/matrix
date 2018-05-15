from django.db import models

class Description(models.Model):
    '''保存用户提交的描述，可以看看都是些什么人在用我的站'''
    ip = models.CharField(max_length=20)
    content = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content[:100]

class Feedback(models.Model):
    ip = models.CharField(max_length=20)
    url = models.URLField(default="")
    content = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content[:100]

class Keyword(models.Model):
    ip = models.CharField(max_length=20)
    content = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content[:100]
        